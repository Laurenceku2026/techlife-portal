import streamlit as st
import requests
import stripe
from datetime import datetime, timedelta, date
from typing import Dict, Optional
from urllib.parse import quote

from portal_apps import (
    PORTAL_APP_KEYS,
    app_description,
    app_display_name,
    normalize_enabled_apps,
    org_enabled_apps,
)
from portal_auth import build_app_launch_url
from portal_branding import apply_streamlit_head_patch, inject_mobile_home_screen_meta, local_page_icon, render_add_to_home_screen_help
from portal_enterprise_ui import enterprise_brand_markup
from kb_translate import bilingualize_kb_content, make_kb_translators
from enterprise_utils import (
    KNOWLEDGE_CATEGORIES,
    add_org_member,
    add_tenant_knowledge,
    assign_or_provision_org_user,
    assign_user_to_org,
    build_kb_export_excel,
    build_kb_template_excel,
    change_user_password,
    clear_organization_logo,
    count_org_members,
    create_organization,
    organization_display_name,
    set_organization_names,
    contract_expires_at_from_date,
    contract_expires_after_years,
    parse_contract_expires_date,
    format_contract_expires,
    DEFAULT_CONTRACT_YEARS,
    delete_organization,
    delete_tenant_knowledge,
    find_user_id_by_email,
    get_full_profile,
    import_tenant_knowledge_excel,
    is_enterprise_user,
    is_org_admin,
    list_org_members,
    list_organizations,
    list_tenant_knowledge,
    remove_org_member,
    set_organization_enabled_apps,
    set_organization_logo,
    update_organization,
    verify_login_credentials,
    _parse_auth_users,
)

apply_streamlit_head_patch()

# ==================== 页面配置 ====================
st.set_page_config(page_title="DFSS", page_icon=local_page_icon(), layout="wide")

# ==================== 管理员配置（从 secrets 读取） ====================
def _get_secret(key: str, *fallback_keys: str) -> str:
    for name in (key, *fallback_keys):
        value = st.secrets.get(name)
        if value:
            return str(value)
    try:
        supa = st.secrets.get("connections", {}).get("supabase", {})
        value = supa.get(key)
        if value:
            return str(value)
    except Exception:
        pass
    return ""


def _require_secret(key: str, *fallback_keys: str) -> str:
    value = _get_secret(key, *fallback_keys)
    if not value:
        st.error(f"缺少配置 {key}，请在 Streamlit Cloud Secrets 或 .streamlit/secrets.toml 中添加。")
        st.stop()
    return value

ADMIN_USERNAME = _get_secret("ADMIN_USERNAME")
ADMIN_PASSWORD = _get_secret("ADMIN_PASSWORD")
ADMIN_EMAIL = _get_secret("ADMIN_EMAIL")

# 五个 APP 的 URL（新增 AI-FA）
APP_URLS = {
    "feasibility": "https://appuct-feasibility-analysis.streamlit.app",
    "dqa": "https://ai-design-dfmea.streamlit.app",
    "fa": "https://ai-fa-8d.streamlit.app",                    # 新增 AI-FA
    "paravary": "https://dfss-stack-tolerance-analysis.streamlit.app",
    "eml": "https://healthy-light-calculator.streamlit.app"
}

# ==================== Stripe 配置 ====================
_stripe_key = _get_secret("STRIPE_SECRET_KEY")
if _stripe_key:
    stripe.api_key = _stripe_key

# ==================== Supabase 配置 ====================
SUPABASE_URL = _require_secret("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = _require_secret("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_KEY")
SUPABASE_ANON_KEY = _get_secret("SUPABASE_ANON_KEY") or SUPABASE_SERVICE_ROLE_KEY

SERVICE_HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
}

AUTH_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Content-Type": "application/json",
}


def _jwt_claim_role(token: str) -> str:
    """Read JWT role claim without verification (for key-type diagnostics)."""
    try:
        import base64
        import json as _json

        parts = (token or "").split(".")
        if len(parts) < 2:
            return ""
        payload = parts[1] + ("=" * (-len(parts[1]) % 4))
        data = _json.loads(base64.urlsafe_b64decode(payload.encode("utf-8")))
        return str(data.get("role") or "")
    except Exception:
        return ""


def _service_key_looks_writable() -> tuple[bool, str]:
    key = (SUPABASE_SERVICE_ROLE_KEY or "").strip()
    if not key:
        return False, "missing_service_role_key"
    if key.startswith("sb_publishable_"):
        return False, "publishable/anon"
    if key.startswith("eyJ"):
        role = _jwt_claim_role(key)
        if role in ("anon", "authenticated"):
            return False, role
        if role == "service_role":
            return True, role
    if key.startswith("sb_secret_"):
        return True, "secret"
    role = _jwt_claim_role(key)
    if role == "service_role":
        return True, role
    if role in ("anon", "authenticated"):
        return False, role
    # Unknown non-JWT format — allow attempt, but surface role for debugging.
    return True, role or "unknown"


def _kb_translators():
    return make_kb_translators(
        _get_secret("DEEPSEEK_API_KEY"),
        _get_secret("DEEPSEEK_BASE_URL") or "https://api.deepseek.com",
        _get_secret("DEEPSEEK_MODEL") or "deepseek-chat",
    )


def supabase_get(table: str, user_id: str = None, id_field: str = "id", *, limit: int = 1000):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if user_id:
        url += f"?{id_field}=eq.{quote(str(user_id), safe='')}&select=*"
    else:
        url += f"?select=*&order=email.asc&limit={int(limit)}"
    headers = {
        **SERVICE_HEADERS,
        "Prefer": "count=exact",
        "Range-Unit": "items",
        "Range": f"0-{max(int(limit) - 1, 0)}",
        "Cache-Control": "no-cache",
    }
    response = requests.get(url, headers=headers, timeout=30)
    return response


def supabase_patch(table: str, user_id: str, data: dict):
    """Patch a row and return the updated representation (empty list if nothing updated)."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{quote(str(user_id), safe='')}"
    headers = {
        **SERVICE_HEADERS,
        "Prefer": "return=representation",
        "Cache-Control": "no-cache",
    }
    response = requests.patch(url, headers=headers, json=data, timeout=20)
    return response


def supabase_patch_by_email(table: str, email: str, data: dict):
    encoded = quote(str(email or "").strip(), safe="")
    url = f"{SUPABASE_URL}/rest/v1/{table}?email=eq.{encoded}"
    headers = {
        **SERVICE_HEADERS,
        "Prefer": "return=representation",
        "Cache-Control": "no-cache",
    }
    return requests.patch(url, headers=headers, json=data, timeout=20)


def _parse_patch_rows(response) -> list:
    if response.status_code not in (200, 201):
        return []
    try:
        body = response.json()
    except Exception:
        return []
    return body if isinstance(body, list) else []


def supabase_patch_ok(table: str, user_id: str, data: dict, *, email: str = "") -> tuple[bool, str]:
    writable, key_kind = _service_key_looks_writable()
    if not writable:
        return (
            False,
            f"SUPABASE_SERVICE_ROLE_KEY 无效（当前识别为 {key_kind}）。请在 Streamlit Cloud Secrets 填写 service_role / sb_secret_，不要用 anon / publishable。",
        )

    response = supabase_patch(table, user_id, data)
    rows = _parse_patch_rows(response)
    if not rows and email:
        response = supabase_patch_by_email(table, email, data)
        rows = _parse_patch_rows(response)

    if response.status_code not in (200, 201):
        return False, response.text or f"HTTP {response.status_code}"
    if not rows:
        return (
            False,
            "数据库未更新任何行（可能是 service_role 配置错误，或用户 id/email 不匹配）。",
        )

    # Read back to confirm persistence for the critical trial field.
    if "free_trials_remaining" in data:
        expected = int(data["free_trials_remaining"])
        uid = rows[0].get("id") or user_id
        verify = supabase_get(table, uid)
        if verify.status_code in (200, 206):
            try:
                verify_rows = verify.json()
            except Exception:
                verify_rows = []
            if isinstance(verify_rows, list) and verify_rows:
                actual = verify_rows[0].get("free_trials_remaining")
                try:
                    if int(actual) != expected:
                        return False, f"写后读回仍为 {actual}（期望 {expected}）"
                except (TypeError, ValueError):
                    return False, f"写后读回无效值: {actual}"
        written = rows[0].get("free_trials_remaining")
        return True, f"ok:{written}"
    return True, "ok"


DEFAULT_FREE_TRIALS = 30


def _trials_display(value) -> int:
    try:
        if value is None:
            return DEFAULT_FREE_TRIALS
        return int(value)
    except (TypeError, ValueError):
        return DEFAULT_FREE_TRIALS

# ==================== 多语言配置 ====================
TEXTS = {
    "zh": {
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 关于系统",
        "about_text": """
**TechLife Suite** 是专为研发工程师打造的 **AI 赋能 DFSS（六西格玛设计）** 平台。

我们致力于用人工智能简化复杂的产品开发流程，覆盖从市场输入、设计预防到失效根治的完整闭环：

- **产品可行性分析**：挖掘市场趋势与用户之声 (VOC)。
- **AI-DQA 设计质量保证**：事前识别设计风险，AI 辅助 DFMEA。
- **Para-Vary 公差仿真**：蒙特卡罗累积公差分析，获得稳健设计。
- **AI-FA 智能故障分析**：AI 驱动 5-Why 根因定位与 8D 报告。

