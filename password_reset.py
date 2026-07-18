"""
忘记密码：JWT 重置链接 + Gmail SMTP 发信 + Supabase Admin 更新密码。
流程对齐 Sigma_bazi（email_smtp + token 链接），鉴权侧适配本门户的 Supabase Auth。
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.parse import quote

import jwt

from email_smtp import build_password_reset_email, send_email, smtp_configured
from enterprise_utils import find_user_id_by_email, set_auth_user_password

RESET_TOKEN_TTL_SECONDS = 3600
RESET_COOLDOWN_SECONDS = 120
JWT_PURPOSE = "pwd_reset"


def create_password_reset_token(email: str, secret: str, *, ttl_seconds: int = RESET_TOKEN_TTL_SECONDS) -> str:
    email = (email or "").strip().lower()
    now = int(time.time())
    payload = {
        "purpose": JWT_PURPOSE,
        "email": email,
        "iat": now,
        "exp": now + max(300, int(ttl_seconds)),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_password_reset_token(token: str, secret: str) -> Tuple[Optional[str], str]:
    """返回 (email, error_code)。成功时 error_code 为空。"""
    token = (token or "").strip()
    if not token or not secret:
        return None, "token_invalid"
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, "token_expired"
    except jwt.PyJWTError:
        return None, "token_invalid"
    if payload.get("purpose") != JWT_PURPOSE:
        return None, "token_invalid"
    email = (payload.get("email") or "").strip().lower()
    if not email or "@" not in email:
        return None, "token_invalid"
    return email, ""


def check_cooldown(email: str, last_sent_map: Dict[str, float], *, cooldown_seconds: int = RESET_COOLDOWN_SECONDS) -> bool:
    """True = 仍在冷却中。"""
    email = (email or "").strip().lower()
    last = last_sent_map.get(email)
    if last is None:
        return False
    return (time.time() - float(last)) < cooldown_seconds


def mark_sent(email: str, last_sent_map: Dict[str, float]) -> None:
    last_sent_map[(email or "").strip().lower()] = time.time()


def send_password_reset_email(
    *,
    email: str,
    lang: str,
    jwt_secret: str,
    supabase_url: str,
    service_headers: Dict[str, str],
    smtp: Dict[str, Any],
    app_base_url: str,
    last_sent_map: Dict[str, float],
    app_name: str = "TechLife Suite",
) -> Tuple[str, str]:
    """
    发送重置邮件。
    返回 (status, detail)：
      - ok: 已发送（或未知邮箱时伪装成功）
      - cooldown: 冷却中
      - smtp_missing / no_base_url / fail: 错误
    """
    email = (email or "").strip().lower()
    if not email or "@" not in email:
        return "fail", "invalid_email"
    if not smtp_configured(
        host=str(smtp.get("host") or ""),
        user=str(smtp.get("user") or ""),
        password=str(smtp.get("password") or ""),
    ):
        return "smtp_missing", ""
    if check_cooldown(email, last_sent_map):
        return "cooldown", ""

    user_id = find_user_id_by_email(supabase_url, service_headers, email)
    # 未知邮箱：不发信，仍返回 ok，避免枚举账号
    if not user_id:
        mark_sent(email, last_sent_map)
        return "ok", "unknown_email"

    base = (app_base_url or "").rstrip("/")
    if not base:
        return "no_base_url", ""

    token = create_password_reset_token(email, jwt_secret)
    reset_url = f"{base}/?pwd_reset=1&email={quote(email, safe='')}&token={quote(token, safe='')}"
    subject, text_body, html_body = build_password_reset_email(
        reset_url=reset_url,
        lang="en" if lang == "en" else "zh",
        app_name=app_name if lang != "en" else "TechLife Suite",
    )
    ok, err = send_email(
        host=str(smtp.get("host") or ""),
        port=int(smtp.get("port") or 587),
        user=str(smtp.get("user") or ""),
        password=str(smtp.get("password") or ""),
        mail_from=str(smtp.get("mail_from") or smtp.get("user") or ""),
        to_addr=email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        use_tls=bool(smtp.get("use_tls", True)),
    )
    if not ok:
        return "fail", err
    mark_sent(email, last_sent_map)
    return "ok", ""


def apply_password_reset_with_token(
    *,
    email: str,
    token: str,
    new_password: str,
    jwt_secret: str,
    supabase_url: str,
    service_headers: Dict[str, str],
) -> Tuple[bool, str]:
    email_norm = (email or "").strip().lower()
    pwd = (new_password or "").strip()
    if not email_norm or not token or len(pwd) < 6:
        return False, "invalid_input"

    token_email, err = verify_password_reset_token(token, jwt_secret)
    if err:
        return False, err
    if token_email != email_norm:
        return False, "token_invalid"

    user_id = find_user_id_by_email(supabase_url, service_headers, email_norm)
    if not user_id:
        return False, "account_not_found"

    return set_auth_user_password(supabase_url, service_headers, user_id, pwd)


def secrets_getenv(get_secret: Callable[[str], str]) -> Callable[[str], Optional[str]]:
    """把门户的 _get_secret 适配成 email_smtp.env_smtp_settings 可用的 getenv。"""

    def _getenv(key: str, default: Optional[str] = None) -> Optional[str]:
        value = get_secret(key)
        return value if value else default

    return _getenv
