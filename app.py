import streamlit as st
from st_supabase_connection import SupabaseConnection
import jwt
import time

# ================== 页面配置 ==================
st.set_page_config(page_title="TechLife Suite", layout="wide")

# ================== 初始化 Supabase 连接 ==================
conn = st.connection("supabase", type=SupabaseConnection)
supabase = conn.client

# ================== 语言配置 ==================
# 支持的语言
LANGUAGES = {
    "zh": "中文",
    "en": "English"
}

# 所有文本字典
TEXTS = {
    "zh": {
        "app_title": "TechLife Suite",
        "welcome_title": "🔐 欢迎使用 TechLife Suite",
        "login_prompt": "请登录或注册以继续",
        "email": "邮箱",
        "password": "密码",
        "mode": "模式",
        "login": "登录",
        "register": "注册",
        "submit": "提交",
        "login_success": "登录成功",
        "register_success": "注册成功！请登录。",
        "login_fail": "登录失败，请检查邮箱和密码",
        "register_fail": "注册失败，可能邮箱已存在",
        "auth_error": "认证出错: {}",
        "logout": "🚪 登出",
        "logged_in_as": "已登录: {}",
        "choose_tool": "请选择您要使用的 AI 分析工具：",
        "product_feasibility": "📊 产品可行性分析",
        "dfmea": "⚙️ DFMEA 分析",
        "tolerance": "📏 公差分析",
        "use_now": "立即使用",
        "admin_panel": "🛠️ 管理面板",
        "admin_welcome": "欢迎，管理员！",
        "user_list": "用户列表",
        "no_users": "暂无用户",
        "email_col": "邮箱",
        "created_at_col": "注册时间",
        "subscription_col": "订阅状态",
        "update_subscription": "更新订阅",
        "back_to_portal": "← 返回门户",
        "unauthorized": "您没有管理员权限。",
    },
    "en": {
        "app_title": "TechLife Suite",
        "welcome_title": "🔐 Welcome to TechLife Suite",
        "login_prompt": "Please log in or sign up to continue",
        "email": "Email",
        "password": "Password",
        "mode": "Mode",
        "login": "Login",
        "register": "Sign Up",
        "submit": "Submit",
        "login_success": "Login successful",
        "register_success": "Registration successful! Please log in.",
        "login_fail": "Login failed, please check email and password",
        "register_fail": "Registration failed, email may already exist",
        "auth_error": "Auth error: {}",
        "logout": "🚪 Logout",
        "logged_in_as": "Logged in as: {}",
        "choose_tool": "Choose your AI analysis tool:",
        "product_feasibility": "📊 Product Feasibility",
        "dfmea": "⚙️ DFMEA Analysis",
        "tolerance": "📏 Tolerance Analysis",
        "use_now": "Use Now",
        "admin_panel": "🛠️ Admin Panel",
        "admin_welcome": "Welcome, Admin!",
        "user_list": "User List",
        "no_users": "No users found",
        "email_col": "Email",
        "created_at_col": "Registered At",
        "subscription_col": "Subscription Status",
        "update_subscription": "Update Subscription",
        "back_to_portal": "← Back to Portal",
        "unauthorized": "You are not authorized as admin.",
    }
}

# 获取当前语言
if "language" not in st.session_state:
    st.session_state.language = "zh"  # 默认中文

def t(key):
    """翻译函数"""
    return TEXTS[st.session_state.language].get(key, key)

# ================== 语言切换按钮（右上角） ==================
col_lang1, col_lang2, col_lang3 = st.columns([8, 1, 1])
with col_lang2:
    if st.button("中文", key="zh_btn"):
        st.session_state.language = "zh"
        st.rerun()
with col_lang3:
    if st.button("English", key="en_btn"):
        st.session_state.language = "en"
        st.rerun()

# ================== JWT 配置（用于单点登录） ==================
JWT_SECRET = st.secrets.get("JWT_SECRET_KEY", "fallback-secret-key-change-me")
TOKEN_EXPIRY_SECONDS = 3600  # 1小时

