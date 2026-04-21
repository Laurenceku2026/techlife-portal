import streamlit as st
from st_supabase_connection import SupabaseConnection
import jwt
import time
import pandas as pd

# ================== 页面配置 ==================
st.set_page_config(page_title="TechLife Suite", layout="wide")

# ================== 初始化 Supabase 连接 ==================
conn = st.connection("supabase", type=SupabaseConnection)
supabase = conn.client

# 为了获取用户列表，需要 service_role key（具有管理员权限）
# 请在 secrets 中配置 SUPABASE_SERVICE_ROLE_KEY
try:
    service_role_key = st.secrets["connections"]["supabase"]["SUPABASE_SERVICE_ROLE_KEY"]
    # 创建一个具有 admin 权限的客户端
    from supabase import create_client
    supabase_admin = create_client(
        st.secrets["connections"]["supabase"]["SUPABASE_URL"],
        service_role_key
    )
except:
    supabase_admin = None
    st.warning("未配置 SUPABASE_SERVICE_ROLE_KEY，管理员功能受限")

# ================== 语言配置 ==================
LANGUAGES = {"zh": "中文", "en": "English"}
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
        "user_list": "注册用户列表",
        "email_col": "邮箱",
        "created_at_col": "注册时间",
        "subscription_col": "订阅状态",
        "update_subscription": "更新订阅",
        "back_to_portal": "← 返回门户",
        "no_users": "暂无用户",
        "load_error": "加载用户列表失败",
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
        "user_list": "Registered Users",
        "email_col": "Email",
        "created_at_col": "Signed Up",
        "subscription_col": "Subscription",
        "update_subscription": "Update",
        "back_to_portal": "← Back to Portal",
        "no_users": "No users found",
        "load_error": "Failed to load users",
    }
}

if "language" not in st.session_state:
    st.session_state.language = "zh"

def t(key):
    return TEXTS[st.session_state.language].get(key, key)

# ================== 语言切换和齿轮（管理员） ==================
# 创建顶部栏：左侧留空，右侧放置语言按钮和齿轮
top_col1, top_col2, top_col3, top_col4 = st.columns([6, 1, 1, 1])
with top_col2:
    if st.button("中文", key="zh_btn"):
        st.session_state.language = "zh"
        st.rerun()
with top_col3:
    if st.button("English", key="en_btn"):
        st.session_state.language = "en"
        st.rerun()
with top_col4:
    # 齿轮图标仅管理员可见（登录后且 is_admin 为 True）
    if st.session_state.get("authenticated", False) and st.session_state.get("is_admin", False):
        if st.button("⚙️", key="admin_gear"):
            st.session_state.show_admin = not st.session_state.get("show_admin", False)
            st.rerun()

# ================== JWT 配置 ==================
JWT_SECRET = st.secrets.get("JWT_SECRET_KEY", "fallback-secret-key-change-me")
TOKEN_EXPIRY_SECONDS = 3600

def generate_token(email):
    payload = {"email": email, "exp": time.time() + TOKEN_EXPIRY_SECONDS}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# ================== 管理员邮箱列表 ==================
ADMIN_EMAILS = ["Techlife2027@gmail.com"]  # 替换为你的管理员邮箱

# ================== 初始化 session_state ==================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.is_admin = False
    st.session_state.token = None
    st.session_state.show_admin = False  # 是否显示管理后台

def logout():
    supabase.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.is_admin = False
    st.session_state.token = None
    st.session_state.show_admin = False
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
                        st.session_state.is_admin = email in ADMIN_EMAILS
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

# ================== 管理后台：显示所有用户 ==================
def admin_dashboard():
    st.subheader(t("admin_title"))
    if supabase_admin is None:
        st.error("管理功能未启用：缺少 SUPABASE_SERVICE_ROLE_KEY")
        return
    try:
        # 获取所有用户
        users = supabase_admin.auth.admin.list_users()
        if not users:
            st.info(t("no_users"))
            return
        user_data = []
        for user in users:
            user_data.append({
                t("email_col"): user.email,
                t("created_at_col"): user.created_at[:19] if user.created_at else "",
                t("subscription_col"): "待扩展"  # 你可以从自定义表读取订阅状态
            })
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True)
        st.markdown("---")
        st.caption("提示：用户订阅管理功能可后续集成 Stripe webhook 实现")
    except Exception as e:
        st.error(f"{t('load_error')}: {e}")
    
    if st.button(t("back_to_portal")):
        st.session_state.show_admin = False
        st.rerun()

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
    
    # 生成 token
    if st.session_state.token is None:
        st.session_state.token = generate_token(st.session_state.user_email)
    token = st.session_state.token
    
    # ========== 工具链接（请修改为你的实际子域名） ==========
    # 注意：这些子域名必须已经在 Cloudflare 配置了重定向规则，指向对应的 Streamlit App
    product_url = f"https://product.techlife-suite.com?token={token}"      # 产品可行性
    dfmea_url = f"https://para-vary.techlife-suite.com?token={token}"      # DFMEA
    tolerance_url = f"https://stack-tolerance.techlife-suite.com?token={token}"  # 公差分析
    
    # 判断是否显示管理后台
    if st.session_state.get("show_admin", False) and st.session_state.is_admin:
        admin_dashboard()
    else:
        # 普通用户界面（或管理员但未进入后台）
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
