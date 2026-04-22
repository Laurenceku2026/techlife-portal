import streamlit as st
from st_supabase_connection import SupabaseConnection
import jwt
import time
import pandas as pd
from datetime import datetime

# ================== 页面配置 ==================
st.set_page_config(page_title="TechLife Suite", layout="wide")

# ================== 自定义 CSS：通过 id 选择器精确控制中英文按钮 ==================
st.markdown("""
<style>
/* 直接通过 id 选择器，最可靠 */
#zh_btn, #en_btn {
    background-color: #ff4b4b !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    width: 100px !important;
    min-width: 100px !important;
    padding: 0.25rem 0 !important;
    font-weight: bold !important;
    text-align: center !important;
}
#zh_btn:hover, #en_btn:hover {
    background-color: #e03a3a !important;
}
/* 确保按钮所在的列不会挤压按钮宽度 */
div[data-testid="column"]:nth-child(2), div[data-testid="column"]:nth-child(3) {
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

# ================== 初始化 Supabase 连接 ==================
conn = st.connection("supabase", type=SupabaseConnection)
supabase = conn.client

# 获取 service_role key（用于管理后台）
try:
    service_role_key = st.secrets["connections"]["supabase"]["SUPABASE_SERVICE_ROLE_KEY"]
    from supabase import create_client
    supabase_admin = create_client(
        st.secrets["connections"]["supabase"]["SUPABASE_URL"],
        service_role_key
    )
except:
    supabase_admin = None

# ================== 语言配置 ==================
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
        "admin_panel": "🛠️ 管理后台",
        "admin_title": "管理员控制台",
        "admin_login_title": "管理员登录",
        "admin_login_prompt": "请输入管理员邮箱和密码",
        "admin_login_fail": "管理员邮箱或密码错误",
        "admin_logout": "退出管理后台",
        "user_list": "注册用户列表",
        "email_col": "邮箱",
        "created_at_col": "注册时间",
        "subscription_col": "订阅状态",
        "update_subscription": "更新订阅",
        "back_to_portal": "← 返回门户",
        "no_users": "暂无用户",
        "load_error": "加载用户列表失败",
        "gear_tooltip": "管理员登录",
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
        "admin_title": "Admin Console",
        "admin_login_title": "Admin Login",
        "admin_login_prompt": "Enter admin email and password",
        "admin_login_fail": "Invalid admin email or password",
        "admin_logout": "Exit Admin",
        "user_list": "Registered Users",
        "email_col": "Email",
        "created_at_col": "Signed Up",
        "subscription_col": "Subscription",
        "update_subscription": "Update",
        "back_to_portal": "← Back to Portal",
        "no_users": "No users found",
        "load_error": "Failed to load users",
        "gear_tooltip": "Admin Login",
    }
}

if "language" not in st.session_state:
    st.session_state.language = "zh"

def t(key):
    return TEXTS[st.session_state.language].get(key, key)

# ================== 顶部栏：语言切换 + 齿轮 ==================
top_col1, top_col2, top_col3, top_col4 = st.columns([6, 1, 1, 1])
with top_col2:
    if st.button("中文", key="zh_btn", type="primary"):
        st.session_state.language = "zh"
        st.rerun()
with top_col3:
    if st.button("English", key="en_btn", type="primary"):
        st.session_state.language = "en"
        st.rerun()
with top_col4:
    if st.button("⚙️", key="gear_btn", help=t("gear_tooltip")):
        st.session_state.show_admin = not st.session_state.get("show_admin", False)
        if not st.session_state.show_admin:
            st.session_state.admin_authenticated = False
            st.session_state.admin_email = None
        st.rerun()

# ================== JWT 配置 ==================
JWT_SECRET = st.secrets["connections"]["supabase"].get("JWT_SECRET_KEY", "fallback-secret")
TOKEN_EXPIRY_SECONDS = 3600

def generate_token(email):
    payload = {"email": email, "exp": time.time() + TOKEN_EXPIRY_SECONDS}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# ================== 管理员邮箱列表 ==================
ADMIN_EMAILS = ["Techlife2027@gmail.com"]   # 请替换为实际管理员邮箱

# ================== 初始化 session_state ==================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.token = None
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
    st.session_state.admin_email = None
if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

def logout():
    supabase.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.token = None
    st.rerun()

def admin_logout():
    st.session_state.admin_authenticated = False
    st.session_state.admin_email = None
    st.session_state.show_admin = False
    st.rerun()

# ================== 普通用户登录/注册表单 ==================
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
                        st.success(t("login_success"))
                        st.rerun()
                    else:
                        st.error(t("login_fail"))
                else:
                    resp = supabase.auth.sign_up({"email": email, "password": password})
                    if resp.user:
                        st.success(t("register_success"))
                    else:
                        st.error(t("register_fail"))
            except Exception as e:
                st.error(t("auth_error").format(str(e)))

# ================== 管理员登录表单 ==================
def admin_login_form():
    with st.form("admin_login_form"):
        email = st.text_input(t("email"))
        password = st.text_input(t("password"), type="password")
        submitted = st.form_submit_button(t("login"))
        if submitted:
            try:
                resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if resp.user and email in ADMIN_EMAILS:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_email = email
                    st.success(t("login_success"))
                    st.rerun()
                else:
                    st.error(t("admin_login_fail"))
            except Exception as e:
                st.error(t("auth_error").format(str(e)))

# ================== 管理后台：显示所有用户 ==================
def admin_dashboard():
    st.subheader(t("admin_title"))
    if supabase_admin is None:
        st.error("管理功能未启用：缺少 SUPABASE_SERVICE_ROLE_KEY")
        if st.button(t("back_to_portal")):
            admin_logout()
        return
    try:
        users = supabase_admin.auth.admin.list_users()
        if not users:
            st.info(t("no_users"))
        else:
            user_data = []
            for user in users:
                created_at_str = ""
                if user.created_at:
                    if isinstance(user.created_at, datetime):
                        created_at_str = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        created_at_str = str(user.created_at)[:19]
                user_data.append({
                    t("email_col"): user.email,
                    t("created_at_col"): created_at_str,
                    t("subscription_col"): "待扩展"
                })
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
            st.caption("提示：用户订阅管理功能可后续集成 Stripe webhook 实现")
    except Exception as e:
        st.error(f"{t('load_error')}: {e}")
    
    if st.button(t("admin_logout")):
        admin_logout()

# ================== 主界面逻辑 ==================
# 优先处理管理员面板（如果 show_admin 为 True）
if st.session_state.get("show_admin", False):
    if not st.session_state.get("admin_authenticated", False):
        st.title(t("admin_login_title"))
        st.markdown(t("admin_login_prompt"))
        admin_login_form()
    else:
        admin_dashboard()
else:
    # 普通用户界面
    if not st.session_state.authenticated:
        st.title(t("welcome_title"))
        st.markdown(t("login_prompt"))
        auth_form()
    else:
        st.sidebar.success(t("logged_in_as").format(st.session_state.user_email))
        if st.sidebar.button(t("logout")):
            logout()
        
        # 生成 token
        if st.session_state.token is None:
            st.session_state.token = generate_token(st.session_state.user_email)
        token = generate_token(st.session_state.user_email)
        st.write("DEBUG_TOKEN:", token)   # 临时显示在页面上
        st.write("DEBUG_TOKEN_LEN:", len(token))
        st.write("All secrets keys:", st.secrets.keys())
        st.write("PORTAL KEY:", st.secrets["JWT_SECRET_KEY"])
        
        # 工具链接（请修改为你的实际子域名）
        lang = st.session_state.language   # 'zh' 或 'en'
        product_url = f"https://appuct-feasibility-analysis.streamlit.app/?token={token}&lang={lang}"
        dfmea_url = f"https://ai-design-dfmea.streamlit.app/?token={token}&lang={lang}"
        tolerance_url = f"https://dfss-stack-tolerance-analysis.streamlit.app/?token={token}&lang={lang}"
        
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