让 AI 成为您的产品开发首席工程师。
""",
        "contact_header": "📧 联系我们",
        "contact_email": "邮箱: Techlife2027@gmail.com",
        "main_title": "TechLife Suite 门户",
        "main_subtitle": "一站式工程研发 AI 工具集",
        "email_placeholder": "请输入邮箱",
        "password_placeholder": "请输入密码",
        "login_btn": "登录",
        "register_btn": "注册新账号",
        "forgot_password": "忘记密码?",
        "register_title": "注册新账号",
        "confirm_password": "确认密码",
        "register_submit": "注册",
        "back_to_login": "返回登录",
        "welcome": "欢迎回来",
        "logout": "登出",
        "free_trial": "剩余免费次数",
        "subscription": "订阅",
        "total_usage": "总使用次数",
        "nav_title": "应用导航",
        "admin_panel": "管理员面板",
        "chinese": "中文",
        "english": "English",
        "admin_login_title": "管理员登录",
        "admin_username": "用户名",
        "admin_password": "密码",
        "admin_login_btn": "登录",
        "admin_back": "返回用户登录",
        "admin_error": "用户名或密码错误",
        "total_users": "总用户数",
        "pro_users": "专业版用户",
        "free_users": "免费版用户",
        "user_list": "用户列表",
        "subscription_mgmt": "订阅管理",
        "select_user": "选择用户",
        "set_subscription": "设置订阅",
        "set_trials": "设置免费次数",
        "update_btn": "更新订阅",
        "save_btn": "保存更新",
        "exit_admin": "退出管理员模式",
        "email_col": "邮箱",
        "subscription_col": "订阅",
        "trials_left": "剩余次数",
        "total_used": "总使用次数",
        "reset_trials_btn": "重置次数为 30",
        "reset_trials_ok": "已重置 {email} 的免费次数为 30",
        "search_user_email": "按邮箱搜索用户",
        "current_user": "当前用户",
        "reset_all_trials": "重置所有免费用户次数",
        "batch_ops": "批量操作",
        "launch": "在新窗口打开",
        "login_failed": "登录失败",
        "register_success": "注册成功！请登录",
        "email_exists": "该邮箱已注册，请直接登录",
        "open_new_tab": "🔗 点击按钮将在新标签页中打开应用",
        "monthly": "月付 $29/月",
        "yearly": "年付 $299/年",
        "expires_at": "到期",
        "upgrade_title": "升级到专业版",
        "pro_features_title": "专业版功能：",
        "pro_feature_1": "- ✅ 无限次使用所有应用",
        "pro_feature_2": "- ✅ 优先技术支持",
        "pro_feature_3": "- ✅ 导出完整报告",
        "payment_success": "✅ 支付成功！您已是专业版用户",
        "payment_pending": "支付未完成",
        "go_to_payment": "💰 前往 Stripe 完成支付",
        "payment_created": "支付会话已创建",
        "refresh_tip": "支付成功后，请点击上方的刷新按钮 🔄 更新状态",
        "enterprise_plan": "企业版",
        "org_admin_btn": "企业管理",
        "org_admin_panel": "企业管理员",
        "exit_org_admin": "返回门户",
        "members_tab": "成员管理",
        "kb_tab": "企业知识库",
        "seats_used": "席位使用",
        "add_member": "新增成员",
        "remove_member": "移出企业",
        "member_email": "成员邮箱",
        "initial_password": "初始密码",
        "member_role": "角色",
        "org_mgmt": "企业管理",
        "create_org": "创建企业",
        "org_name": "企业名称",
        "org_name_zh": "企业名称（中文）",
        "org_name_en": "企业名称（英文）",
        "org_name_required": "请至少填写中文或英文企业名称",
        "org_names_migration_hint": "请先在 Supabase 执行 supabase_migration_org_names.sql",
        "org_name_display_lock": "固定企业名称语言",
        "org_name_display_lock_hint": "勾选后主页始终显示所选语言的企业名称；不勾选则随页面中英文切换",
        "org_name_display_fixed": "固定显示",
        "max_seats": "席位上限",
        "contract_years": "使用年限（年）",
        "contract_expires": "到期日期",
        "contract_expires_col": "到期日",
        "contract_expires_unset": "未设置",
        "assign_user_org": "绑定用户到企业",
        "org_list": "企业列表",
        "select_org": "选择企业",
        "set_org_admin": "设为管理员",
        "set_org_member": "设为成员",
        "remove_from_org": "移出企业",
        "migration_hint": "请先在 Supabase 执行 supabase_migration_enterprise.sql",
        "kb_category": "分类",
        "kb_content": "经验内容",
        "kb_add": "添加条目",
        "kb_delete": "删除",
        "kb_db_title": "{org_name} · 独立知识数据库",
        "kb_excel_hint": "第1行为企业数据库标题，第3行为分类表头（含「其他/Other」），经验从第4行起按列填写。可先下载空白模板，本地填写后上传。",
        "kb_download_template": "下载空白模板",
        "kb_download_data": "导出当前数据",
        "kb_upload_excel": "上传 Excel 文件",
        "kb_import_btn": "导入知识库",
        "kb_replace_on_import": "导入前清空现有数据",
        "kb_imported": "已导入 {count} 条记录",
        "kb_import_failed": "导入失败",
        "kb_invalid_excel": "Excel 文件格式无效",
        "kb_missing_columns": "缺少第3行分类表头（光学…其他/Other）",
        "kb_no_valid_rows": "未找到可导入的有效数据行",
        "user_mgmt_tab": "用户管理",
        "platform_kb_tab": "企业知识库",
        "platform_kb_empty": "该企业暂无知识库条目",
        "platform_kb_count": "共 {count} 条记录",
        "platform_no_orgs_kb": "暂无企业，请先在「企业管理」中创建",
        "seat_limit_reached": "已达席位上限",
        "member_added": "成员已添加",
        "member_removed": "成员已移出企业",
        "org_created": "企业已创建",
        "org_updated": "企业已更新",
        "user_assigned": "用户已绑定",
        "org_apps_title": "企业应用权限",
        "org_apps_hint": "选择该企业可使用的子应用。默认全部开启；可仅开通所需应用（例如只开 EML Calculator）。",
        "org_apps_select": "已开通应用",
        "org_apps_save": "保存应用权限",
        "org_apps_saved": "应用权限已更新",
        "org_apps_required": "至少选择一个应用",
        "org_apps_migration_hint": "请先在 Supabase 执行 supabase_migration_org_apps.sql",
        "org_apps_col": "开通应用",
        "assign_user_btn": "绑定并设置密码",
        "login_email_hint": "登录用户名为上方邮箱；新用户将自动创建账号，已有用户将重置为上述初始密码",
        "password_required": "请设置至少6位初始密码",
        "password_reset_failed": "密码设置失败",
        "login_verify_failed": "账号已绑定，但登录验证未通过，请检查 Supabase 配置或联系技术支持",
        "login_verify_ok": "登录验证通过，请用该邮箱和初始密码在门户登录",
        "user_not_found": "未找到该邮箱用户",
        "delete_org": "删除企业",
        "delete_org_confirm": "确认删除该企业（将解除所有成员绑定并删除企业知识库）",
        "org_deleted": "企业已删除",
        "confirm_delete_save": "确认删除",
        "cancel": "取消",
        "selected_org_hint": "先在下拉框选择企业，再点列表标题右侧「− 删除」，最后确认删除",
        "delete_minus": "− 删除",
        "delete_minus_help": "删除当前选中的企业",
        "pending_delete": "待删除企业",
        "change_password": "修改密码",
        "current_password": "当前密码",
        "new_password": "新密码",
        "confirm_new_password": "确认新密码",
        "password_changed": "密码已更新，请使用新密码登录",
        "current_password_wrong": "当前密码不正确",
        "password_mismatch": "两次输入的新密码不一致",
        "org_logo": "企业 Logo",
        "upload_logo": "上传 Logo（PNG/JPG/WebP，不超过 500KB）",
        "save_logo": "保存 Logo",
        "remove_logo": "删除 Logo",
        "logo_saved": "Logo 已更新",
        "logo_removed": "Logo 已删除",
        "logo_too_large": "图片过大，请小于 500KB",
        "logo_invalid_type": "仅支持 PNG、JPG 或 WebP",
        "logo_migration_hint": "请先在 Supabase 执行 supabase_migration_org_logo.sql",
        "add_home_title": "📱 添加到主屏幕（DFSS）",
        "add_home_intro": "在手机浏览器打开本页后，可将 **DFSS** 图标添加到主屏幕，像 App 一样快速打开。",
        "add_home_ios": "**iPhone（Safari）**：分享 → **添加到主屏幕**",
        "add_home_android_chrome": "**Android（Chrome）**：菜单 ⋮ → **安装应用** 或 **添加到主屏幕**",
        "add_home_edge": "**Microsoft Edge**：菜单 ··· → **添加到手机** / **安装此站点为应用**",
        "add_home_xiaomi": "**小米浏览器**：菜单 → **添加到主屏幕** 或 **添加快捷方式到桌面**",
        "add_home_huawei": "**华为 / 荣耀浏览器**：菜单 → **添加至** / **添加到主屏幕**（或在收藏夹中选择 **添加到桌面**）",
        "add_home_vivo": "**vivo 浏览器**：菜单 → **添加到桌面** 或 **添加快捷方式**（部分机型在「收藏」→ **添加到主屏幕**）",
        "add_home_samsung": "**三星浏览器（Samsung Internet）**：菜单 ☰ → **添加页面至** → **主屏幕**",
        "settings_tab": "企业设置",
        "license_expire": "使用到期日",
    },
    "en": {
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 About System",
        "about_text": """
**TechLife Suite** is an **AI-empowered DFSS (Design for Six Sigma)** platform for R&D engineers.

We use artificial intelligence to simplify complex product development, covering the full loop from market input and design prevention to failure resolution:

- **Product Feasibility**: Market trends and Voice of Customer (VOC).
- **AI-DQA**: Upfront design risk identification with AI-assisted DFMEA.
- **Para-Vary**: Monte Carlo tolerance stack-up for robust design.
- **AI-FA**: AI-driven 5-Why root cause analysis and 8D reporting.

