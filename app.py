import streamlit as st
from supabase import create_client
import jwt
import time
from datetime import datetime

# ================== 页面配置 ==================
st.set_page_config(page_title="TechLife Suite", layout="wide")

# ================== 自定义 CSS（语言按钮红底白字） ==================
st.markdown("""
<style>
button[kind="primary"][key="zh_btn"],
button[kind="primary"][key="en_btn"] {
    background-color: #ff4b4b !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    width: 100px !important;
    padding: 0.25rem 0 !important;
    font-weight: bold !important;
}
div[data-testid="column"]:nth-of-type(2),
div[data-testid="column"]:nth-of-type(3) {
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

# ================== Supabase 客户端（使用 service_role 绕过 RLS） ==================
def get_supabase():
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ================== 语言配置 ==================
TEXTS = {
    "zh": {
        "title": "🚀 TechLife Suite",
        "welcome": "🔐 欢迎使用 TechLife Suite",
        "login_prompt": "请登录或注册以继续",
        "email": "邮箱",
        "password": "密码",
        "login": "登录",
        "register": "注册",
        "submit": "提交",
        "login_success": "登录成功",
        "register_success": "注册成功！请登录。",
        "login_fail": "登录失败",
        "register_fail": "注册失败",
        "logout": "🚪 登出",
        "logged_in_as": "已登录: {}",
        "choose_tool": "请选择您要使用的 AI 分析工具：",
        "product": "📊 产品可行性分析",
        "dfmea": "⚙️ DFMEA 分析",
        "tolerance": "📏 公差分析",
        "use_now": "立即使用",
        "subscription": "订阅计划",
        "free": "免费版",
        "pro": "专业版",
        "remaining": "本月剩余免费次数: {}",
        "unlimited": "无限次使用",
        "upgrade": "升级订阅",
        "admin": "⚙️",
        "mode": "模式",
    },
    "en": {
        "title": "🚀 TechLife Suite",
        "welcome": "🔐 Welcome to TechLife Suite",
        "login_prompt": "Please log in or sign up",
        "email": "Email",
        "password": "Password",
        "login": "Login",
        "register": "Sign Up",
        "submit": "Submit",
        "login_success": "Login successful",
        "register_success": "Registration successful! Please log in.",
        "login_fail": "Login failed",
        "register_fail": "Registration failed",
        "logout": "🚪 Logout",
        "logged_in_as": "Logged in as: {}",
        "choose_tool": "Choose your AI analysis tool:",
        "product": "📊 Product Feasibility",
        "dfmea": "⚙️ DFMEA Analysis",
        "tolerance": "📏 Tolerance Analysis",
        "use_now": "Use Now",
        "subscription": "Subscription Plan",
        "free": "Free",
        "pro": "Pro",
        "remaining": "Free trials remaining: {}",
        "unlimited": "Unlimited",
        "upgrade": "Upgrade",
        "admin": "⚙️",
        "mode": "Mode",
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "zh"

def t(key):
    return TEXTS[st.session_state.lang].get(key, key)

# ================== 顶部栏（语言切换 + 齿轮） ==================
col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
with col2:
    if st.button("中文", key="zh_btn", type="primary"):
        st.session_state.lang = "zh"
        st.rerun()
with col3:
    if st.button("English", key="en_btn", type="primary"):
        st.session_state.lang = "en"
        st.rerun()
with col4:
    if st.button(t("admin"), key="admin_btn"):
        st.session_state.show_admin = not st.session_state.get("show_admin", False)
        st.rerun()

# ================== JWT 配置 ==================
JWT_SECRET = st.secrets["JWT_SECRET_KEY"]
TOKEN_EXPIRY = 3600  # 1小时

def generate_token(email):
    payload = {"email": email, "exp": time.time() + TOKEN_EXPIRY}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# ================== 订阅函数 ==================
def get_user_subscription(email):
    """获取用户订阅信息，不存在则创建默认记录"""
    result = supabase.table("user_authentication").select("*").eq("email", email).execute()
    if result.data:
        return result.data[0]
    # 不存在则创建默认记录
    default = {
        "email": email,
        "subscription_status": "free",
        "usage_count": 0,
        "usage_limit": 10
    }
    supabase.table("user_authentication").insert(default).execute()
    return default

def increment_usage(email):
    """增加使用次数（仅免费用户）"""
    user = get_user_subscription(email)
    if user["subscription_status"] == "active":
        return
    supabase.table("user_authentication").update(
        {"usage_count": user["usage_count"] + 1}
    ).eq("email", email).execute()

# ================== 登录/注册 ==================
if not st.session_state.get("authenticated", False):
    st.title(t("welcome"))
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
                else:  # 注册
                    resp = supabase.auth.sign_up({"email": email, "password": password})
                    if resp.user:
                        # 自动创建订阅记录
                        get_user_subscription(email)
                        st.success(t("register_success"))
                    else:
                        st.error(t("register_fail"))
            except Exception as e:
                st.error(f"{t('login_fail') if mode == t('login') else t('register_fail')}: {e}")

else:
    # ================== 已登录界面 ==================
    # 侧边栏
    st.sidebar.success(t("logged_in_as").format(st.session_state.user_email))
    if st.sidebar.button(t("logout")):
        st.session_state.clear()
        st.rerun()
    
    # 订阅信息
    user = get_user_subscription(st.session_state.user_email)
    is_pro = user["subscription_status"] == "active"
    st.sidebar.markdown(f"**{t('subscription')}**: {t('pro') if is_pro else t('free')}")
    if is_pro:
        st.sidebar.success(t("unlimited"))
    else:
        remaining = max(0, user["usage_limit"] - user["usage_count"])
        st.sidebar.info(t("remaining").format(remaining))
        if remaining == 0:
            st.sidebar.warning(t("remaining").format(0))
    
    # 生成 JWT token
    token = generate_token(st.session_state.user_email)
    
    # 工具链接（请修改为你的实际子域名）
    lang = st.session_state.lang
    product_url = f"https://appuct-feasibility-analysis.streamlit.app/?token={token}&lang={lang}"
    dfmea_url = f"https://ai-design-dfmea.streamlit.app/?token={token}&lang={lang}"
    tolerance_url = f"https://dfss-stack-tolerance-analysis.streamlit.app/?token={token}&lang={lang}"
    
    # 主界面
    st.title(t("title"))
    st.markdown(t("choose_tool"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"### {t('product')}")
        st.link_button(t("use_now"), product_url)
    with col2:
        st.markdown(f"### {t('dfmea')}")
        st.link_button(t("use_now"), dfmea_url)
    with col3:
        st.markdown(f"### {t('tolerance')}")
        st.link_button(t("use_now"), tolerance_url)
    
    # 管理员后台（简单版）
    if st.session_state.get("show_admin", False):
        st.divider()
        st.subheader("🛠️ 管理后台")
        try:
            users = supabase.table("user_authentication").select("*").execute()
            if users.data:
                st.dataframe(users.data, use_container_width=True)
            else:
                st.info("暂无用户")
        except Exception as e:
            st.error(f"加载用户列表失败: {e}")
