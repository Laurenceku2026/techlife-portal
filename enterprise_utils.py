"""Enterprise organizations, members, and tenant knowledge base helpers."""
from __future__ import annotations

import base64
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

KNOWLEDGE_CATEGORIES = ["光学", "机械", "材料", "热学", "电气", "控制", "其他"]
KB_CATEGORY_HEADERS = [
    "光学 / Optical",
    "机械 / Mechanical",
    "材料 / Material",
    "热学 / Thermal",
    "电气 / Electrical",
    "控制 / Control",
    "其他 / Other",
]
KB_HEADER_ROW = 3
KB_DATA_START_ROW = 4
KB_INSTRUCTION = (
    "请在下面各列类别中添加您的经验，每条经验占一格，经验之间不要留空 / "
    "Please add your knowledge in the category below, each knowledge is in one cell "
    "and no empty cell in between"
)
LOGO_MAX_BYTES = 500_000
LOGO_ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


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
        "organization_logo_url": None,
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
            select="id,name,max_seats,is_active,contract_expires_at,logo_url",
            filters={"id": org_id},
        )
        if org_rows:
            profile["organization_name"] = org_rows[0].get("name")
            profile["organization_logo_url"] = org_rows[0].get("logo_url")
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


def set_organization_logo(
    supabase_url: str,
    headers: Dict[str, str],
    org_id: str,
    file_bytes: bytes,
    content_type: str,
) -> tuple[bool, str]:
    if not org_id:
        return False, "missing_org_id"
    if not file_bytes:
        return False, "empty_file"
    if len(file_bytes) > LOGO_MAX_BYTES:
        return False, "too_large"

    normalized_type = (content_type or "").lower()
    if normalized_type == "image/jpg":
        normalized_type = "image/jpeg"
    if normalized_type not in LOGO_ALLOWED_TYPES:
        return False, "invalid_type"

    encoded = base64.b64encode(file_bytes).decode("ascii")
    data_url = f"data:{normalized_type};base64,{encoded}"
    ok, detail = supabase_update(
        supabase_url,
        headers,
        "organizations",
        org_id,
        {"logo_url": data_url},
    )
    if ok:
        return True, ""
    if "logo_url" in (detail or "") and "column" in (detail or "").lower():
        return False, "missing_column"
    return False, detail or "update_failed"


def clear_organization_logo(
    supabase_url: str,
    headers: Dict[str, str],
    org_id: str,
) -> tuple[bool, str]:
    if not org_id:
        return False, "missing_org_id"
    ok, detail = supabase_update(
        supabase_url,
        headers,
        "organizations",
        org_id,
        {"logo_url": None},
    )
    if ok:
        return True, ""
    return False, detail or "update_failed"


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