def generate_token(email):
    payload = {
        "email": email,
        "exp": time.time() + TOKEN_EXPIRY_SECONDS
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# ================== 管理员邮箱列表 ==================
ADMIN_EMAILS = ["admin@techlife.com", "techlife2027@gmail.com"]  # 请修改为你的管理员邮箱

# ================== 初始化 session_state ==================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.is_admin = False
    st.session_state.token = None

# ================== 登出函数 ==================
def logout():
    supabase.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.is_admin = False
    st.session_state.token = None
    st.rerun()

# ================== 登录/注册表单 ==================
def auth_form():
    with st.form("auth_form"):
        email = st.text_input(t("email"))
        password = st.text_input(t("password"), type="password")
        mode = st.radio(t("mode"), [t("login"), t("register")], horizontal=True)
        submitted = st.form_submit_button(t("submit"))

        if submitted:
            try:
                if mode == t("login"):
                    resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if resp.user:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        # 检查是否为管理员
                        st.session_state.is_admin = email in ADMIN_EMAILS
                        st.success(t("login_success"))
                        st.rerun()
                    else:
                        st.error(t("login_fail"))
                else:  # 注册
                    resp = supabase.auth.sign_up({"email": email, "password": password})
                    if resp.user:
                        st.success(t("register_success"))
                    else:
                        st.error(t("register_fail"))
            except Exception as e:
                st.error(t("auth_error").format(str(e)))

# ================== 管理面板（仅管理员可见） ==================
def admin_panel():
    st.subheader(t("admin_panel"))
    st.write(t("admin_welcome"))
    
    # 示例：从 Supabase 的 Auth 用户列表获取所有用户（需要 admin 权限，这里简化：直接查询自定义表 user_authentication）
    # 注意：Supabase 的 admin 列表需要 service_role key，为了安全，我们使用之前创建的 user_authentication 表
    try:
        # 使用 service_role 需要额外配置，这里演示从 user_authentication 表读取
        # 实际上，由于我们只用了 Supabase Auth，用户数据在 auth.users 表中，但直接查询需要 service_role 密钥。
        # 简单起见，我们假设已经创建了 user_authentication 表并同步了用户。
        # 如果没有该表，可以提示。
        with st.expander(t("user_list")):
            # 这里需要 Supabase 的 admin 权限，我们暂时显示一个占位
            st.info("管理员功能：可在此查看所有用户、修改订阅状态等。需要额外配置 Supabase 的 service_role key。")
            # 实际实现可调用 supabase 的 admin API，但为了安全，建议在云函数中处理。
    except Exception as e:
        st.error(f"加载用户列表失败: {e}")

# ================== 主界面 ==================
if not st.session_state.authenticated:
    st.title(t("welcome_title"))
    st.markdown(t("login_prompt"))
    auth_form()
else:
    # 侧边栏显示用户信息和登出按钮
    st.sidebar.success(t("logged_in_as").format(st.session_state.user_email))
    if st.sidebar.button(t("logout")):
        logout()
    
    # 生成单点登录 token（用于跳转工具时传递身份）
    if st.session_state.token is None:
        st.session_state.token = generate_token(st.session_state.user_email)
    token = st.session_state.token
    
    # 工具链接（附加 token）
    product_url = f"https://product.techlife-suite.com?token={token}"
    dfmea_url = f"https://para-vary.techlife-suite.com?token={token}"
    tolerance_url = f"https://stack-tolerance.techlife-suite.com?token={token}"
    
    # 主区域
    st.title(t("app_title"))
    st.markdown(t("choose_tool"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"### {t('product_feasibility')}")
        st.link_button(t("use_now"), product_url)
    with col2:
        st.markdown(f"### {t('dfmea')}")
        st.link_button(t("use_now"), dfmea_url)
    with col3:
        st.markdown(f"### {t('tolerance')}")
        st.link_button(t("use_now"), tolerance_url)
    
    # 如果用户是管理员，显示管理面板（可选，放在折叠区域或独立页面）
    if st.session_state.is_admin:
        st.divider()
        with st.expander(t("admin_panel")):
            admin_panel()
    else:
        # 普通用户可以有一个返回门户的按钮（其实已经在门户了）
        pass