Let AI be your Chief Product Development Engineer.
""",
        "contact_header": "📧 Contact Us",
        "contact_email": "Email: Techlife2027@gmail.com",
        "main_title": "TechLife Suite Portal",
        "main_subtitle": "One-stop AI Toolkit for R&D Engineering",
        "email_placeholder": "Enter your email",
        "password_placeholder": "Enter your password",
        "login_btn": "LOG IN",
        "register_btn": "REGISTER",
        "forgot_password": "Forgot Password?",
        "register_title": "Register New Account",
        "confirm_password": "Confirm Password",
        "register_submit": "Register",
        "back_to_login": "Back to Login",
        "welcome": "Welcome back",
        "logout": "Logout",
        "free_trial": "Remaining Trials",
        "subscription": "Subscription",
        "total_usage": "Total Usage",
        "nav_title": "App Navigation",
        "admin_panel": "Admin Panel",
        "chinese": "中文",
        "english": "English",
        "admin_login_title": "Admin Login",
        "admin_username": "Username",
        "admin_password": "Password",
        "admin_login_btn": "Login",
        "admin_back": "Back to User Login",
        "admin_error": "Invalid credentials",
        "total_users": "Total Users",
        "pro_users": "Pro Users",
        "free_users": "Free Users",
        "user_list": "User List",
        "subscription_mgmt": "Subscription Management",
        "select_user": "Select User",
        "set_subscription": "Set Subscription",
        "set_trials": "Set Trials",
        "update_btn": "Update",
        "save_btn": "Save changes",
        "exit_admin": "Exit Admin Mode",
        "email_col": "Email",
        "subscription_col": "Subscription",
        "trials_left": "Trials Left",
        "total_used": "Total Used",
        "reset_trials_btn": "Reset trials to 30",
        "reset_trials_ok": "Reset trials for {email} to 30",
        "search_user_email": "Search user by email",
        "current_user": "Current user",
        "reset_all_trials": "Reset All Free Users Trials",
        "batch_ops": "Batch Operations",
        "launch": "Open in New Tab",
        "login_failed": "Login failed",
        "register_success": "Registration successful! Please login.",
        "email_exists": "Email already registered. Please login.",
        "open_new_tab": "🔗 Click button to open app in new tab",
        "monthly": "Monthly $29/month",
        "yearly": "Yearly $299/year",
        "expires_at": "Expires",
        "upgrade_title": "Upgrade to Pro",
        "pro_features_title": "Pro Features:",
        "pro_feature_1": "- ✅ Unlimited access to all apps",
        "pro_feature_2": "- ✅ Priority support",
        "pro_feature_3": "- ✅ Export full reports",
        "payment_success": "✅ Payment successful! You are now a Pro user!",
        "payment_pending": "Payment not completed",
        "go_to_payment": "💰 Go to Stripe to complete payment",
        "payment_created": "Payment session created",
        "refresh_tip": "After payment, please click the refresh button 🔄 above to update status",
        "enterprise_plan": "Enterprise",
        "org_admin_btn": "Org Admin",
        "org_admin_panel": "Organization Admin",
        "exit_org_admin": "Back to Portal",
        "members_tab": "Members",
        "kb_tab": "Knowledge Base",
        "seats_used": "Seats",
        "add_member": "Add Member",
        "remove_member": "Remove",
        "member_email": "Member Email",
        "initial_password": "Initial Password",
        "member_role": "Role",
        "org_mgmt": "Organizations",
        "create_org": "Create Organization",
        "org_name": "Organization Name",
        "org_name_zh": "Organization name (Chinese)",
        "org_name_en": "Organization name (English)",
        "org_name_required": "Enter at least a Chinese or English organization name",
        "org_names_migration_hint": "Run supabase_migration_org_names.sql in Supabase first",
        "org_name_display_lock": "Lock organization name language",
        "org_name_display_lock_hint": "When checked, the portal always shows the selected language; when unchecked, it follows the page language",
        "org_name_display_fixed": "Always show",
        "max_seats": "Max Seats",
        "contract_years": "Contract term (years)",
        "contract_expires": "Expiry date",
        "contract_expires_col": "Expires",
        "contract_expires_unset": "Not set",
        "assign_user_org": "Assign User to Organization",
        "org_list": "Organization List",
        "select_org": "Select Organization",
        "set_org_admin": "Set as Admin",
        "set_org_member": "Set as Member",
        "remove_from_org": "Remove from Org",
        "migration_hint": "Run supabase_migration_enterprise.sql in Supabase first",
        "kb_category": "Category",
        "kb_content": "Content",
        "kb_add": "Add Entry",
        "kb_delete": "Delete",
        "kb_db_title": "{org_name} · Dedicated Knowledge Database",
        "kb_excel_hint": "Row 1 is the title, row 3 has category headers (including Other), and knowledge starts from row 4 by column. Download the blank template, fill locally, then upload.",
        "kb_download_template": "Download Blank Template",
        "kb_download_data": "Export Current Data",
        "kb_upload_excel": "Upload Excel File",
        "kb_import_btn": "Import Knowledge Base",
        "kb_replace_on_import": "Clear existing data before import",
        "kb_imported": "Imported {count} record(s)",
        "kb_import_failed": "Import failed",
        "kb_invalid_excel": "Invalid Excel file",
        "kb_missing_columns": "Required wide-format headers missing on row 3 (Optical … Other)",
        "kb_no_valid_rows": "No valid rows found to import",
        "user_mgmt_tab": "User Management",
        "platform_kb_tab": "Org Knowledge Bases",
        "platform_kb_empty": "No knowledge entries for this organization",
        "platform_kb_count": "{count} record(s)",
        "platform_no_orgs_kb": "No organizations yet. Create one under Organizations first.",
        "seat_limit_reached": "Seat limit reached",
        "member_added": "Member added",
        "member_removed": "Member removed",
        "org_created": "Organization created",
        "org_updated": "Organization updated",
        "user_assigned": "User assigned",
        "org_apps_title": "Organization App Access",
        "org_apps_hint": "Choose which child apps this organization may launch. All apps are enabled by default; restrict to only what they need (e.g. EML Calculator only).",
        "org_apps_select": "Enabled apps",
        "org_apps_save": "Save app access",
        "org_apps_saved": "App access updated",
        "org_apps_required": "Select at least one app",
        "org_apps_migration_hint": "Run supabase_migration_org_apps.sql in Supabase first",
        "org_apps_col": "Apps enabled",
        "assign_user_btn": "Assign and Set Password",
        "login_email_hint": "Login username is the email above. New users are created; existing users get the password reset.",
        "password_required": "Initial password must be at least 6 characters",
        "password_reset_failed": "Failed to set password",
        "login_verify_failed": "User bound, but login verification failed. Check Supabase settings or contact support.",
        "login_verify_ok": "Login verified. Use this email and the initial password on the portal.",
        "user_not_found": "User email not found",
        "delete_org": "Delete Organization",
        "delete_org_confirm": "Confirm delete (unbinds all members and removes tenant knowledge base)",
        "org_deleted": "Organization deleted",
        "confirm_delete_save": "Confirm Delete",
        "cancel": "Cancel",
        "selected_org_hint": "Select an organization, click − Delete at the top right of the list, then confirm",
        "delete_minus": "− Delete",
        "delete_minus_help": "Delete the selected organization",
        "pending_delete": "Organization pending delete",
        "change_password": "Change Password",
        "current_password": "Current Password",
        "new_password": "New Password",
        "confirm_new_password": "Confirm New Password",
        "password_changed": "Password updated. Please sign in with your new password.",
        "current_password_wrong": "Current password is incorrect",
        "password_mismatch": "New passwords do not match",
        "org_logo": "Organization Logo",
        "upload_logo": "Upload logo (PNG/JPG/WebP, max 500KB)",
        "save_logo": "Save Logo",
        "remove_logo": "Remove Logo",
        "logo_saved": "Logo updated",
        "logo_removed": "Logo removed",
        "logo_too_large": "Image too large. Max 500KB.",
        "logo_invalid_type": "Only PNG, JPG, or WebP is supported",
        "logo_migration_hint": "Run supabase_migration_org_logo.sql in Supabase first",
        "add_home_title": "📱 Add to Home Screen (DFSS)",
        "add_home_intro": "Open this page in your mobile browser to add the **DFSS** icon to your home screen.",
        "add_home_ios": "**iPhone (Safari)**: Share → **Add to Home Screen**",
        "add_home_android_chrome": "**Android (Chrome)**: Menu ⋮ → **Install app** or **Add to Home screen**",
        "add_home_edge": "**Microsoft Edge**: Menu ··· → **Add to phone** / **Install this site as an app**",
        "add_home_xiaomi": "**Xiaomi Browser**: Menu → **Add to Home screen** or **Add shortcut to desktop**",
        "add_home_huawei": "**Huawei / Honor Browser**: Menu → **Add to** / **Add to Home screen** (or **Add to desktop** from bookmarks)",
        "add_home_vivo": "**vivo Browser**: Menu → **Add to desktop** or **Add shortcut** (on some models: **Bookmarks** → **Add to Home screen**)",
        "add_home_samsung": "**Samsung Internet**: Menu ☰ → **Add page to** → **Home screen**",
        "settings_tab": "Settings",
        "license_expire": "License expire",
    }
}

# ==================== Session State ====================
if "lang" not in st.session_state:
    st.session_state.lang = "zh"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False
if "reset_password" not in st.session_state:
    st.session_state.reset_password = False
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "show_admin_login" not in st.session_state:
    st.session_state.show_admin_login = False
if "org_admin_mode" not in st.session_state:
    st.session_state.org_admin_mode = False
if "pending_delete_org_id" not in st.session_state:
    st.session_state.pending_delete_org_id = None

def t():
    return TEXTS[st.session_state.lang]

# ==================== 辅助函数 ====================
def get_user_profile(user_id: str):
    return get_full_profile(SUPABASE_URL, SERVICE_HEADERS, user_id)

def get_user_total_usage(user_id: str):
    if not user_id or user_id == "admin":
        return 0
    try:
        response = supabase_get("usage_logs", user_id, id_field="user_id")
        if response.status_code == 200:
            data = response.json()
            return sum([item.get("analysis_count", 1) for item in data])
    except Exception:
        pass
    return 0

#------------
def create_checkout_session(user_id: str, user_email: str, price_id: str):
    if not _stripe_key:
        return None, "Missing STRIPE_SECRET_KEY"
    stripe.api_key = _stripe_key
    try:
        session = stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url="https://techlife-app.streamlit.app?payment_success=true",  # ← 改这里
            cancel_url="https://techlife-app.streamlit.app",
            metadata={'user_id': user_id, 'price_id': price_id}
        )
        return session.url, None
    except Exception as e:
        return None, str(e)

#---
def handle_stripe_callback():
    """处理 Stripe 支付成功回调（由 Webhook 处理，前端只显示消息）"""
    query_params = st.query_params
    if "session_id" in query_params:
        # 显示成功消息（不再调用 Stripe API）
        st.success("🎉 支付成功！您已升级为专业版用户")
        st.info("📌 请重新登录以激活专业版权限")
        # 清除 URL 参数
        st.query_params.clear()

def reset_to_guest_session():
    """Clear auth and widget state before showing the public login page."""
    preserved_lang = st.session_state.get("lang", "zh")
    password_flash = st.session_state.get("_password_changed_flash", False)
    keys_to_delete = [key for key in list(st.session_state.keys()) if not str(key).startswith("_")]
    for key in keys_to_delete:
        del st.session_state[key]
    st.session_state.lang = preserved_lang
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.admin_mode = False
    st.session_state.org_admin_mode = False
    st.session_state.show_admin_login = False
    st.session_state.show_register = False
    st.session_state.reset_password = False
    st.session_state.pending_delete_org_id = None
    _scrub_admin_url_query_params()
    if password_flash:
        st.session_state._password_changed_flash = True


def reset_to_authenticated_main_session():
    """Clear widget state while keeping the logged-in enterprise/personal user."""
    preserved_lang = st.session_state.get("lang", "zh")
    password_flash = st.session_state.get("_password_changed_flash", False)
    authenticated = st.session_state.get("authenticated", False)
    user_id = st.session_state.get("user_id")
    user_email = st.session_state.get("user_email")

    keys_to_delete = [key for key in list(st.session_state.keys()) if not str(key).startswith("_")]
    for key in keys_to_delete:
        del st.session_state[key]

    st.session_state.lang = preserved_lang
    st.session_state.authenticated = authenticated
    st.session_state.user_id = user_id
    st.session_state.user_email = user_email
    st.session_state.admin_mode = False
    st.session_state.org_admin_mode = False
    st.session_state.show_admin_login = False
    st.session_state.show_register = False
    st.session_state.reset_password = False
    st.session_state.pending_delete_org_id = None
    if password_flash:
        st.session_state._password_changed_flash = True


def request_guest_reset():
    st.session_state._guest_reset = True


def apply_pending_guest_reset():
    if st.session_state.pop("_guest_reset", False):
        reset_to_guest_session()


PLATFORM_ADMIN_WIDGET_KEYS = (
    "platform_admin_section",
    "platform_tab_btn_users",
    "platform_tab_btn_orgs",
    "platform_tab_btn_kb",
    "platform_kb_org_id",
    "platform_selected_org_id",
    "platform_kb_download_template_btn",
    "platform_kb_download_export_btn",
    "platform_kb_excel_uploader",
    "platform_kb_replace_on_import",
    "platform_kb_import_btn",
    "platform_kb_delete_select",
    "platform_kb_delete_btn",
    "admin_select_user",
    "admin_select_user_id",
    "admin_new_tier",
    "admin_new_trials",
    "admin_months",
    "admin_update_btn",
    "admin_reset_trials_btn",
    "admin_reset_pwd",
    "admin_reset_all",
    "admin_user_search",
    "admin_exit",
    "admin_username",
    "admin_password",
    "org_minus_btn",
    "confirm_delete_org_btn",
    "cancel_delete_org_btn",
    "platform_org_name_zh",
    "platform_org_name_en",
    "platform_org_name_lock",
    "platform_org_name_fixed_lang",
    "platform_org_max_seats",
    "platform_org_contract_expires",
    "platform_update_org_btn",
    "platform_save_names_btn",
    "platform_org_enabled_apps",
    "platform_org_apps_save_btn",
    "platform_assign_email",
    "platform_assign_password",
    "platform_assign_role_email",
    "platform_remove_email",
)


def _reset_platform_admin_widget_state():
    for key in PLATFORM_ADMIN_WIDGET_KEYS:
        st.session_state.pop(key, None)
    for key in list(st.session_state.keys()):
        key_str = str(key)
        if key_str.startswith("FormSubmitter:") and (
            "platform_" in key_str or "admin_" in key_str or "org_" in key_str
        ):
            st.session_state.pop(key, None)
    st.session_state.pop("_admin_tier_user", None)


def apply_pending_admin_login():
    if not st.session_state.pop("_pending_admin_login", False):
        return
    _reset_platform_admin_widget_state()
    st.session_state.admin_mode = True
    st.session_state.show_admin_login = False
    st.session_state.authenticated = True
    st.session_state.user_email = ADMIN_EMAIL or ""
    st.session_state.user_id = "admin"
    st.session_state.platform_admin_section = "users"


ORG_ADMIN_WIDGET_KEYS = (
    "org_admin_section",
    "org_tab_btn_members",
    "org_tab_btn_kb",
    "org_tab_btn_settings",
    "org_remove_select",
    "org_remove_btn",
    "kb_download_template_btn",
    "kb_download_export_btn",
    "kb_excel_uploader",
    "kb_replace_on_import",
    "kb_import_btn",
    "org_kb_delete_select",
    "org_kb_delete_btn",
    "org_admin_logo_uploader",
    "org_admin_save_logo",
    "org_admin_remove_logo",
    "org_admin_save_names_btn",
    "org_admin_org_name_lock",
    "org_admin_org_name_fixed_lang",
    "org_admin_exit",
)

ORG_ADMIN_SECTION_WIDGET_KEYS = {
    "members": (
        "org_remove_select",
        "org_remove_btn",
        "org_member_email",
        "org_member_password",
        "org_member_role",
    ),
    "kb": (
        "kb_download_template_btn",
        "kb_download_export_btn",
        "kb_excel_uploader",
        "kb_replace_on_import",
        "kb_import_btn",
        "org_kb_delete_select",
        "org_kb_delete_btn",
        "org_kb_add_category",
        "org_kb_add_content",
    ),
    "settings": (
        "org_admin_org_name_zh",
        "org_admin_org_name_en",
        "org_admin_org_name_lock",
        "org_admin_org_name_fixed_lang",
        "org_admin_save_names_btn",
        "org_admin_logo_uploader",
        "org_admin_save_logo",
        "org_admin_remove_logo",
    ),
}

ORG_ADMIN_SECTION_KEY_PREFIXES = {
    "members": ("org_member_", "org_remove_", "org_add_member"),
    "kb": ("kb_", "org_kb_"),
    "settings": ("org_admin_org_name", "org_admin_logo", "org_admin_save", "org_admin_remove"),
}

ORG_ADMIN_SECTION_FORM_PREFIXES = {
    "members": "FormSubmitter:org_add_member_form",
    "kb": "FormSubmitter:org_kb_add_form",
}


def _clear_org_admin_section_keys(section: str):
    for key in ORG_ADMIN_SECTION_WIDGET_KEYS.get(section, ()):
        st.session_state.pop(key, None)
    for prefix in ORG_ADMIN_SECTION_KEY_PREFIXES.get(section, ()):
        for key in list(st.session_state.keys()):
            if str(key).startswith(prefix):
                st.session_state.pop(key, None)
    form_prefix = ORG_ADMIN_SECTION_FORM_PREFIXES.get(section)
    if form_prefix:
        for key in list(st.session_state.keys()):
            if str(key).startswith(form_prefix):
                st.session_state.pop(key, None)


_HIDDEN_ADMIN_TAB_CSS = """
<style>
div[data-testid="stExpander"] details > summary {
    display: none !important;
}
div[data-testid="stExpander"] details {
    border: none !important;
}
div[data-testid="stExpander"] .streamlit-expanderContent {
    border: none !important;
    padding-top: 0 !important;
}
</style>
"""


def _scrub_admin_url_query_params():
    for param in ("admin_tab", "org_tab"):
        if param in st.query_params:
            del st.query_params[param]


def request_org_admin_section_switch(target_section: str):
    if st.session_state.get("org_admin_section", "members") == target_section:
        return
    st.session_state.org_admin_section = target_section
    st.session_state._org_admin_active_section = target_section


def request_platform_admin_section_switch(target_section: str):
    if st.session_state.get("platform_admin_section", "users") == target_section:
        return
    st.session_state.platform_admin_section = target_section


def _render_admin_tab_buttons(
    section_labels: Dict[str, str],
    selected_section: str,
    key_prefix: str,
    on_switch,
):
    tab_keys = list(section_labels.keys())
    cols = st.columns(len(tab_keys))
    for col, tab_key in zip(cols, tab_keys):
        with col:
            st.button(
                section_labels[tab_key],
                key=f"{key_prefix}_tab_btn_{tab_key}",
                type="primary" if selected_section == tab_key else "secondary",
                use_container_width=True,
                disabled=selected_section == tab_key,
                on_click=on_switch,
                args=(tab_key,),
            )


def _render_hidden_expander_tab_css():
    st.markdown(_HIDDEN_ADMIN_TAB_CSS, unsafe_allow_html=True)


def _clear_org_admin_widget_keys():
    for key in ORG_ADMIN_WIDGET_KEYS:
        st.session_state.pop(key, None)
    for key in list(st.session_state.keys()):
        if str(key).startswith("FormSubmitter:") and "org_" in str(key):
            st.session_state.pop(key, None)


def request_org_admin_exit():
    st.session_state._exit_org_admin_pending = True


def request_org_admin_entry():
    st.session_state._enter_org_admin_pending = True


def apply_pending_org_admin_entry():
    if st.session_state.pop("_enter_org_admin_pending", False):
        reset_to_authenticated_main_session()
        st.session_state.org_admin_mode = True
        st.session_state.org_admin_section = "members"
        st.session_state._org_admin_active_section = "members"
        st.session_state.pop("_org_admin_names_org_id", None)
        st.session_state.pop("_platform_names_org_id", None)


def apply_pending_org_admin_exit():
    if st.session_state.pop("_exit_org_admin_pending", False):
        reset_to_authenticated_main_session()


def _safe_date_prefix(value, fallback: str = "-") -> str:
    if not value:
        return fallback
    return str(value)[:10]


def _welcome_display_name(email: Optional[str]) -> str:
    if not email:
        return ""
    local = email.split("@", 1)[0].strip()
    if not local:
        return email
    return local.capitalize()


def profile_organization_name(profile, lang=None):
    if not profile:
        return ""
    return organization_display_name(
        lang=lang or st.session_state.get("lang", "zh"),
        name_zh=profile.get("organization_name_zh"),
        name_en=profile.get("organization_name_en"),
        name=profile.get("organization_name_legacy"),
        name_display_mode=profile.get("organization_name_display_mode") or "auto",
    )


def sync_org_name_widget_state(org_id, org, prefix: str):
    name_zh = (org.get("name_zh") or org.get("name") or "").strip()
    name_en = (org.get("name_en") or "").strip()
    display_mode = (org.get("name_display_mode") or "auto").strip().lower()
    if display_mode not in ("zh", "en"):
        display_mode = "auto"

    zh_key = f"{prefix}_org_name_zh"
    en_key = f"{prefix}_org_name_en"
    lock_key = f"{prefix}_org_name_lock"
    fixed_key = f"{prefix}_org_name_fixed_lang"
    tracked_id = st.session_state.get(f"_{prefix}_names_org_id")
    needs_sync = (
        tracked_id != org_id
        or zh_key not in st.session_state
        or en_key not in st.session_state
    )
    if needs_sync:
        st.session_state[f"_{prefix}_names_org_id"] = org_id
        st.session_state[zh_key] = name_zh
        st.session_state[en_key] = name_en
        st.session_state[lock_key] = display_mode in ("zh", "en")
        st.session_state[fixed_key] = display_mode if display_mode in ("zh", "en") else "zh"


def render_organization_names_editor(org_id, org, key_prefix: str):
    sync_org_name_widget_state(org_id, org, key_prefix)
    col_zh, col_en = st.columns(2)
    with col_zh:
        name_zh = st.text_input(t()["org_name_zh"], key=f"{key_prefix}_org_name_zh")
    with col_en:
        name_en = st.text_input(t()["org_name_en"], key=f"{key_prefix}_org_name_en")
    lock_display = st.checkbox(
        t()["org_name_display_lock"],
        help=t()["org_name_display_lock_hint"],
        key=f"{key_prefix}_org_name_lock",
    )
    fixed_lang = "zh"
    if lock_display:
        fixed_lang = st.radio(
            t()["org_name_display_fixed"],
            options=["zh", "en"],
            format_func=lambda value: t()["chinese"] if value == "zh" else t()["english"],
            horizontal=True,
            key=f"{key_prefix}_org_name_fixed_lang",
        )
    display_mode = fixed_lang if lock_display else "auto"
    if st.button(t()["save_btn"], key=f"{key_prefix}_save_names_btn", use_container_width=True):
        ok, reason = set_organization_names(
            SUPABASE_URL,
            SERVICE_HEADERS,
            org_id,
            name_zh,
            name_en,
            name_display_mode=display_mode,
        )
        if ok:
            st.success(t()["org_updated"])
            st.rerun()
        elif reason == "name_required":
            st.warning(t()["org_name_required"])
        elif reason == "missing_column":
            st.error(t()["org_names_migration_hint"])
        else:
            st.error(reason or t()["org_names_migration_hint"])
    return name_zh, name_en


def safe_get_profile(user_id: str):
    try:
        return get_user_profile(user_id)
    except Exception:
        return {
            "subscription_tier": "free",
            "free_trials_remaining": 30,
            "subscription_expires_at": None,
            "organization_id": None,
            "org_role": None,
            "organization_name": None,
            "organization_name_zh": None,
            "organization_name_en": None,
            "organization_name_legacy": None,
            "organization_name_display_mode": "auto",
            "organization_logo_url": None,
        }


def render_enterprise_branding(profile):
    org_name = profile_organization_name(profile)
    if not org_name:
        return

    logo_url = profile.get("organization_logo_url")
    st.markdown(
        enterprise_brand_markup(org_name, logo_url, variant="main"),
        unsafe_allow_html=True,
    )


def _handle_logo_upload_result(ok: bool, reason: str):
    if ok:
        st.success(t()["logo_saved"])
        st.rerun()
    elif reason == "too_large":
        st.error(t()["logo_too_large"])
    elif reason == "invalid_type":
        st.error(t()["logo_invalid_type"])
    elif reason == "missing_column":
        st.error(t()["logo_migration_hint"])
    elif reason == "empty_file":
        st.warning(t()["upload_logo"])
    else:
        st.error(reason or t()["logo_invalid_type"])


def render_org_logo_section(
    org_id: str,
    logo_url,
    key_prefix: str,
    *,
    include_uploader: bool = True,
    uploaded=None,
):
    st.subheader(t()["org_logo"])
    if logo_url:
        st.image(logo_url, width=140)
    if include_uploader:
        uploaded = st.file_uploader(
            t()["upload_logo"],
            type=["png", "jpg", "jpeg", "webp"],
            key=f"{key_prefix}_logo_uploader",
        )
    col_save, col_remove = st.columns(2)
    with col_save:
        if st.button(t()["save_logo"], key=f"{key_prefix}_save_logo", use_container_width=True, type="primary"):
            if not uploaded:
                st.warning(t()["upload_logo"])
            else:
                ok, reason = set_organization_logo(
                    SUPABASE_URL,
                    SERVICE_HEADERS,
                    org_id,
                    uploaded.getvalue(),
                    uploaded.type or "",
                )
                _handle_logo_upload_result(ok, reason)
    with col_remove:
        if logo_url and st.button(t()["remove_logo"], key=f"{key_prefix}_remove_logo", use_container_width=True):
            ok, reason = clear_organization_logo(SUPABASE_URL, SERVICE_HEADERS, org_id)
            if ok:
                st.success(t()["logo_removed"])
                st.rerun()
            elif reason == "missing_column":
                st.error(t()["logo_migration_hint"])
            else:
                st.error(reason or t()["logo_invalid_type"])


def render_sidebar_change_password():
    with st.expander(t()["change_password"], expanded=False):
        with st.form("sidebar_change_password_form", border=False):
            current_password = st.text_input(t()["current_password"], type="password")
            new_password = st.text_input(t()["new_password"], type="password")
            confirm_password = st.text_input(t()["confirm_new_password"], type="password")
            submitted = st.form_submit_button(t()["change_password"], use_container_width=True)
            if submitted:
                if len(new_password or "") < 6:
                    st.warning(t()["password_required"])
                elif new_password != confirm_password:
                    st.warning(t()["password_mismatch"])
                elif not current_password:
                    st.warning(t()["current_password_wrong"])
                else:
                    ok, reason = change_user_password(
                        SUPABASE_URL,
                        SUPABASE_ANON_KEY,
                        st.session_state.user_email,
                        current_password,
                        new_password,
                    )
                    if ok:
                        st.session_state._password_changed_flash = True
                        request_guest_reset()
                        st.rerun()
                    elif reason == "current_password_wrong":
                        st.error(t()["current_password_wrong"])
                    else:
                        st.error(reason or t()["password_reset_failed"])


# ==================== UI 组件 ====================
def render_sidebar():
    with st.sidebar:
        profile = None
        if st.session_state.authenticated and st.session_state.user_id not in (None, "admin"):
            profile = safe_get_profile(st.session_state.user_id)
        enterprise = bool(profile and is_enterprise_user(profile))

        if enterprise:
            org_name = profile_organization_name(profile) or t()["enterprise_plan"]
            logo_url = profile.get("organization_logo_url")
            st.markdown(
                enterprise_brand_markup(org_name, logo_url, variant="sidebar"),
                unsafe_allow_html=True,
            )
        else:
            st.title(t()["sidebar_title"])
        st.subheader(t()["about_header"])
        st.markdown(t()["about_text"])
        if not enterprise:
            st.divider()
            st.subheader(t()["contact_header"])
            st.markdown(t()["contact_email"])

        render_add_to_home_screen_help(translate=t)
        
        if st.session_state.authenticated:
            st.divider()
            st.markdown(f"**👤 {st.session_state.user_email or ''}**")

            if st.session_state.user_id == "admin":
                st.caption("平台管理员" if st.session_state.lang == "zh" else "Platform Admin")
                st.button(
                    t()["logout"],
                    use_container_width=True,
                    key="admin_sidebar_logout",
                    on_click=request_guest_reset,
                )
            else:
                if profile is None:
                    profile = safe_get_profile(st.session_state.user_id)
                tier = profile.get("subscription_tier", "free")
                remaining = profile.get("free_trials_remaining", 30)
                total_usage = get_user_total_usage(st.session_state.user_id)

                if enterprise:
                    pass
                else:
                    st.caption(f"📋 {t()['subscription']}: {'💎 Pro' if tier == 'pro' else '🔒 Free'}")
                    if tier == "free":
                        st.caption(f"🎫 {t()['free_trial']}: {remaining}")
                        st.caption(f"📊 {t()['total_usage']}: {total_usage}")
                    else:
                        st.caption(f"🎫 {t()['free_trial']}: ∞")
                        expires_at = profile.get("subscription_expires_at")
                        if expires_at:
                            st.caption(f"📅 {t()['expires_at']}: {_safe_date_prefix(expires_at)}")

                render_sidebar_change_password()

                if st.button(t()["logout"], use_container_width=True):
                    request_guest_reset()
                    st.rerun()

                if not enterprise and tier == "free":
                    st.markdown("---")
                    st.markdown(f"### 💎 {t()['upgrade_title']}")
                    st.markdown(f"**{t()['pro_features_title']}**")
                    st.markdown(t()["pro_feature_1"])
                    st.markdown(t()["pro_feature_2"])
                    st.markdown(t()["pro_feature_3"])

                    if st.button(t()["monthly"], key="sidebar_monthly_btn", use_container_width=True, type="primary"):
                        spinner_text = "正在创建支付会话..." if st.session_state.lang == "zh" else "Creating payment session..."
                        with st.spinner(spinner_text):
                            url, error = create_checkout_session(
                                st.session_state.user_id, st.session_state.user_email,
                                st.secrets["STRIPE_PRICE_MONTHLY"]
                            )
                            if url:
                                st.session_state.payment_url = url
                                st.session_state.payment_type = "monthly"
                                st.rerun()
                            else:
                                error_text = "创建支付会话失败" if st.session_state.lang == "zh" else "Failed to create payment session"
                                st.error(f"{error_text}: {error}")

                    if st.button(t()["yearly"], key="sidebar_yearly_btn", use_container_width=True, type="primary"):
                        spinner_text = "正在创建支付会话..." if st.session_state.lang == "zh" else "Creating payment session..."
                        with st.spinner(spinner_text):
                            url, error = create_checkout_session(
                                st.session_state.user_id, st.session_state.user_email,
                                st.secrets["STRIPE_PRICE_YEARLY"]
                            )
                            if url:
                                st.session_state.payment_url = url
                                st.session_state.payment_type = "yearly"
                                st.rerun()
                            else:
                                error_text = "创建支付会话失败" if st.session_state.lang == "zh" else "Failed to create payment session"
                                st.error(f"{error_text}: {error}")

                    if "payment_url" in st.session_state and st.session_state.payment_url:
                        if st.session_state.payment_type == "monthly":
                            payment_display = "月付" if st.session_state.lang == "zh" else "Monthly"
                        else:
                            payment_display = "年付" if st.session_state.lang == "zh" else "Yearly"
                        st.success(f"✅ {payment_display} {t()['payment_created']}")
                        button_html = f'''
                        <a href="{st.session_state.payment_url}" target="_blank" style="
                            display: block;
                            width: 100%;
                            padding: 0.5rem 0.75rem;
                            background-color: #ff4b4b;
                            color: white;
                            text-align: center;
                            text-decoration: none;
                            border-radius: 0.5rem;
                            font-weight: 500;
                            margin: 0.5rem 0;
                            border: none;
                            cursor: pointer;
                            transition: background-color 0.2s;
                        " onmouseover="this.style.backgroundColor='#e04343'" onmouseout="this.style.backgroundColor='#ff4b4b'">
                            {t()["go_to_payment"]}
                        </a>
                        '''
                        st.markdown(button_html, unsafe_allow_html=True)
                        st.info(t()["refresh_tip"])

def render_top_buttons():
    profile = None
    if st.session_state.authenticated and st.session_state.user_id not in (None, "admin"):
        profile = safe_get_profile(st.session_state.user_id)
    show_org_gear = profile and is_org_admin(profile)
    show_platform_gear = not st.session_state.authenticated

    col1, col2, col3, col4, col5 = st.columns([8, 1.2, 1.2, 1.2, 1])
    with col2:
        if st.button(t()["chinese"], key="zh_btn", use_container_width=True, type="primary"):
            if st.session_state.lang != "zh":
                st.session_state.lang = "zh"
                st.rerun()
    with col3:
        if st.button(t()["english"], key="en_btn", use_container_width=True, type="primary"):
            if st.session_state.lang != "en":
                st.session_state.lang = "en"
                st.rerun()
    with col4:
        if show_org_gear:
            st.button(
                "⚙️",
                key="org_gear_btn",
                help=t()["org_admin_btn"],
                use_container_width=True,
                on_click=request_org_admin_entry,
            )
        elif show_platform_gear:
            if st.button("⚙️", key="gear_btn", help="Admin Login", use_container_width=True):
                _reset_platform_admin_widget_state()
                st.session_state.show_admin_login = True
                st.rerun()

def render_admin_login_form():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['admin_login_title']}</h2>", unsafe_allow_html=True)
        with st.form("admin_login_form", border=True):
            username = st.text_input(t()["admin_username"], key="admin_username")
            password = st.text_input(t()["admin_password"], type="password", key="admin_password")
            submitted = st.form_submit_button(t()["admin_login_btn"], type="primary", use_container_width=True)
            if submitted:
                if not ADMIN_USERNAME or not ADMIN_PASSWORD:
                    st.error(
                        "平台管理员账号未在 Secrets 中配置（ADMIN_USERNAME / ADMIN_PASSWORD）"
                        if st.session_state.lang == "zh"
                        else "Platform admin credentials are not configured in Secrets."
                    )
                elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state._pending_admin_login = True
                    st.rerun()
                else:
                    st.error(t()["admin_error"])
        if st.button(t()["admin_back"], use_container_width=True):
            st.session_state.show_admin_login = False
            st.rerun()
#-------------
def render_login_form():
    """显示登录表单"""
    # 检查支付成功参数
    query_params = st.query_params
    if "payment_success" in query_params:
        st.success("🎉 支付成功！您已升级为专业版用户")
        st.info("📌 请重新登录")
        st.query_params.clear()
    
    # 登录表单
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center;'>{t()['main_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>{t()['main_subtitle']}</p>", unsafe_allow_html=True)
        
        with st.form("login_form", border=True):
            email = st.text_input(t()["email_placeholder"], key="login_email")
            password = st.text_input(t()["password_placeholder"], type="password", key="login_password")
            submitted = st.form_submit_button(t()["login_btn"], type="primary", use_container_width=True)
            
            if submitted and email and password:
                try:
                    login_email = email.strip()
                    auth_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
                    response = requests.post(
                        auth_url,
                        headers=AUTH_HEADERS,
                        json={"email": login_email, "password": password},
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.authenticated = True
                        st.session_state.user_id = data.get("user", {}).get("id")
                        st.session_state.user_email = login_email
                        st.rerun()
                    else:
                        try:
                            err_body = response.json()
                            err_msg = (
                                err_body.get("error_description")
                                or err_body.get("msg")
                                or err_body.get("message")
                                or "未知错误"
                            )
                        except ValueError:
                            err_msg = response.text or "未知错误"
                        st.error(f"登录失败: {err_msg}")
                except Exception as e:
                    st.error(f"登录失败: {e}")
        
        # 注册和忘记密码按钮
        col_reg, col_forgot = st.columns(2)
        with col_reg:
            if st.button(t()["register_btn"], use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
        with col_forgot:
            if st.button(t()["forgot_password"], use_container_width=True):
                st.session_state.reset_password = True
                st.rerun()

def render_register_form():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['register_title']}</h2>", unsafe_allow_html=True)
        with st.form("register_form", border=True):
            email = st.text_input(t()["email_placeholder"], key="reg_email")
            password = st.text_input(t()["password_placeholder"], type="password", key="reg_password")
            confirm = st.text_input(t()["confirm_password"], type="password", key="reg_confirm")
            submitted = st.form_submit_button(t()["register_submit"], type="primary", use_container_width=True)
            if submitted:
                if not email or not password:
                    st.warning("请填写邮箱和密码" if st.session_state.lang == "zh" else "Please fill in email and password")
                elif password != confirm:
                    st.warning("两次输入的密码不一致" if st.session_state.lang == "zh" else "Passwords do not match")
                elif len(password) < 6:
                    st.warning("密码长度至少6位" if st.session_state.lang == "zh" else "Password must be at least 6 characters")
                else:
                    try:
                        auth_url = f"{SUPABASE_URL}/auth/v1/signup"
                        response = requests.post(auth_url, headers=AUTH_HEADERS, json={"email": email, "password": password})
                        if response.status_code == 200:
                            st.success(t()["register_success"])
                            st.info("👈 " + ("请点击下方返回登录按钮" if st.session_state.lang == "zh" else "Please click the back button below to login"))
                        else:
                            error_msg = response.json().get("msg", "注册失败")
                            if "User already registered" in error_msg:
                                st.error(t()["email_exists"])
                            else:
                                st.error(f"注册失败: {error_msg}" if st.session_state.lang == "zh" else f"Registration failed: {error_msg}")
                    except Exception as e:
                        st.error(f"注册失败: {e}" if st.session_state.lang == "zh" else f"Registration failed: {e}")
        
        if st.button(t()["back_to_login"], use_container_width=True):
            st.session_state.show_register = False
            st.rerun()

def render_reset_password_form():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['forgot_password']}</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            st.info("请联系管理员重置密码")
            st.markdown(f"📧 {t()['contact_email']}")
        if st.button(t()["back_to_login"], use_container_width=True):
            st.session_state.reset_password = False
            st.rerun()

def render_subscription_section(profile, tier, remaining, total_usage):
    col_card1, col_card2, col_card3, col_card4, col_upgrade = st.columns([1, 1, 1, 1, 1.2])

    with col_card1:
        st.metric(t()["subscription"], "💎 Pro" if tier == "pro" else "🔒 Free", border=True)

    with col_card2:
        if tier == "free":
            st.metric(t()["free_trial"], remaining, border=True)
        else:
            st.metric(t()["free_trial"], "∞", border=True)
            expires_at = profile.get("subscription_expires_at")
            if expires_at:
                st.caption(f"📅 {t()['expires_at']}: {expires_at[:10]}")

    with col_card3:
        st.metric(t()["total_usage"], total_usage, border=True)

    with col_card4:
        st.caption("")

    with col_upgrade:
        if tier == "free":
            st.markdown(f"<div style='text-align: center; font-weight: 500; margin-bottom: 8px;'>{t()['upgrade_title']}</div>", unsafe_allow_html=True)

            if st.button(t()["monthly"], key="main_monthly_btn", use_container_width=True):
                spinner_text = "正在创建支付会话..." if st.session_state.lang == "zh" else "Creating payment session..."
                with st.spinner(spinner_text):
                    url, error = create_checkout_session(
                        st.session_state.user_id, st.session_state.user_email,
                        st.secrets["STRIPE_PRICE_MONTHLY"]
                    )
                    if url:
                        st.session_state.payment_url = url
                        st.session_state.payment_type = "monthly"
                        st.rerun()
                    else:
                        error_text = "创建支付会话失败" if st.session_state.lang == "zh" else "Failed to create payment session"
                        st.error(f"{error_text}: {error}")

            if st.button(t()["yearly"], key="main_yearly_btn", use_container_width=True):
                spinner_text = "正在创建支付会话..." if st.session_state.lang == "zh" else "Creating payment session..."
                with st.spinner(spinner_text):
                    url, error = create_checkout_session(
                        st.session_state.user_id, st.session_state.user_email,
                        st.secrets["STRIPE_PRICE_YEARLY"]
                    )
                    if url:
                        st.session_state.payment_url = url
                        st.session_state.payment_type = "yearly"
                        st.rerun()
                    else:
                        error_text = "创建支付会话失败" if st.session_state.lang == "zh" else "Failed to create payment session"
                        st.error(f"{error_text}: {error}")

            if "payment_url" in st.session_state and st.session_state.payment_url:
                if st.session_state.payment_type == "monthly":
                    payment_display = "月付" if st.session_state.lang == "zh" else "Monthly"
                else:
                    payment_display = "年付" if st.session_state.lang == "zh" else "Yearly"
                st.success(f"✅ {payment_display} {t()['payment_created']}")
                button_html = f'''
                <a href="{st.session_state.payment_url}" target="_blank" style="
                    display: block;
                    width: 100%;
                    padding: 0.5rem 0.75rem;
                    background-color: #ff4b4b;
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 0.5rem;
                    font-weight: 500;
                    margin: 0.5rem 0;
                    border: none;
                    cursor: pointer;
                    transition: background-color 0.2s;
                " onmouseover="this.style.backgroundColor='#e04343'" onmouseout="this.style.backgroundColor='#ff4b4b'">
                    {t()["go_to_payment"]}
                </a>
                '''
                st.markdown(button_html, unsafe_allow_html=True)
                st.info(t()["refresh_tip"])
        else:
            st.markdown(f"<div style='text-align: center; font-weight: 500; margin-bottom: 8px;'>{t()['upgrade_title']}</div>", unsafe_allow_html=True)
            st.success("✅ 已是专业版", icon="🎉")


def render_app_navigation(profile, tier, remaining):
    st.markdown(f"### {t()['nav_title']}")
    st.caption(t()["open_new_tab"])

    org_id = profile.get("organization_id")
    if org_id:
        enabled_keys = normalize_enabled_apps(profile.get("enabled_apps"))
    else:
        enabled_keys = list(PORTAL_APP_KEYS)

    lang = st.session_state.lang
    org_name = profile_organization_name(profile, lang=lang)
    org_role = profile.get("org_role")

    for app_key in PORTAL_APP_KEYS:
        if app_key not in enabled_keys:
            continue
        if app_key not in APP_URLS:
            continue
        name = app_display_name(app_key, lang=lang)
        desc = app_description(app_key, lang=lang)
        with st.container(border=True):
            col_name, col_desc, col_btn = st.columns([2, 3, 1])
            with col_name:
                st.markdown(f"**{name}**")
            with col_desc:
                st.caption(desc)
            with col_btn:
                lang_param = "zh" if lang == "zh" else "en"
                full_url = build_app_launch_url(
                    APP_URLS[app_key],
                    st.session_state.user_id,
                    st.session_state.user_email,
                    lang_param,
                    tier,
                    remaining,
                    organization_id=org_id,
                    organization_name=org_name,
                    organization_name_zh=profile.get("organization_name_zh"),
                    organization_name_en=profile.get("organization_name_en"),
                    organization_name_display_mode=profile.get("organization_name_display_mode") or "auto",
                    org_role=org_role,
                )
                button_html = f'''
                <a href="{full_url}" target="_blank" style="
                    display: inline-block;
                    width: 100%;
                    padding: 8px 16px;
                    background-color: #ff4b4b;
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 500;
                    cursor: pointer;
                ">{t()['launch']}</a>
                '''
                st.markdown(button_html, unsafe_allow_html=True)


def render_main_app():
    handle_stripe_callback()

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        profile = safe_get_profile(st.session_state.user_id)
        tier = profile.get("subscription_tier", "free")
        remaining = profile.get("free_trials_remaining", 30)
        total_usage = get_user_total_usage(st.session_state.user_id)
        enterprise = is_enterprise_user(profile)
        org_name = profile_organization_name(profile) if enterprise else None

        if org_name:
            render_enterprise_branding(profile)

        if enterprise:
            st.markdown(
                f"<h3 style='text-align: left; margin:0;'>{t()['welcome']}, {_welcome_display_name(st.session_state.user_email)}</h3>",
                unsafe_allow_html=True,
            )
        else:
            col_welcome, col_refresh = st.columns([11, 1])
            with col_welcome:
                st.markdown(
                    f"<h3 style='text-align: left; margin:0;'>{t()['welcome']}, {_welcome_display_name(st.session_state.user_email)}</h3>",
                    unsafe_allow_html=True,
                )
            with col_refresh:
                if st.button("🔄", key="refresh_btn", help="刷新数据", use_container_width=True):
                    if "payment_url" in st.session_state:
                        del st.session_state.payment_url
                    st.rerun()

        st.markdown("---")

        if not enterprise:
            render_subscription_section(profile, tier, remaining, total_usage)
            st.markdown("---")

        render_app_navigation(profile, tier, remaining)


def render_org_members_tab(profile):
    org_id = profile.get("organization_id")
    max_seats = profile.get("max_seats") or 10
    members = list_org_members(SUPABASE_URL, SERVICE_HEADERS, org_id)
    used = len(members)
    st.metric(t()["seats_used"], f"{used} / {max_seats}")

    if members:
        member_rows = [
            {
                t()["email_col"]: m.get("email"),
                t()["member_role"]: m.get("org_role") or "member",
            }
            for m in members
        ]
        st.table(member_rows)

    with st.form("org_add_member_form", border=True):
        new_email = st.text_input(t()["member_email"], key="org_member_email")
        new_password = st.text_input(t()["initial_password"], type="password", key="org_member_password")
        new_role = st.selectbox(t()["member_role"], ["member", "admin"], key="org_member_role")
        submitted = st.form_submit_button(t()["add_member"], type="primary", use_container_width=True)
        if submitted:
            if not new_email or not new_password:
                st.warning("请填写邮箱和密码" if st.session_state.lang == "zh" else "Email and password required")
            elif len(new_password) < 6:
                st.warning("密码至少6位" if st.session_state.lang == "zh" else "Password must be at least 6 characters")
            else:
                ok, reason = add_org_member(
                    SUPABASE_URL,
                    SERVICE_HEADERS,
                    org_id,
                    new_email.strip(),
                    new_password,
                    org_role=new_role,
                    max_seats=max_seats,
                )
                if ok:
                    st.success(t()["member_added"])
                    st.rerun()
                elif reason == "seat_limit":
                    st.error(t()["seat_limit_reached"])
                else:
                    st.error("添加失败" if st.session_state.lang == "zh" else "Failed to add member")

    if members:
        removable = [m for m in members if m.get("id") != st.session_state.user_id]
        if removable:
            options = [f"{m.get('email')} ({m.get('org_role')})" for m in removable]
            if st.session_state.get("org_remove_select") not in options:
                st.session_state.pop("org_remove_select", None)
            selected = st.selectbox(t()["remove_member"], options, key="org_remove_select")
            if st.button(t()["remove_member"], key="org_remove_btn", use_container_width=True):
                email = selected.split(" ")[0]
                target = next((m for m in removable if m.get("email") == email), None)
                if target and remove_org_member(SUPABASE_URL, SERVICE_HEADERS, target.get("id")):
                    st.success(t()["member_removed"])
                    st.rerun()


def render_tenant_kb_panel(
    org_id: str,
    org_name: str,
    *,
    widget_keys: Optional[Dict[str, str]] = None,
    include_excel_upload: bool = True,
    uploaded_excel=None,
):
    """Shared tenant knowledge base UI for org admins and platform admins."""
    keys = {
        "template_btn": "kb_download_template_btn",
        "export_btn": "kb_download_export_btn",
        "uploader": "kb_excel_uploader",
        "replace": "kb_replace_on_import",
        "import_btn": "kb_import_btn",
        "delete_select": "org_kb_delete_select",
        "delete_btn": "org_kb_delete_btn",
        "add_form": "org_kb_add_form",
        "add_category": "org_kb_add_category",
        "add_content": "org_kb_add_content",
    }
    if widget_keys:
        keys.update(widget_keys)

    entries = list_tenant_knowledge(SUPABASE_URL, SERVICE_HEADERS, org_id)

    st.markdown(f"### {t()['kb_db_title'].format(org_name=org_name)}")
    st.caption(t()["kb_excel_hint"])

    lang = st.session_state.lang
    safe_org = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in org_name)
    template_name = f"{safe_org}_knowledge_template.xlsx"
    export_name = f"{safe_org}_knowledge_export.xlsx"

    col_tpl, col_export = st.columns(2)
    try:
        template_bytes = build_kb_template_excel(org_name, lang)
        export_bytes = build_kb_export_excel(entries, org_name, lang)
    except Exception as exc:
        st.error("知识库 Excel 生成失败" if st.session_state.lang == "zh" else "Failed to build knowledge base Excel")
        st.caption(str(exc))
        template_bytes = b""
        export_bytes = b""

    with col_tpl:
        st.download_button(
            t()["kb_download_template"],
            data=template_bytes,
            file_name=template_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=keys["template_btn"],
        )
    with col_export:
        st.download_button(
            t()["kb_download_data"],
            data=export_bytes,
            file_name=export_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=keys["export_btn"],
        )

    if include_excel_upload:
        uploaded_excel = st.file_uploader(
            t()["kb_upload_excel"],
            type=["xlsx"],
            key=keys["uploader"],
        )
    replace_existing = st.checkbox(t()["kb_replace_on_import"], key=keys["replace"])
    if st.button(t()["kb_import_btn"], key=keys["import_btn"], type="primary", use_container_width=True):
        if not uploaded_excel:
            st.warning(t()["kb_upload_excel"])
        else:
            to_en, to_zh = _kb_translators()
            imported, reason = import_tenant_knowledge_excel(
                SUPABASE_URL,
                SERVICE_HEADERS,
                org_id,
                uploaded_excel.getvalue(),
                replace_existing=replace_existing,
                translate_to_en=to_en,
                translate_to_zh=to_zh,
            )
            if reason == "ok":
                st.success(t()["kb_imported"].format(count=imported))
                st.rerun()
            elif reason == "missing_columns":
                st.error(t()["kb_missing_columns"])
            elif reason == "no_valid_rows":
                st.error(t()["kb_no_valid_rows"])
            elif reason.startswith("invalid_excel"):
                st.error(t()["kb_invalid_excel"])
            else:
                st.error(f"{t()['kb_import_failed']}: {reason}")

    st.markdown("---")

    if entries:
        kb_rows = [
            {
                "ID": e.get("id"),
                t()["kb_category"]: e.get("category"),
                t()["kb_content"]: (e.get("content") or "")[:120],
            }
            for e in entries
        ]
        st.table(kb_rows)

        delete_options = [
            f"#{e.get('id')} [{e.get('category')}] {(e.get('content') or '')[:40]}"
            for e in entries
        ]
        if st.session_state.get(keys["delete_select"]) not in delete_options:
            st.session_state.pop(keys["delete_select"], None)
        del_sel = st.selectbox(t()["kb_delete"], delete_options, key=keys["delete_select"])
        if st.button(t()["kb_delete"], key=keys["delete_btn"], use_container_width=True):
            record_id = int(del_sel.split("]")[0].replace("#", "").strip())
            if delete_tenant_knowledge(SUPABASE_URL, SERVICE_HEADERS, record_id, org_id):
                st.success("已删除" if st.session_state.lang == "zh" else "Deleted")
                st.rerun()

    with st.form(keys["add_form"], border=True):
        category = st.selectbox(
            t()["kb_category"],
            KNOWLEDGE_CATEGORIES,
            key=keys["add_category"],
        )
        content = st.text_area(t()["kb_content"], key=keys["add_content"])
        submitted = st.form_submit_button(t()["kb_add"], type="primary", use_container_width=True)
        if submitted and content.strip():
            to_en, to_zh = _kb_translators()
            zh_text, en_text = bilingualize_kb_content(
                content.strip(),
                translate_to_en=to_en,
                translate_to_zh=to_zh,
            )
            if add_tenant_knowledge(
                SUPABASE_URL,
                SERVICE_HEADERS,
                org_id,
                category,
                zh_text,
                content_en=en_text,
            ):
                st.success("已添加" if st.session_state.lang == "zh" else "Added")
                st.rerun()


def _render_persisted_file_uploaders(active_section: str, *, scope: str) -> Dict[str, object]:
    """Keep file uploaders mounted across admin tab switches to avoid native segfaults."""
    uploads: Dict[str, object] = {}
    kb_disabled = active_section != "kb"
    settings_disabled = active_section != "settings"
    if scope == "org":
        uploads["kb_excel"] = st.file_uploader(
            t()["kb_upload_excel"],
            type=["xlsx"],
            key="kb_excel_uploader",
            disabled=kb_disabled,
            label_visibility="collapsed" if kb_disabled else "visible",
        )
        uploads["logo"] = st.file_uploader(
            t()["upload_logo"],
            type=["png", "jpg", "jpeg", "webp"],
            key="org_admin_logo_uploader",
            disabled=settings_disabled,
            label_visibility="collapsed" if settings_disabled else "visible",
        )
    else:
        uploads["kb_excel"] = st.file_uploader(
            t()["kb_upload_excel"],
            type=["xlsx"],
            key="platform_kb_excel_uploader",
            disabled=kb_disabled,
            label_visibility="collapsed" if kb_disabled else "visible",
        )
    return uploads


def render_org_kb_tab(profile, *, include_excel_upload: bool = True, uploaded_excel=None):
    org_id = profile.get("organization_id")
    org_name = profile_organization_name(profile) or t()["enterprise_plan"]
    if not org_id:
        st.warning("未找到企业信息" if st.session_state.lang == "zh" else "Organization not found")
        return
    render_tenant_kb_panel(
        org_id,
        org_name,
        include_excel_upload=include_excel_upload,
        uploaded_excel=uploaded_excel,
    )


def render_org_settings_tab(profile, *, include_uploader: bool = True, uploaded=None):
    expires_text = format_contract_expires(
        profile.get("contract_expires_at"),
        fallback=t()["contract_expires_unset"],
    )
    st.metric(t()["license_expire"], expires_text)
    st.markdown("---")
    st.subheader(t()["org_name"])
    org_id = profile.get("organization_id")
    org_record = {
        "name_zh": profile.get("organization_name_zh") or profile.get("organization_name_legacy"),
        "name_en": profile.get("organization_name_en"),
        "name": profile.get("organization_name_legacy"),
        "name_display_mode": profile.get("organization_name_display_mode") or "auto",
    }
    render_organization_names_editor(org_id, org_record, "org_admin")
    st.markdown("---")
    render_org_logo_section(
        profile.get("organization_id"),
        profile.get("organization_logo_url"),
        "org_admin",
        include_uploader=include_uploader,
        uploaded=uploaded,
    )


def render_org_admin_panel():
    profile = safe_get_profile(st.session_state.user_id)
    if not is_org_admin(profile):
        request_org_admin_exit()
        st.rerun()
        return

    org_name = profile_organization_name(profile) or t()["enterprise_plan"]
    st.markdown(f"## ⚙️ {t()['org_admin_panel']} — {org_name}")

    section_labels = {
        "members": t()["members_tab"],
        "kb": t()["kb_tab"],
        "settings": t()["settings_tab"],
    }
    selected_section = st.session_state.get("org_admin_section", "members")
    if selected_section not in section_labels:
        selected_section = "members"
        st.session_state.org_admin_section = "members"

    _render_admin_tab_buttons(section_labels, selected_section, "org", request_org_admin_section_switch)
    org_uploads = _render_persisted_file_uploaders(selected_section, scope="org")
    _render_hidden_expander_tab_css()
    with st.expander(section_labels["members"], expanded=(selected_section == "members")):
        render_org_members_tab(profile)
    with st.expander(section_labels["kb"], expanded=(selected_section == "kb")):
        render_org_kb_tab(
            profile,
            include_excel_upload=False,
            uploaded_excel=org_uploads.get("kb_excel"),
        )
    with st.expander(section_labels["settings"], expanded=(selected_section == "settings")):
        render_org_settings_tab(
            profile,
            include_uploader=False,
            uploaded=org_uploads.get("logo"),
        )

    st.markdown("---")
    st.button(
        t()["exit_org_admin"],
        use_container_width=True,
        key="org_admin_exit",
        on_click=request_org_admin_exit,
    )


def render_platform_org_kb_section(*, include_excel_upload: bool = True, uploaded_excel=None):
    orgs = list_organizations(SUPABASE_URL, SERVICE_HEADERS)
    if not orgs:
        st.info(t()["platform_no_orgs_kb"])
        return

    org_lookup = {org.get("id"): org for org in orgs if org.get("id")}
    org_ids = list(org_lookup.keys())
    if not org_ids:
        st.info(t()["platform_no_orgs_kb"])
        return

    if st.session_state.get("platform_kb_org_id") not in org_ids:
        st.session_state.pop("platform_kb_org_id", None)

    def _org_kb_label(oid: str) -> str:
        org = org_lookup.get(oid, {})
        short_id = (oid or "")[:8]
        display_name = organization_display_name(org=org, lang=st.session_state.lang)
        return f"{display_name or '-'} | {short_id}"

    selected_org_id = st.selectbox(
        t()["select_org"],
        org_ids,
        format_func=_org_kb_label,
        key="platform_kb_org_id",
    )
    selected_org = org_lookup.get(selected_org_id, {})
    org_name = organization_display_name(org=selected_org, lang=st.session_state.lang) or t()["enterprise_plan"]
    render_tenant_kb_panel(
        selected_org_id,
        org_name,
        include_excel_upload=include_excel_upload,
        uploaded_excel=uploaded_excel,
        widget_keys={
            "template_btn": "platform_kb_download_template_btn",
            "export_btn": "platform_kb_download_export_btn",
            "uploader": "platform_kb_excel_uploader",
            "replace": "platform_kb_replace_on_import",
            "import_btn": "platform_kb_import_btn",
            "delete_select": "platform_kb_delete_select",
            "delete_btn": "platform_kb_delete_btn",
            "add_form": "platform_kb_add_form",
        },
    )


def render_platform_enterprise_section(users):
    try:
        orgs = list_organizations(SUPABASE_URL, SERVICE_HEADERS)
        if not orgs and st.session_state.lang == "zh":
            st.caption(t()["migration_hint"])

        st.subheader(t()["create_org"])
        with st.form("platform_create_org", border=True):
            col_name_zh, col_name_en = st.columns(2)
            with col_name_zh:
                create_name_zh = st.text_input(t()["org_name_zh"])
            with col_name_en:
                create_name_en = st.text_input(t()["org_name_en"])
            max_seats = st.number_input(t()["max_seats"], min_value=1, max_value=500, value=10)
            contract_years = st.number_input(
                t()["contract_years"],
                min_value=1,
                max_value=10,
                value=DEFAULT_CONTRACT_YEARS,
            )
            submitted = st.form_submit_button(t()["create_org"], type="primary", use_container_width=True)
            if submitted:
                if not (create_name_zh.strip() or create_name_en.strip()):
                    st.warning(t()["org_name_required"])
                else:
                    created = create_organization(
                        SUPABASE_URL,
                        SERVICE_HEADERS,
                        int(max_seats),
                        name_zh=create_name_zh,
                        name_en=create_name_en,
                        contract_years=int(contract_years),
                    )
                    if created:
                        st.session_state.pending_delete_org_id = None
                        st.success(t()["org_created"])
                        st.rerun()

        if not orgs:
            return

        org_rows = []
        org_lookup = {}
        for org in orgs:
            org_id = org.get("id")
            member_count = count_org_members(SUPABASE_URL, SERVICE_HEADERS, org_id)
            org_lookup[org_id] = {**org, "member_count": member_count}
            enabled_count = len(org_enabled_apps(org))
            org_rows.append({
                t()["org_name_zh"]: (org.get("name_zh") or org.get("name") or "-"),
                t()["org_name_en"]: org.get("name_en") or "-",
                t()["contract_expires_col"]: format_contract_expires(
                    org.get("contract_expires_at"),
                    fallback=t()["contract_expires_unset"],
                ),
                t()["max_seats"]: org.get("max_seats"),
                t()["seats_used"]: member_count,
                t()["org_apps_col"]: f"{enabled_count}/{len(PORTAL_APP_KEYS)}",
                "ID": org_id,
            })

        col_header, col_del = st.columns([5, 1])
        with col_header:
            st.subheader(t()["org_list"])
        with col_del:
            minus_clicked = st.button(
                t()["delete_minus"],
                key="org_minus_btn",
                type="primary",
                use_container_width=True,
                help=t()["delete_minus_help"],
            )

        st.caption(t()["selected_org_hint"])
        org_ids = [org.get("id") for org in orgs if org.get("id")]
        if not org_ids:
            return

        if st.session_state.get("platform_selected_org_id") not in org_ids:
            st.session_state.platform_selected_org_id = org_ids[0]
        pending_id = st.session_state.get("pending_delete_org_id")
        if pending_id and pending_id not in org_ids:
            st.session_state.pending_delete_org_id = None

        def _org_option_label(oid: str) -> str:
            item = org_lookup.get(oid, {})
            short_id = (oid or "")[:8]
            expires_label = format_contract_expires(
                item.get("contract_expires_at"),
                fallback=t()["contract_expires_unset"],
            )
            display_name = organization_display_name(org=item, lang=st.session_state.lang)
            return (
                f"{display_name or '-'} | {t()['contract_expires_col']}: {expires_label} | "
                f"{item.get('member_count', 0)}/{item.get('max_seats', 0)} | {short_id}"
            )

        selected_org_id = st.selectbox(
            t()["select_org"],
            org_ids,
            format_func=_org_option_label,
            key="platform_selected_org_id",
        )
        st.dataframe(org_rows, use_container_width=True, hide_index=True)

        selected_org = org_lookup.get(selected_org_id, {})

        st.markdown("---")
        st.subheader(t()["org_name"])
        render_organization_names_editor(selected_org_id, selected_org, "platform")

        if minus_clicked and selected_org_id:
            st.session_state.pending_delete_org_id = selected_org_id

        pending_id = st.session_state.get("pending_delete_org_id")
        if pending_id and pending_id in org_lookup:
            pending_name = organization_display_name(org=org_lookup[pending_id], lang=st.session_state.lang) or pending_id
            st.warning(f"{t()['pending_delete']}: {pending_name}")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button(t()["confirm_delete_save"], key="confirm_delete_org_btn", type="primary", use_container_width=True):
                    ok, reason = delete_organization(SUPABASE_URL, SERVICE_HEADERS, pending_id)
                    if ok:
                        st.session_state.pending_delete_org_id = None
                        st.success(t()["org_deleted"])
                        st.rerun()
                    else:
                        st.error(
                            f"删除失败: {reason}"
                            if st.session_state.lang == "zh"
                            else f"Delete failed: {reason}"
                        )
            with col_cancel:
                if st.button(t()["cancel"], key="cancel_delete_org_btn", use_container_width=True):
                    st.session_state.pending_delete_org_id = None
                    st.rerun()
        elif pending_id:
            st.session_state.pending_delete_org_id = None

        st.markdown("---")
        col_seats, col_expires = st.columns(2)
        with col_seats:
            new_max = st.number_input(
                t()["max_seats"],
                min_value=1,
                max_value=500,
                value=int(selected_org.get("max_seats") or 10),
                key="platform_org_max_seats",
            )
        with col_expires:
            default_contract_date = parse_contract_expires_date(selected_org.get("contract_expires_at"))
            if default_contract_date is None:
                default_contract_date = contract_expires_after_years(DEFAULT_CONTRACT_YEARS)
                default_contract_date = parse_contract_expires_date(default_contract_date) or (
                    date.today() + timedelta(days=365)
                )
            if st.session_state.get("_platform_contract_org_id") != selected_org_id:
                st.session_state._platform_contract_org_id = selected_org_id
                st.session_state["platform_org_contract_expires"] = default_contract_date
            new_expires = st.date_input(
                t()["contract_expires"],
                key="platform_org_contract_expires",
            )
        if st.button(t()["update_btn"], key="platform_update_org_btn", use_container_width=True):
            if update_organization(
                SUPABASE_URL,
                SERVICE_HEADERS,
                selected_org_id,
                {
                    "max_seats": int(new_max),
                    "contract_expires_at": contract_expires_at_from_date(new_expires),
                },
            ):
                st.success(t()["org_updated"])
                st.rerun()

        st.markdown("---")
        st.subheader(t()["org_apps_title"])
        st.caption(t()["org_apps_hint"])
        current_apps = org_enabled_apps(selected_org)
        if st.session_state.get("_platform_apps_org_id") != selected_org_id:
            st.session_state._platform_apps_org_id = selected_org_id
            st.session_state["platform_org_enabled_apps"] = current_apps
        selected_apps = st.multiselect(
            t()["org_apps_select"],
            options=list(PORTAL_APP_KEYS),
            format_func=lambda key: app_display_name(key, lang=st.session_state.lang),
            key="platform_org_enabled_apps",
        )
        if st.button(t()["org_apps_save"], key="platform_org_apps_save_btn", use_container_width=True, type="primary"):
            if not selected_apps:
                st.warning(t()["org_apps_required"])
            else:
                ok, detail = set_organization_enabled_apps(
                    SUPABASE_URL,
                    SERVICE_HEADERS,
                    selected_org_id,
                    selected_apps,
                )
                if ok:
                    st.success(t()["org_apps_saved"])
                    st.rerun()
                elif detail == "missing_column":
                    st.error(t()["org_apps_migration_hint"])
                else:
                    st.error(detail or t()["org_apps_migration_hint"])

        st.markdown("---")
        render_org_logo_section(
            selected_org_id,
            selected_org.get("logo_url"),
            "platform",
        )

        st.markdown("---")
        st.subheader(t()["assign_user_org"])
        with st.form("platform_assign_user_form", border=True):
            assign_email = st.text_input(t()["member_email"], key="platform_assign_email")
            assign_password = st.text_input(t()["initial_password"], type="password", key="platform_assign_password")
            st.caption(t()["login_email_hint"])
            assign_role = st.selectbox(
                t()["member_role"],
                ["admin", "member"],
                index=0,
                key="platform_assign_role_email",
            )
            st.caption(_org_option_label(selected_org_id))
            submitted = st.form_submit_button(t()["assign_user_btn"], type="primary", use_container_width=True)
            if submitted:
                if not assign_email.strip():
                    st.warning("请输入邮箱" if st.session_state.lang == "zh" else "Please enter an email")
                elif len(assign_password or "") < 6:
                    st.warning(t()["password_required"])
                else:
                    ok, reason = assign_or_provision_org_user(
                        SUPABASE_URL,
                        SERVICE_HEADERS,
                        assign_email.strip(),
                        assign_password,
                        selected_org_id,
                        assign_role,
                        max_seats=int(selected_org.get("max_seats") or 10),
                    )
                    if ok:
                        verified, verify_detail = verify_login_credentials(
                            SUPABASE_URL,
                            SUPABASE_ANON_KEY,
                            assign_email.strip(),
                            assign_password,
                        )
                        if verified:
                            st.success(f"{t()['user_assigned']} — {t()['login_verify_ok']}")
                        else:
                            st.warning(f"{t()['login_verify_failed']}: {verify_detail}")
                        st.rerun()
                    elif reason == "seat_limit":
                        st.error(t()["seat_limit_reached"])
                    elif reason == "password_required":
                        st.warning(t()["password_required"])
                    elif reason == "password_reset_failed":
                        st.error(t()["password_reset_failed"])
                    elif reason == "auth_failed":
                        st.error("创建账号失败" if st.session_state.lang == "zh" else "Failed to create account")
                    else:
                        st.error(
                            f"绑定失败: {reason}"
                            if st.session_state.lang == "zh"
                            else f"Assignment failed: {reason}"
                        )

        with st.form("platform_remove_email_form", border=True):
            remove_email = st.text_input(t()["member_email"], key="platform_remove_email")
            submitted_remove = st.form_submit_button(t()["remove_from_org"], use_container_width=True)
            if submitted_remove and remove_email.strip():
                user_id = find_user_id_by_email(SUPABASE_URL, SERVICE_HEADERS, remove_email.strip())
                if user_id and assign_user_to_org(
                    SUPABASE_URL, SERVICE_HEADERS, user_id, None, None, make_enterprise=False,
                ):
                    st.success(t()["user_assigned"])
                    st.rerun()
                elif not user_id:
                    st.error(t()["user_not_found"])
    except Exception as exc:
        st.error("企业管理操作失败" if st.session_state.lang == "zh" else "Organization management failed")
        st.exception(exc)


def render_admin_user_section(users, auth_users):
    writable, key_kind = _service_key_looks_writable()
    if not writable:
        st.error(
            f"无法写入 profiles：当前 SUPABASE_SERVICE_ROLE_KEY 识别为 **{key_kind}**。"
            "请到 Streamlit Cloud → Settings → Secrets，改成 Supabase 的 **service_role**（或 sb_secret_）密钥，"
            "不要使用 anon / publishable。"
            if st.session_state.lang == "zh"
            else f"Cannot write profiles: SUPABASE_SERVICE_ROLE_KEY looks like **{key_kind}**. "
            "Use the Supabase service_role / sb_secret_ key in Streamlit Secrets, not anon/publishable."
        )

    pro_users = [u for u in users if u.get("subscription_tier") == "pro"]
    enterprise_users = [u for u in users if u.get("subscription_tier") == "enterprise"]
    confirmed_count = sum(1 for u in users if auth_users.get(u.get("id"), {}).get("email_confirmed_at"))

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(t()["total_users"], len(users))
    with col2: st.metric("已确认邮箱", confirmed_count)
    with col3: st.metric(t()["pro_users"], len(pro_users))
    with col4: st.metric(t()["free_users"], len(users) - len(pro_users) - len(enterprise_users))

    st.markdown("---")
    st.subheader(t()["user_list"])

    if users:
        user_data = []
        for user in users:
            ai = auth_users.get(user.get("id"), {})
            tier = user.get("subscription_tier", "free")
            if tier == "pro":
                tier_label = "💎 Pro"
            elif tier == "enterprise":
                tier_label = "🏢 Enterprise"
            else:
                tier_label = "🔒 Free"
            user_data.append({
                t()["email_col"]: user.get("email"),
                "邮箱确认": "✅" if ai.get("email_confirmed_at") else "❌",
                t()["subscription_col"]: tier_label,
                "剩余次数": _trials_display(user.get("free_trials_remaining")),
                "注册时间": _safe_date_prefix(ai.get("created_at")),
                "最后登录": _safe_date_prefix(ai.get("last_sign_in_at")),
                "到期时间": _safe_date_prefix(user.get("subscription_expires_at")),
            })
        st.dataframe(user_data, use_container_width=True, height=400)
    else:
        st.info("暂无用户数据")

    st.markdown("---")
    st.subheader(t()["subscription_mgmt"])

    if users:
        search_email = st.text_input(
            t()["search_user_email"],
            key="admin_user_search",
            placeholder="mabelwong926@gmail.com",
        ).strip().lower()
        filtered_users = users
        if search_email:
            filtered_users = [
                u for u in users
                if search_email in str(u.get("email") or "").lower()
            ]
            if not filtered_users:
                st.warning(t()["user_not_found"])

        user_lookup = {
            str(u.get("id")): u
            for u in filtered_users
            if u.get("id")
        }
        user_ids = list(user_lookup.keys())

        # Drop stale selectbox state that belongs to an older options list / key.
        st.session_state.pop("admin_select_user", None)
        if st.session_state.get("admin_select_user_id") not in user_ids:
            st.session_state.pop("admin_select_user_id", None)

        if not user_ids:
            st.info("暂无可选用户" if st.session_state.lang == "zh" else "No users to select")
            selected_user = None
            selected_email = None
        else:
            def _admin_user_label(uid: str) -> str:
                item = user_lookup.get(uid, {})
                email = (item.get("email") or uid).strip()
                tier = item.get("subscription_tier") or "free"
                return f"{email} ({tier})"

            selected_user_id = st.selectbox(
                t()["select_user"],
                user_ids,
                format_func=_admin_user_label,
                key="admin_select_user_id",
            )
            selected_user = user_lookup.get(selected_user_id)
            selected_email = (selected_user or {}).get("email") or ""
            st.markdown(f"**{t()['current_user']}:** `{selected_email}`")

        if selected_user:
            selected_user_id = str(selected_user.get("id"))
            if st.session_state.get("_admin_tier_user") != selected_user_id:
                st.session_state._admin_tier_user = selected_user_id
                st.session_state.pop("admin_new_tier", None)
                st.session_state.pop("admin_new_trials", None)
                st.session_state.pop("admin_months", None)
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                tier_choices = ["free", "pro", "enterprise"]
                current_tier = selected_user.get("subscription_tier", "free")
                tier_index = tier_choices.index(current_tier) if current_tier in tier_choices else 0
                new_tier = st.selectbox(
                    t()["set_subscription"], tier_choices,
                    index=tier_index, key="admin_new_tier",
                )
            with col_s2:
                current_trials = _trials_display(selected_user.get("free_trials_remaining"))
                new_trials = st.number_input(
                    t()["set_trials"], min_value=0, max_value=999,
                    value=int(current_trials), key="admin_new_trials",
                )
            with col_s3:
                admin_months = st.number_input(
                    "Pro 月数" if st.session_state.lang == "zh" else "Pro months",
                    min_value=1, max_value=12, value=1, key="admin_months",
                    disabled=new_tier != "pro",
                )

            if new_tier in ("pro", "enterprise"):
                st.caption(
                    "提示：Pro / Enterprise 用户不消耗免费次数；若要按次数计费，请改回 free。"
                    if st.session_state.lang == "zh"
                    else "Note: Pro / Enterprise users do not consume free trials. Switch to free to use trial counts."
                )

            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button(t()["update_btn"], use_container_width=True, key="admin_update_btn", type="primary"):
                    update_data = {"subscription_tier": new_tier, "free_trials_remaining": int(new_trials)}
                    if new_tier == "pro":
                        update_data["subscription_expires_at"] = (
                            datetime.now() + timedelta(days=30 * int(admin_months))
                        ).isoformat()
                    else:
                        update_data["subscription_expires_at"] = None
                    ok, detail = supabase_patch_ok(
                        "profiles",
                        selected_user.get("id"),
                        update_data,
                        email=selected_email,
                    )
                    if ok:
                        st.session_state.pop("admin_new_trials", None)
                        st.session_state.pop("admin_new_tier", None)
                        st.success(f"已更新 {selected_email}")
                        st.rerun()
                    else:
                        st.error(f"更新失败: {detail}")
            with col_b2:
                if st.button(t()["reset_trials_btn"], use_container_width=True, key="admin_reset_trials_btn"):
                    ok, detail = supabase_patch_ok(
                        "profiles",
                        selected_user.get("id"),
                        {"free_trials_remaining": DEFAULT_FREE_TRIALS},
                        email=selected_email,
                    )
                    if ok:
                        st.session_state.pop("admin_new_trials", None)
                        st.success(t()["reset_trials_ok"].format(email=selected_email))
                        st.rerun()
                    else:
                        st.error(f"更新失败: {detail}")
            with col_b3:
                if st.button("📧 发送密码重置邮件", use_container_width=True, key="admin_reset_pwd"):
                    try:
                        reset_data = {"email": selected_email}
                        reset_response = requests.post(
                            f"{SUPABASE_URL}/auth/v1/recover",
                            headers=AUTH_HEADERS,
                            json=reset_data,
                        )
                        if reset_response.status_code == 200:
                            st.success(f"✅ 密码重置邮件已发送至 {selected_email}")
                        else:
                            st.error(f"发送失败: {reset_response.text}")
                    except Exception as e:
                        st.error(f"发送失败: {e}")

    st.markdown("---")
    if st.button(t()["reset_all_trials"], use_container_width=True, key="admin_reset_all"):
        users_resp = supabase_get("profiles", limit=5000)
        if users_resp.status_code in (200, 206):
            reset_count = 0
            for user in users_resp.json():
                # Only personal free users use trial counts
                if user.get("subscription_tier") == "free" and not user.get("organization_id"):
                    ok, detail = supabase_patch_ok(
                        "profiles",
                        user.get("id"),
                        {"free_trials_remaining": DEFAULT_FREE_TRIALS},
                        email=user.get("email") or "",
                    )
                    if ok:
                        reset_count += 1
            st.success(
                f"已重置 {reset_count} 个免费用户次数为 {DEFAULT_FREE_TRIALS}"
                if st.session_state.lang == "zh"
                else f"Reset trials to {DEFAULT_FREE_TRIALS} for {reset_count} free users"
            )
            st.rerun()
        else:
            st.error(f"读取用户失败: {users_resp.text}")


def render_admin_panel():
    st.markdown(f"## ⚙️ {t()['admin_panel']}")
    try:
        response = supabase_get("profiles", limit=5000)
        raw_users = response.json() if response.status_code in (200, 206) else []
        users = raw_users if isinstance(raw_users, list) else []

        auth_users = {}
        try:
            auth_response = requests.get(
                f"{SUPABASE_URL}/auth/v1/admin/users",
                headers=SERVICE_HEADERS,
                params={"page": 1, "per_page": 200},
                timeout=15,
            )
            if auth_response.status_code == 200:
                data = auth_response.json()
                for u in _parse_auth_users(data):
                    if u.get("id"):
                        auth_users[u.get("id")] = {
                            "created_at": u.get("created_at", ""),
                            "last_sign_in_at": u.get("last_sign_in_at", ""),
                            "email_confirmed_at": u.get("email_confirmed_at", ""),
                        }
        except Exception as e:
            st.warning(f"获取用户详细信息失败: {e}")

        section_labels = {
            "users": t()["user_mgmt_tab"],
            "orgs": t()["org_mgmt"],
            "kb": t()["platform_kb_tab"],
        }
        selected_section = st.session_state.get("platform_admin_section", "users")
        if selected_section not in section_labels:
            selected_section = "users"
            st.session_state.platform_admin_section = "users"

        _render_admin_tab_buttons(
            section_labels,
            selected_section,
            "platform",
            request_platform_admin_section_switch,
        )
        platform_uploads = _render_persisted_file_uploaders(selected_section, scope="platform")
        _render_hidden_expander_tab_css()
        with st.expander(section_labels["users"], expanded=(selected_section == "users")):
            try:
                render_admin_user_section(users, auth_users)
            except Exception as exc:
                st.error("用户管理加载失败" if st.session_state.lang == "zh" else "Failed to load user management")
                st.exception(exc)
        with st.expander(section_labels["orgs"], expanded=(selected_section == "orgs")):
            try:
                render_platform_enterprise_section(users)
            except Exception as exc:
                st.error("企业管理加载失败" if st.session_state.lang == "zh" else "Failed to load organization management")
                st.exception(exc)
        with st.expander(section_labels["kb"], expanded=(selected_section == "kb")):
            try:
                render_platform_org_kb_section(
                    include_excel_upload=False,
                    uploaded_excel=platform_uploads.get("kb_excel"),
                )
            except Exception as exc:
                st.error("企业知识库加载失败" if st.session_state.lang == "zh" else "Failed to load organization knowledge bases")
                st.exception(exc)

    except Exception as e:
        st.warning(f"无法获取数据: {e}")
        st.exception(e)
    
    st.markdown("---")
    st.button(
        t()["exit_admin"],
        use_container_width=True,
        key="admin_exit",
        on_click=request_guest_reset,
    )

def main():
    try:
        inject_mobile_home_screen_meta()
        apply_pending_guest_reset()
        apply_pending_admin_login()
        _scrub_admin_url_query_params()
        apply_pending_org_admin_entry()
        apply_pending_org_admin_exit()
        if not st.session_state.get("authenticated"):
            st.session_state.admin_mode = False
            st.session_state.org_admin_mode = False
        if st.session_state.pop("_password_changed_flash", False):
            st.success(t()["password_changed"])
        render_sidebar()
        render_top_buttons()
        if st.session_state.get("show_admin_login", False):
            render_admin_login_form()
        elif not st.session_state.authenticated:
            if st.session_state.get("show_register", False):
                render_register_form()
            elif st.session_state.get("reset_password", False):
                render_reset_password_form()
            else:
                render_login_form()
        else:
            if st.session_state.get("admin_mode", False):
                render_admin_panel()
            elif st.session_state.get("org_admin_mode", False):
                render_org_admin_panel()
            else:
                render_main_app()
    except Exception as exc:
        lang = st.session_state.get("lang", "zh")
        st.error("应用运行出错，请稍后重试或联系管理员。" if lang == "zh" else "App error. Please retry or contact support.")
        st.exception(exc)

if __name__ == "__main__":
    main()