def change_user_password(
    supabase_url: str,
    anon_key: str,
    email: str,
    current_password: str,
    new_password: str,
) -> tuple[bool, str]:
    headers = {
        "apikey": anon_key,
        "Content-Type": "application/json",
    }
    try:
        login_response = requests.post(
            f"{supabase_url}/auth/v1/token?grant_type=password",
            headers=headers,
            json={"email": (email or "").strip(), "password": current_password},
            timeout=15,
        )
        if login_response.status_code != 200:
            return False, "current_password_wrong"

        access_token = login_response.json().get("access_token")
        if not access_token:
            return False, "current_password_wrong"

        update_response = requests.put(
            f"{supabase_url}/auth/v1/user",
            headers={
                **headers,
                "Authorization": f"Bearer {access_token}",
            },
            json={"password": new_password},
            timeout=15,
        )
        if update_response.status_code in (200, 201):
            return True, ""
        try:
            body = update_response.json()
            return False, (
                body.get("error_description")
                or body.get("msg")
                or body.get("message")
                or update_response.text
            )
        except ValueError:
            return False, update_response.text or f"HTTP {update_response.status_code}"
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
    *,
    content_en: Optional[str] = None,
) -> bool:
    result = supabase_insert(
        supabase_url,
        headers,
        "knowledge_base",
        {
            "category": category,
            "content": content,
            "content_en": content_en or content,
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


def _kb_workbook_title(org_name: str, lang: str) -> str:
    if lang == "en":
        return f"{org_name} · Enterprise Knowledge Database"
    return f"{org_name} · 企业数据库"


def _kb_sheet_title(lang: str) -> str:
    return "Knowledge" if lang == "en" else "知识库"


def _parse_category_label(label: Any) -> Optional[str]:
    if label is None:
        return None
    text = str(label).strip()
    if not text or text.lower() == "nan":
        return None

    if text in KNOWLEDGE_CATEGORIES:
        return text

    for category, header in zip(KNOWLEDGE_CATEGORIES, KB_CATEGORY_HEADERS):
        if text == header:
            return category
        if text.lower() == header.lower():
            return category

    if "/" in text:
        zh_part = text.split("/", 1)[0].strip()
        if zh_part in KNOWLEDGE_CATEGORIES:
            return zh_part
        en_part = text.split("/", 1)[1].strip().lower()
        en_map = {
            "optical": "光学",
            "mechanical": "机械",
            "material": "材料",
            "thermal": "热学",
            "electrical": "电气",
            "control": "控制",
            "other": "其他",
        }
        if en_part in en_map:
            return en_map[en_part]

    lowered = text.lower()
    if lowered == "other":
        return "其他"
    return None


def _write_kb_workbook(
    org_name: str,
    lang: str,
    entries_by_category: Optional[Dict[str, List[str]]] = None,
) -> bytes:
    import io

    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = _kb_sheet_title(lang)
    worksheet.cell(1, 1, _kb_workbook_title(org_name, lang))
    worksheet.cell(2, 1, KB_INSTRUCTION)

    for col_idx, header in enumerate(KB_CATEGORY_HEADERS, start=1):
        worksheet.cell(KB_HEADER_ROW, col_idx, header)

    if entries_by_category:
        max_rows = max((len(values) for values in entries_by_category.values()), default=0)
        for row_offset in range(max_rows):
            row_idx = KB_DATA_START_ROW + row_offset
            for col_idx, category in enumerate(KNOWLEDGE_CATEGORIES, start=1):
                values = entries_by_category.get(category, [])
                if row_offset < len(values):
                    worksheet.cell(row_idx, col_idx, values[row_offset])

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def build_kb_template_excel(org_name: str, lang: str = "zh") -> bytes:
    return _write_kb_workbook(org_name, lang)


def build_kb_export_excel(
    entries: List[Dict[str, Any]],
    org_name: str,
    lang: str = "zh",
) -> bytes:
    grouped: Dict[str, List[str]] = {category: [] for category in KNOWLEDGE_CATEGORIES}
    for entry in entries:
        category = _parse_category_label(entry.get("category")) or str(entry.get("category", "")).strip()
        content = str(entry.get("content", "")).strip()
        if not category or not content:
            continue
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(content)
    return _write_kb_workbook(org_name, lang, grouped)


def _load_kb_worksheet(file_bytes: bytes):
    import io

    from openpyxl import load_workbook

    return load_workbook(io.BytesIO(file_bytes)).active


def _find_kb_header_row(worksheet) -> Optional[int]:
    for row_idx in range(1, 8):
        for col_idx in range(1, 20):
            value = worksheet.cell(row_idx, col_idx).value
            if value and _parse_category_label(value):
                matched = 0
                for scan_col in range(1, 20):
                    if _parse_category_label(worksheet.cell(row_idx, scan_col).value):
                        matched += 1
                if matched >= 3:
                    return row_idx
    return None


def _parse_wide_kb_worksheet(worksheet) -> Optional[List[Dict[str, str]]]:
    header_row = _find_kb_header_row(worksheet)
    if not header_row:
        return None

    categories_by_col: Dict[int, str] = {}
    for col_idx in range(1, worksheet.max_column + 1):
        category = _parse_category_label(worksheet.cell(header_row, col_idx).value)
        if category:
            categories_by_col[col_idx] = category

    if len(categories_by_col) < 3:
        return None

    rows_to_import: List[Dict[str, str]] = []
    for row_idx in range(header_row + 1, worksheet.max_row + 1):
        for col_idx, category in categories_by_col.items():
            raw_value = worksheet.cell(row_idx, col_idx).value
            if raw_value is None:
                continue
            content = str(raw_value).strip()
            if not content or content.lower() == "nan":
                continue
            rows_to_import.append(
                {
                    "category": category,
                    "content": content,
                    "content_en": content,
                }
            )
    return rows_to_import


def _parse_legacy_kb_dataframe(file_bytes: bytes) -> Optional[List[Dict[str, str]]]:
    import io

    import pandas as pd

    legacy_aliases = {
        "category": {"分类", "category", "Category"},
        "content": {"经验内容", "content", "Content"},
        "content_en": {"经验内容(英文)", "content_en", "Content (EN)", "Content_EN"},
    }

    try:
        frame = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception:
        return None

    if frame.empty:
        return None

    column_map: Dict[str, str] = {}
    for column in frame.columns:
        cleaned = str(column).strip()
        for field, aliases in legacy_aliases.items():
            if cleaned in aliases:
                column_map[field] = column

    if "category" not in column_map or "content" not in column_map:
        return None

    rows_to_import: List[Dict[str, str]] = []
    for _, row in frame.iterrows():
        category = _parse_category_label(row.get(column_map["category"])) or str(
            row.get(column_map["category"], "")
        ).strip()
        content = str(row.get(column_map["content"], "")).strip()
        if not content:
            continue
        content_en_col = column_map.get("content_en")
        content_en = str(row.get(content_en_col, "")).strip() if content_en_col else content
        if not content_en:
            content_en = content
        rows_to_import.append(
            {
                "category": category or KNOWLEDGE_CATEGORIES[0],
                "content": content,
                "content_en": content_en,
            }
        )
    return rows_to_import or None


def delete_all_tenant_knowledge(
    supabase_url: str,
    headers: Dict[str, str],
    organization_id: str,
) -> bool:
    if not organization_id:
        return False
    return supabase_delete(
        supabase_url,
        headers,
        "knowledge_base",
        f"organization_id=eq.{quote(str(organization_id), safe='')}&scope=eq.tenant",
    )


def import_tenant_knowledge_excel(
    supabase_url: str,
    headers: Dict[str, str],
    organization_id: str,
    file_bytes: bytes,
    *,
    replace_existing: bool = False,
) -> tuple[int, str]:
    if not organization_id:
        return 0, "missing_org_id"
    if not file_bytes:
        return 0, "empty_file"

    rows_to_import: Optional[List[Dict[str, str]]] = None
    try:
        worksheet = _load_kb_worksheet(file_bytes)
        rows_to_import = _parse_wide_kb_worksheet(worksheet)
    except Exception as exc:
        return 0, f"invalid_excel:{exc}"

    if rows_to_import is None:
        rows_to_import = _parse_legacy_kb_dataframe(file_bytes)

    if rows_to_import is None:
        return 0, "missing_columns"

    if not rows_to_import:
        return 0, "no_valid_rows"

    if replace_existing:
        delete_all_tenant_knowledge(supabase_url, headers, organization_id)

    imported = 0
    for item in rows_to_import:
        if add_tenant_knowledge(
            supabase_url,
            headers,
            organization_id,
            item["category"],
            item["content"],
            content_en=item["content_en"],
        ):
            imported += 1

    if imported == 0:
        return 0, "import_failed"
    return imported, "ok"
