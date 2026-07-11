"""Enterprise organizations, members, and tenant knowledge base helpers."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

KNOWLEDGE_CATEGORIES = ["光学", "机械", "材料", "热学", "电气", "控制"]


def _parse_auth_users(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, dict):
        users = data.get("users")
        return users if isinstance(users, list) else []
    if isinstance(data, list):
        return data
    return []


def _table_url(supabase_url: str, table: str, query: str = "") -> str:
    base = f"{supabase_url}/rest/v1/{table}"
    return f"{base}?{query}" if query else base


def supabase_select(
    supabase_url: str,
    headers: Dict[str, str],
    table: str,
    *,
    select: str = "*",
    filters: Optional[Dict[str, str]] = None,
    order: Optional[str] = None,
) -> List[Dict[str, Any]]:
    parts = [f"select={quote(select, safe='*,()')}"]
    if filters:
        for key, value in filters.items():
            if value is None:
                parts.append(f"{key}=is.null")
            else:
                parts.append(f"{key}=eq.{quote(str(value), safe='')}")
    if order:
        parts.append(f"order={order}")
    url = _table_url(supabase_url, table, "&".join(parts))
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []


def supabase_insert(
    supabase_url: str,
    headers: Dict[str, str],
    table: str,
    data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    insert_headers = {**headers, "Prefer": "return=representation"}
    try:
        response = requests.post(
            _table_url(supabase_url, table),
            headers=insert_headers,
            json=data,
            timeout=15,
        )
        if response.status_code in (200, 201):
            try:
                rows = response.json()
                if isinstance(rows, list) and rows:
                    return rows[0]
            except ValueError:
                pass
            return data
    except Exception:
        pass
    return None


def supabase_update(
    supabase_url: str,
    headers: Dict[str, str],
    table: str,
    row_id: str,
    data: Dict[str, Any],
    *,
    id_field: str = "id",
) -> tuple[bool, str]:
    url = _table_url(supabase_url, table, f"{id_field}=eq.{row_id}")
    try:
        response = requests.patch(url, headers=headers, json=data, timeout=15)
        if response.status_code in (200, 204):
            return True, ""
        return False, response.text or f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def supabase_delete(
    supabase_url: str,
    headers: Dict[str, str],
    table: str,
    query: str,
) -> bool:
    url = _table_url(supabase_url, table, query)
    try:
        response = requests.delete(url, headers=headers, timeout=15)
        return response.status_code in (200, 204)
    except Exception:
        return False


def get_full_profile(
    supabase_url: str,
    headers: Dict[str, str],
    user_id: str,
) -> Dict[str, Any]:
    default = {
        "id": user_id,
        "email": "",
        "subscription_tier": "free",
        "free_trials_remaining": 30,
        "subscription_expires_at": None,
        "organization_id": None,
        "org_role": None,
        "organization_name": None,
        "max_seats": None,
    }
    if not user_id or user_id == "admin":
        return default

    rows = supabase_select(
        supabase_url,
        headers,
        "profiles",
        select="id,email,subscription_tier,free_trials_remaining,subscription_expires_at,organization_id,org_role",
        filters={"id": user_id},
    )
    if not rows:
        rows = supabase_select(
            supabase_url,
            headers,
            "profiles",
            select="id,email,subscription_tier,free_trials_remaining,subscription_expires_at",
            filters={"id": user_id},
        )
    if not rows:
        return default

    profile = {**default, **rows[0]}
    org_id = profile.get("organization_id")
    if org_id:
        org_rows = supabase_select(
            supabase_url,
            headers,
            "organizations",
            select="id,name,max_seats,is_active,contract_expires_at",
            filters={"id": org_id},
        )
        if org_rows:
            profile["organization_name"] = org_rows[0].get("name")
            profile["max_seats"] = org_rows[0].get("max_seats")
            profile["org_is_active"] = org_rows[0].get("is_active", True)
    return profile


def is_enterprise_user(profile: Dict[str, Any]) -> bool:
    return bool(profile.get("organization_id"))


def is_org_admin(profile: Dict[str, Any]) -> bool:
    return is_enterprise_user(profile) and profile.get("org_role") == "admin"


def list_organizations(supabase_url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    return supabase_select(
        supabase_url,
        headers,
        "organizations",
        order="name.asc",
    )


def create_organization(
    supabase_url: str,
    headers: Dict[str, str],
    name: str,
    max_seats: int,
) -> Optional[Dict[str, Any]]:
    return supabase_insert(
        supabase_url,
        headers,
        "organizations",
        {
            "name": name.strip(),
            "max_seats": max_seats,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        },
    )


def update_organization(
    supabase_url: str,
    headers: Dict[str, str],
    org_id: str,
    data: Dict[str, Any],
) -> bool:
    ok, _ = supabase_update(supabase_url, headers, "organizations", org_id, data)
    return ok


def delete_organization(
    supabase_url: str,
    headers: Dict[str, str],
    org_id: str,
) -> tuple[bool, str]:
    try:
        if not org_id:
            return False, "missing_org_id"

        members = list_org_members(supabase_url, headers, org_id)
        for member in members:
            member_id = member.get("id")
            if member_id:
                ok, detail = supabase_update(
                    supabase_url,
                    headers,
                    "profiles",
                    member_id,
                    {"organization_id": None, "org_role": None},
                )
                if not ok:
                    return False, detail or f"unbind_failed:{member_id}"

        supabase_delete(
            supabase_url,
            headers,
            "knowledge_base",
            f"organization_id=eq.{quote(str(org_id), safe='')}&scope=eq.tenant",
        )

        if not supabase_delete(
            supabase_url,
            headers,
            "organizations",
            f"id=eq.{quote(str(org_id), safe='')}",
        ):
            return False, "delete_failed"
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def list_org_members(
    supabase_url: str,
    headers: Dict[str, str],
    organization_id: str,
) -> List[Dict[str, Any]]:
    return supabase_select(
        supabase_url,
        headers,
        "profiles",
        select="id,email,org_role,subscription_tier",
        filters={"organization_id": organization_id},
        order="email.asc",
    )


def count_org_members(
    supabase_url: str,
    headers: Dict[str, str],
    organization_id: str,
) -> int:
    return len(list_org_members(supabase_url, headers, organization_id))


def create_auth_user(
    supabase_url: str,
    service_headers: Dict[str, str],
    email: str,
    password: str,
) -> Optional[str]:
    """Create Supabase Auth user; returns user id or None."""
    try:
        response = requests.post(
            f"{supabase_url}/auth/v1/admin/users",
            headers=service_headers,
            json={"email": email, "password": password, "email_confirm": True},
            timeout=15,
        )
        if response.status_code in (200, 201):
            try:
                body = response.json()
                if isinstance(body, dict):
                    return body.get("id")
            except ValueError:
                pass
        if response.status_code == 422 and "already" in response.text.lower():
            return find_auth_user_id_by_email(supabase_url, service_headers, email)
    except Exception:
        pass
    return None


def ensure_profile(
    supabase_url: str,
    headers: Dict[str, str],
    user_id: str,
    email: str,
    data: Dict[str, Any],
) -> tuple[bool, str]:
    rows = supabase_select(
        supabase_url,
        headers,
        "profiles",
        filters={"id": user_id},
    )
    payload = {"email": email, **data}
    if rows:
        return supabase_update(supabase_url, headers, "profiles", user_id, payload)
    payload["id"] = user_id
    payload.setdefault("free_trials_remaining", 0)
    payload.setdefault("subscription_tier", "pro")
    result = supabase_insert(supabase_url, headers, "profiles", payload)
    if result is not None:
        return True, ""
    return False, "insert_failed"


def find_auth_user_id_by_email(
    supabase_url: str,
    service_headers: Dict[str, str],
    email: str,
) -> Optional[str]:
    normalized = (email or "").strip().lower()
    if not normalized:
        return None

    page = 1
    per_page = 200
    while page <= 20:
        try:
            response = requests.get(
                f"{supabase_url}/auth/v1/admin/users",
                headers=service_headers,
                params={"page": page, "per_page": per_page},
                timeout=15,
            )
            if response.status_code != 200:
                break
            users = _parse_auth_users(response.json())
            if not users:
                break
            for user in users:
                if (user.get("email") or "").strip().lower() == normalized:
                    return user.get("id")
            if len(users) < per_page:
                break
            page += 1
        except Exception:
            break
    return None


def find_user_id_by_email(
    supabase_url: str,
    service_headers: Dict[str, str],
    email: str,
) -> Optional[str]:
    user_id = find_auth_user_id_by_email(supabase_url, service_headers, email)
    if user_id:
        return user_id

    rows = supabase_select(
        supabase_url,
        service_headers,
        "profiles",
        select="id,email",
        filters={"email": (email or "").strip()},
    )
    if rows:
        return rows[0].get("id")

    return None


def set_auth_user_password(
    supabase_url: str,
    service_headers: Dict[str, str],
    user_id: str,
    password: str,
) -> tuple[bool, str]:
    try:
        response = requests.put(
            f"{supabase_url}/auth/v1/admin/users/{user_id}",
            headers=service_headers,
            json={"password": password, "email_confirm": True},
            timeout=15,
        )
        if response.status_code in (200, 201):
            return True, ""
        return False, response.text or f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def verify_login_credentials(
    supabase_url: str,
    anon_key: str,
    email: str,
    password: str,
) -> tuple[bool, str]:
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            f"{supabase_url}/auth/v1/token?grant_type=password",
            headers=headers,
            json={"email": (email or "").strip(), "password": password},
            timeout=15,
        )
        if response.status_code == 200:
            return True, ""
        try:
            body = response.json()
            return False, (
                body.get("error_description")
                or body.get("msg")
                or body.get("message")
                or response.text
            )
        except ValueError:
            return False, response.text or f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def assign_or_provision_org_user(
    supabase_url: str,
    service_headers: Dict[str, str],
    email: str,
    password: str,
    organization_id: str,
    org_role: str,
    *,
    max_seats: int = 500,
) -> tuple[bool, str]:
    """Create or locate auth user, always set password, then bind to organization."""
    normalized_email = (email or "").strip()
    if not normalized_email:
        return False, "email_required"
    if not password or len(password) < 6:
        return False, "password_required"

    user_id = find_auth_user_id_by_email(supabase_url, service_headers, normalized_email)
    if not user_id:
        if count_org_members(supabase_url, service_headers, organization_id) >= max_seats:
            return False, "seat_limit"
        user_id = create_auth_user(supabase_url, service_headers, normalized_email, password)
        if not user_id:
            return False, "auth_failed"

    pwd_ok, pwd_detail = set_auth_user_password(
        supabase_url, service_headers, user_id, password
    )
    if not pwd_ok:
        return False, pwd_detail or "password_reset_failed"

    ok, detail = ensure_profile(
        supabase_url,
        service_headers,
        user_id,
        normalized_email,
        {
            "organization_id": organization_id,
            "org_role": org_role,
            "subscription_tier": "pro",
            "free_trials_remaining": 0,
        },
    )
    return (ok, "ok" if ok else (detail or "profile_failed"))


def assign_email_to_org(
    supabase_url: str,
    service_headers: Dict[str, str],
    email: str,
    organization_id: str,
    org_role: str,
) -> tuple[bool, str]:
    user_id = find_user_id_by_email(supabase_url, service_headers, email)
    if not user_id:
        return False, "not_found"

    ok, detail = ensure_profile(
        supabase_url,
        service_headers,
        user_id,
        email.strip(),
        {
            "organization_id": organization_id,
            "org_role": org_role,
            "subscription_tier": "pro",
        },
    )
    if not ok:
        return False, detail or "profile_failed"
    return True, "ok"


def assign_user_to_org(
    supabase_url: str,
    headers: Dict[str, str],
    user_id: str,
    organization_id: Optional[str],
    org_role: Optional[str],
    *,
    make_enterprise: bool = True,
) -> bool:
    data: Dict[str, Any] = {
        "organization_id": organization_id,
        "org_role": org_role,
    }
    if make_enterprise and organization_id:
        data["subscription_tier"] = "pro"
    elif not organization_id:
        data["org_role"] = None
    ok, _ = supabase_update(supabase_url, headers, "profiles", user_id, data)
    return ok


def add_org_member(
    supabase_url: str,
    service_headers: Dict[str, str],
    organization_id: str,
    email: str,
    password: str,
    org_role: str = "member",
    max_seats: int = 10,
) -> tuple[bool, str]:
    if count_org_members(supabase_url, service_headers, organization_id) >= max_seats:
        return False, "seat_limit"

    normalized_email = (email or "").strip()
    user_id = find_auth_user_id_by_email(supabase_url, service_headers, normalized_email)
    if not user_id:
        user_id = create_auth_user(supabase_url, service_headers, normalized_email, password)
    if not user_id:
        return False, "auth_failed"

    pwd_ok, pwd_detail = set_auth_user_password(
        supabase_url, service_headers, user_id, password
    )
    if not pwd_ok:
        return False, pwd_detail or "password_reset_failed"

    ok, reason = ensure_profile(
        supabase_url,
        service_headers,
        user_id,
        normalized_email,
        {
            "organization_id": organization_id,
            "org_role": org_role,
            "subscription_tier": "pro",
            "free_trials_remaining": 0,
        },
    )
    return (ok, "ok" if ok else (reason or "profile_failed"))


def remove_org_member(
    supabase_url: str,
    headers: Dict[str, str],
    user_id: str,
) -> bool:
    return assign_user_to_org(
        supabase_url,
        headers,
        user_id,
        organization_id=None,
        org_role=None,
        make_enterprise=False,
    )


def list_tenant_knowledge(
    supabase_url: str,
    headers: Dict[str, str],
    organization_id: str,
) -> List[Dict[str, Any]]:
    return supabase_select(
        supabase_url,
        headers,
        "knowledge_base",
        select="id,category,content,content_en,created_at",
        filters={"scope": "tenant", "organization_id": organization_id},
        order="id.desc",
    )


def add_tenant_knowledge(
    supabase_url: str,
    headers: Dict[str, str],
    organization_id: str,
    category: str,
    content: str,
) -> bool:
    result = supabase_insert(
        supabase_url,
        headers,
        "knowledge_base",
        {
            "category": category,
            "content": content,
            "content_en": content,
            "scope": "tenant",
            "organization_id": organization_id,
            "created_at": datetime.now().isoformat(),
        },
    )
    return result is not None


def delete_tenant_knowledge(
    supabase_url: str,
    headers: Dict[str, str],
    record_id: int,
    organization_id: str,
) -> bool:
    rows = supabase_select(
        supabase_url,
        headers,
        "knowledge_base",
        filters={"id": str(record_id), "organization_id": organization_id, "scope": "tenant"},
    )
    if not rows:
        return False
    return supabase_delete(
        supabase_url,
        headers,
        "knowledge_base",
        f"id=eq.{record_id}&organization_id=eq.{organization_id}&scope=eq.tenant",
    )
