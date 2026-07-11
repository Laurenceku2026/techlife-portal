"""Signed portal tokens for child app SSO."""
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import jwt
import streamlit as st

TOKEN_TTL_SECONDS = 8 * 3600


def get_jwt_secret() -> str:
    secret = st.secrets.get("JWT_SECRET_KEY")
    if not secret:
        st.error("缺少配置 JWT_SECRET_KEY，请在 Streamlit secrets 中添加。")
        st.stop()
    return secret


def _jwt_secret_or_none() -> Optional[str]:
    return st.secrets.get("JWT_SECRET_KEY")


def create_portal_token(
    user_id: str,
    email: str,
    lang: str,
    subscription_tier: str,
    trials_remaining: int,
    *,
    organization_id: Optional[str] = None,
    organization_name: Optional[str] = None,
    org_role: Optional[str] = None,
) -> str:
    now = int(time.time())
    payload: Dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "lang": lang,
        "tier": subscription_tier,
        "trials_left": trials_remaining,
        "iat": now,
        "exp": now + TOKEN_TTL_SECONDS,
    }
    if organization_id:
        payload["organization_id"] = organization_id
        payload["organization_name"] = organization_name or ""
        payload["org_role"] = org_role or "member"
    return jwt.encode(payload, get_jwt_secret(), algorithm="HS256")


def verify_portal_token(token: str) -> Optional[Dict[str, Any]]:
    secret = _jwt_secret_or_none()
    if not secret:
        return None
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def build_app_launch_url(
    base_url: str,
    user_id: str,
    email: str,
    lang: str,
    subscription_tier: str,
    trials_remaining: int,
    *,
    organization_id: Optional[str] = None,
    organization_name: Optional[str] = None,
    org_role: Optional[str] = None,
    include_legacy_params: bool = True,
) -> str:
    """Build child-app URL with signed token (and optional legacy params for rollout)."""
    token = create_portal_token(
        user_id,
        email,
        lang,
        subscription_tier,
        trials_remaining,
        organization_id=organization_id,
        organization_name=organization_name,
        org_role=org_role,
    )
    params = {"token": token, "lang": lang}
    if include_legacy_params:
        params.update(
            {
                "user_id": user_id,
                "email": email,
                "trials_left": str(trials_remaining),
            }
        )
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{urlencode(params)}"
