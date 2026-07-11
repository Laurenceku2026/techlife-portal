import streamlit as st
import requests
import stripe
from datetime import datetime, timedelta

from portal_auth import build_app_launch_url
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
    set_organization_logo,
    update_organization,
    verify_login_credentials,
    _parse_auth_users,
)

# ==================== 页面配置 ====================
st.set_page_config(page_title="TechLife Suite", page_icon="🔧", layout="wide")

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


def _kb_translators():
    return make_kb_translators(
        _get_secret("DEEPSEEK_API_KEY"),
        _get_secret("DEEPSEEK_BASE_URL") or "https://api.deepseek.com",
        _get_secret("DEEPSEEK_MODEL") or "deepseek-chat",
    )


def supabase_get(table: str, user_id: str = None, id_field: str = "id"):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if user_id:
        url += f"?{id_field}=eq.{user_id}"
    response = requests.get(url, headers=SERVICE_HEADERS)
    return response

def supabase_patch(table: str, user_id: str, data: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{user_id}"
    response = requests.patch(url, headers=SERVICE_HEADERS, json=data)
    return response

# ==================== 多语言配置 ====================
TEXTS = {
    "zh": {
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 关于系统",
        "about_text": """
**TechLife Suite** 是专为研发工程师打造的 **AI 赋能 DFSS（六西格玛设计）** 平台。

我们致力于通过人工智能技术，简化复杂的工程设计流程，帮助团队实现：

- **智能需求分析**：快速拆解客户之声 (VOC)。
- **自动化风险评估**：AI 辅助生成 DFMEA。
- **参数优化设计**：利用算法寻找最优容差。

让 AI 成为您的首席质量工程师。
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
        "exit_admin": "退出管理员模式",
        "email_col": "邮箱",
        "subscription_col": "订阅",
        "trials_left": "剩余次数",
        "total_used": "总使用次数",
        "reset_all_trials": "重置所有用户免费次数",
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
        "max_seats": "席位上限",
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
        "seat_limit_reached": "已达席位上限",
        "member_added": "成员已添加",
        "member_removed": "成员已移出企业",
        "org_created": "企业已创建",
        "org_updated": "企业已更新",
        "user_assigned": "用户已绑定",
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
        "settings_tab": "企业设置",
    },
    "en": {
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 About System",
        "about_text": """
**TechLife Suite** is an **AI-empowered DFSS (Design for Six Sigma)** platform for R&D engineers.

We are committed to simplifying complex engineering design processes through AI technology, helping teams achieve:

- **Intelligent Requirement Analysis**: Decompose Voice of Customer (VOC).
- **Automated Risk Assessment**: AI-assisted DFMEA generation.
- **Parameter Optimization**: Algorithm-driven tolerance search.

Let AI become your Chief Quality Engineer.
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
        "exit_admin": "Exit Admin Mode",
        "email_col": "Email",
        "subscription_col": "Subscription",
        "trials_left": "Trials Left",
        "total_used": "Total Used",
        "reset_all_trials": "Reset All Users Trials",
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
        "max_seats": "Max Seats",
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
        "seat_limit_reached": "Seat limit reached",
        "member_added": "Member added",
        "member_removed": "Member removed",
        "org_created": "Organization created",
        "org_updated": "Organization updated",
        "user_assigned": "User assigned",
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
        "settings_tab": "Settings",
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


ORG_ADMIN_WIDGET_KEYS = (
    "org_admin_section",
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
    "org_admin_exit",
)


def _clear_org_admin_widget_keys():
    for key in ORG_ADMIN_WIDGET_KEYS:
        st.session_state.pop(key, None)
    for key in list(st.session_state.keys()):
        if str(key).startswith("FormSubmitter:") and "org_" in str(key):
            st.session_state.pop(key, None)


def request_org_admin_exit():
    st.session_state._exit_org_admin_pending = True


def apply_pending_org_admin_exit():
    if st.session_state.pop("_exit_org_admin_pending", False):
        reset_to_authenticated_main_session()


def _safe_date_prefix(value, fallback: str = "-") -> str:
    if not value:
        return fallback
    return str(value)[:10]


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
            "organization_logo_url": None,
        }


def render_enterprise_branding(profile):
    org_name = profile.get("organization_name")
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


def render_org_logo_section(org_id: str, logo_url, key_prefix: str):
    st.subheader(t()["org_logo"])
    if logo_url:
        st.image(logo_url, width=140)
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
            org_name = profile.get("organization_name") or t()["enterprise_plan"]
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
        
        if st.session_state.authenticated:
            st.divider()
            st.markdown(f"**👤 {st.session_state.user_email or ''}**")

            if st.session_state.user_id == "admin":
                st.caption("平台管理员" if st.session_state.lang == "zh" else "Platform Admin")
                if st.button(t()["logout"], use_container_width=True, key="admin_sidebar_logout"):
                    request_guest_reset()
                    st.rerun()
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
            if st.button("⚙️", key="org_gear_btn", help=t()["org_admin_btn"], use_container_width=True):
                _clear_org_admin_widget_keys()
                st.session_state.org_admin_mode = True
                st.rerun()
        elif show_platform_gear:
            if st.button("⚙️", key="gear_btn", help="Admin Login", use_container_width=True):
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
                    st.session_state.admin_mode = True
                    st.session_state.show_admin_login = False
                    st.session_state.authenticated = True
                    st.session_state.user_email = ADMIN_EMAIL
                    st.session_state.user_id = "admin"
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

    apps = {
        "📊 Product Feasibility": {
            "desc": "产品可行性分析 - 挖掘市场与用户之声",
            "desc_en": "Product Feasibility - Voice of Market & Users",
            "url": APP_URLS["feasibility"],
        },
        "🔍 AI-DQA": {
            "desc": "设计风险分析 - AI赋能DFMEA",
            "desc_en": "Design Risk Analysis - AI-powered DFMEA",
            "url": APP_URLS["dqa"],
        },
        "🔬 AI-FA": {
            "desc": "智能故障分析 - AI驱动5-Why根因定位与8D报告",
            "desc_en": "Intelligent Failure Analysis - AI-powered 5-Why Root Cause & 8D Report",
            "url": APP_URLS["fa"],
        },
        "📈 Para-Vary": {
            "desc": "蒙特卡洛模拟 - 累积公差仿真",
            "desc_en": "Monte Carlo Simulation - Tolerance Stack-up",
            "url": APP_URLS["paravary"],
        },
        "💡 EML Calculator": {
            "desc": "健康照明EML/m-EDI计算器 - 光谱分析与节律效应评估",
            "desc_en": "Healthy Lighting EML/m-EDI Calculator - Spectral Analysis & Circadian Evaluation",
            "url": APP_URLS["eml"],
        },
    }

    org_id = profile.get("organization_id")
    org_name = profile.get("organization_name")
    org_role = profile.get("org_role")

    for name, info in apps.items():
        with st.container(border=True):
            col_name, col_desc, col_btn = st.columns([2, 3, 1])
            with col_name:
                st.markdown(f"**{name}**")
            with col_desc:
                desc = info["desc"] if st.session_state.lang == "zh" else info["desc_en"]
                st.caption(desc)
            with col_btn:
                lang_param = "zh" if st.session_state.lang == "zh" else "en"
                full_url = build_app_launch_url(
                    info["url"],
                    st.session_state.user_id,
                    st.session_state.user_email,
                    lang_param,
                    tier,
                    remaining,
                    organization_id=org_id,
                    organization_name=org_name,
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
        org_name = profile.get("organization_name") if enterprise else None

        if org_name:
            render_enterprise_branding(profile)

        if enterprise:
            st.markdown(
                f"<h3 style='text-align: left; margin:0;'>{t()['welcome']}, {st.session_state.user_email}</h3>",
                unsafe_allow_html=True,
            )
        else:
            col_welcome, col_refresh = st.columns([11, 1])
            with col_welcome:
                st.markdown(
                    f"<h3 style='text-align: left; margin:0;'>{t()['welcome']}, {st.session_state.user_email}</h3>",
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
        st.dataframe(member_rows, use_container_width=True)

    with st.form("org_add_member_form", border=True):
        new_email = st.text_input(t()["member_email"])
        new_password = st.text_input(t()["initial_password"], type="password")
        new_role = st.selectbox(t()["member_role"], ["member", "admin"])
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
            selected = st.selectbox(t()["remove_member"], options, key="org_remove_select")
            if st.button(t()["remove_member"], key="org_remove_btn", use_container_width=True):
                email = selected.split(" ")[0]
                target = next((m for m in removable if m.get("email") == email), None)
                if target and remove_org_member(SUPABASE_URL, SERVICE_HEADERS, target.get("id")):
                    st.success(t()["member_removed"])
                    st.rerun()


def render_org_kb_tab(profile):
    org_id = profile.get("organization_id")
    org_name = profile.get("organization_name") or t()["enterprise_plan"]
    entries = list_tenant_knowledge(SUPABASE_URL, SERVICE_HEADERS, org_id)

    st.markdown(f"### {t()['kb_db_title'].format(org_name=org_name)}")
    st.caption(t()["kb_excel_hint"])

    lang = st.session_state.lang
    safe_org = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in org_name)
    template_name = f"{safe_org}_knowledge_template.xlsx"
    export_name = f"{safe_org}_knowledge_export.xlsx"

    col_tpl, col_export = st.columns(2)
    with col_tpl:
        st.download_button(
            t()["kb_download_template"],
            data=build_kb_template_excel(org_name, lang),
            file_name=template_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="kb_download_template_btn",
        )
    with col_export:
        st.download_button(
            t()["kb_download_data"],
            data=build_kb_export_excel(entries, org_name, lang),
            file_name=export_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="kb_download_export_btn",
        )

    uploaded_excel = st.file_uploader(
        t()["kb_upload_excel"],
        type=["xlsx"],
        key="kb_excel_uploader",
    )
    replace_existing = st.checkbox(t()["kb_replace_on_import"], key="kb_replace_on_import")
    if st.button(t()["kb_import_btn"], key="kb_import_btn", type="primary", use_container_width=True):
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
        st.dataframe(kb_rows, use_container_width=True)

        delete_options = [f"#{e.get('id')} [{e.get('category')}] {(e.get('content') or '')[:40]}" for e in entries]
        del_sel = st.selectbox(t()["kb_delete"], delete_options, key="org_kb_delete_select")
        if st.button(t()["kb_delete"], key="org_kb_delete_btn", use_container_width=True):
            record_id = int(del_sel.split("]")[0].replace("#", "").strip())
            if delete_tenant_knowledge(SUPABASE_URL, SERVICE_HEADERS, record_id, org_id):
                st.success("已删除" if st.session_state.lang == "zh" else "Deleted")
                st.rerun()

    with st.form("org_kb_add_form", border=True):
        category = st.selectbox(t()["kb_category"], KNOWLEDGE_CATEGORIES)
        content = st.text_area(t()["kb_content"])
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


def render_org_admin_panel():
    profile = safe_get_profile(st.session_state.user_id)
    if not is_org_admin(profile):
        request_org_admin_exit()
        st.rerun()
        return

    org_name = profile.get("organization_name") or t()["enterprise_plan"]
    st.markdown(f"## ⚙️ {t()['org_admin_panel']} — {org_name}")

    section_labels = {
        "members": t()["members_tab"],
        "kb": t()["kb_tab"],
        "settings": t()["settings_tab"],
    }
    selected_section = st.radio(
        "org_admin_section",
        list(section_labels.keys()),
        format_func=lambda key: section_labels[key],
        horizontal=True,
        key="org_admin_section",
        label_visibility="collapsed",
    )
    if selected_section == "members":
        render_org_members_tab(profile)
    elif selected_section == "kb":
        render_org_kb_tab(profile)
    else:
        render_org_logo_section(
            profile.get("organization_id"),
            profile.get("organization_logo_url"),
            "org_admin",
        )

    st.markdown("---")
    st.button(
        t()["exit_org_admin"],
        use_container_width=True,
        key="org_admin_exit",
        on_click=request_org_admin_exit,
    )


def render_platform_enterprise_section(users):
    try:
        orgs = list_organizations(SUPABASE_URL, SERVICE_HEADERS)
        if not orgs and st.session_state.lang == "zh":
            st.caption(t()["migration_hint"])

        st.subheader(t()["create_org"])
        with st.form("platform_create_org", border=True):
            org_name = st.text_input(t()["org_name"])
            max_seats = st.number_input(t()["max_seats"], min_value=1, max_value=500, value=10)
            submitted = st.form_submit_button(t()["create_org"], type="primary", use_container_width=True)
            if submitted and org_name.strip():
                created = create_organization(SUPABASE_URL, SERVICE_HEADERS, org_name.strip(), int(max_seats))
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
            org_rows.append({
                t()["org_name"]: org.get("name"),
                t()["max_seats"]: org.get("max_seats"),
                t()["seats_used"]: member_count,
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
            return (
                f"{item.get('name', '-')} | {item.get('member_count', 0)}/{item.get('max_seats', 0)} | {short_id}"
            )

        selected_org_id = st.selectbox(
            t()["select_org"],
            org_ids,
            format_func=_org_option_label,
            key="platform_selected_org_id",
        )
        st.dataframe(org_rows, use_container_width=True)

        selected_org = org_lookup.get(selected_org_id, {})

        if minus_clicked and selected_org_id:
            st.session_state.pending_delete_org_id = selected_org_id

        pending_id = st.session_state.get("pending_delete_org_id")
        if pending_id and pending_id in org_lookup:
            pending_name = org_lookup[pending_id].get("name", pending_id)
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
        new_max = st.number_input(
            t()["max_seats"],
            min_value=1,
            max_value=500,
            value=int(selected_org.get("max_seats") or 10),
            key="platform_org_max_seats",
        )
        if st.button(t()["update_btn"], key="platform_update_org_btn", use_container_width=True):
            if update_organization(SUPABASE_URL, SERVICE_HEADERS, selected_org_id, {"max_seats": int(new_max)}):
                st.success(t()["org_updated"])
                st.rerun()

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
                "剩余次数": user.get("free_trials_remaining", 30),
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
        user_options = [f"{u.get('email')} ({u.get('subscription_tier')})" for u in users]
        if st.session_state.get("admin_select_user") not in user_options:
            st.session_state.admin_select_user = user_options[0]
        selected = st.selectbox(t()["select_user"], user_options, key="admin_select_user")
        selected_email = selected.split(" (")[0]
        selected_user = next((u for u in users if u.get("email") == selected_email), None)

        if selected_user:
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
                new_trials = st.number_input(
                    t()["set_trials"], min_value=0, max_value=100,
                    value=selected_user.get("free_trials_remaining", 30), key="admin_new_trials",
                )
            with col_s3:
                admin_months = st.number_input(
                    "Pro 月数" if st.session_state.lang == "zh" else "Pro months",
                    min_value=1, max_value=12, value=1, key="admin_months",
                    disabled=new_tier != "pro",
                )

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button(t()["update_btn"], use_container_width=True, key="admin_update_btn", type="primary"):
                    update_data = {"subscription_tier": new_tier, "free_trials_remaining": new_trials}
                    if new_tier == "pro":
                        update_data["subscription_expires_at"] = (
                            datetime.now() + timedelta(days=30 * int(admin_months))
                        ).isoformat()
                    else:
                        update_data["subscription_expires_at"] = None
                    patch_resp = supabase_patch("profiles", selected_user.get("id"), update_data)
                    if patch_resp.status_code in [200, 204]:
                        st.success(f"已更新 {selected_email}")
                        st.rerun()
                    else:
                        st.error(f"更新失败: {patch_resp.text}")
            with col_b2:
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
        users_resp = supabase_get("profiles")
        if users_resp.status_code == 200:
            for user in users_resp.json():
                if user.get("subscription_tier") == "free":
                    supabase_patch("profiles", user.get("id"), {"free_trials_remaining": 30})
            st.success("所有免费用户次数已重置为 30 次")
            st.rerun()


def render_admin_panel():
    st.markdown(f"## ⚙️ {t()['admin_panel']}")
    try:
        response = supabase_get("profiles")
        users = response.json() if response.status_code == 200 else []

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

        tab_users, tab_orgs = st.tabs([t()["user_mgmt_tab"], t()["org_mgmt"]])
        with tab_users:
            try:
                render_admin_user_section(users, auth_users)
            except Exception as exc:
                st.error("用户管理加载失败" if st.session_state.lang == "zh" else "Failed to load user management")
                st.exception(exc)
        with tab_orgs:
            try:
                render_platform_enterprise_section(users)
            except Exception as exc:
                st.error("企业管理加载失败" if st.session_state.lang == "zh" else "Failed to load organization management")
                st.exception(exc)

    except Exception as e:
        st.warning(f"无法获取数据: {e}")
        st.exception(e)
    
    st.markdown("---")
    if st.button(t()["exit_admin"], use_container_width=True, key="admin_exit"):
        request_guest_reset()
        st.rerun()

def main():
    try:
        apply_pending_guest_reset()
        apply_pending_org_admin_exit()
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
