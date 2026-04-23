import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="TechLife Suite",
    page_icon="🔧",
    layout="wide"
)

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
        "free_trial": "免费次数",
        "subscription": "订阅",
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
        "months": "月数",
        "update_btn": "更新订阅",
        "exit_admin": "退出管理员模式",
        "email_col": "邮箱",
        "subscription_col": "订阅",
        "trials_left": "剩余次数",
        "expires_col": "到期时间",
    },
    "en": {
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 About System",
        "about_text": """
**TechLife Suite** is an **AI-empowered DFSS (Design for Six Sigma)** platform for R&D engineers.

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
        "free_trial": "Free Trials",
        "subscription": "Subscription",
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
        "months": "Months",
        "update_btn": "Update Subscription",
        "exit_admin": "Exit Admin Mode",
        "email_col": "Email",
        "subscription_col": "Subscription",
        "trials_left": "Trials Left",
        "expires_col": "Expires",
    }
}

ADMIN_USERNAME = "Laurence_ku"
ADMIN_PASSWORD = "Ku_product$2026"

@st.cache_resource
def init_supabase():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as e:
        st.error(f"Supabase 连接失败: {e}")
        return None

supabase = init_supabase()

# Session State
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

def t():
    return TEXTS[st.session_state.lang]

def get_user_profile(user_id: str):
    """安全获取用户资料"""
    if not supabase or not user_id:
        return {"subscription_tier": "free", "free_trials_remaining": 10}
    try:
        response = supabase.table("profiles")\
            .select("subscription_tier, free_trials_remaining")\
            .eq("id", user_id)\
            .execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        print(f"Error fetching profile: {e}")
    return {"subscription_tier": "free", "free_trials_remaining": 10}

def render_sidebar():
    with st.sidebar:
        st.title(t()["sidebar_title"])
        st.subheader(t()["about_header"])
        st.markdown(t()["about_text"])
        st.divider()
        st.subheader(t()["contact_header"])
        st.markdown(t()["contact_email"])
        
        if st.session_state.authenticated:
            st.divider()
            st.markdown(f"**👤 {st.session_state.user_email}**")
            profile = get_user_profile(st.session_state.user_id)
            tier = profile.get("subscription_tier", "free")
            st.caption(f"订阅: {'💎 专业版' if tier == 'pro' else '🔒 免费版'}")
            
            if st.button(t()["logout"], use_container_width=True):
                if supabase:
                    try:
                        supabase.auth.sign_out()
                    except:
                        pass
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_email = None
                st.session_state.admin_mode = False
                st.rerun()

def render_top_buttons():
    col1, col2, col3, col4, col5 = st.columns([8, 1.2, 1.2, 1.2, 1])
    with col2:
        if st.button(t()["chinese"], key="zh_btn", use_container_width=True):
            if st.session_state.lang != "zh":
                st.session_state.lang = "zh"
                st.rerun()
    with col3:
        if st.button(t()["english"], key="en_btn", use_container_width=True):
            if st.session_state.lang != "en":
                st.session_state.lang = "en"
                st.rerun()
    with col4:
        if st.button("⚙️", key="gear_btn", help="管理员登录", use_container_width=True):
            st.session_state.show_admin_login = True
            st.rerun()

def render_admin_login_form():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['admin_login_title']}</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            username = st.text_input(t()["admin_username"], key="admin_username")
            password = st.text_input(t()["admin_password"], type="password", key="admin_password")
            if st.button(t()["admin_login_btn"], use_container_width=True, type="primary"):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_mode = True
                    st.session_state.show_admin_login = False
                    st.session_state.authenticated = True
                    st.session_state.user_email = "admin@techlife.com"
                    st.session_state.user_id = "admin"
                    st.rerun()
                else:
                    st.error(t()["admin_error"])
        if st.button(t()["admin_back"], use_container_width=True):
            st.session_state.show_admin_login = False
            st.rerun()

def render_login_form():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center;'>{t()['main_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>{t()['main_subtitle']}</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            email = st.text_input(t()["email_placeholder"], key="login_email")
            password = st.text_input(t()["password_placeholder"], type="password", key="login_password")
            
            if st.button(t()["login_btn"], use_container_width=True, type="primary"):
                if email and password and supabase:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.session_state.authenticated = True
                        st.session_state.user_id = response.user.id
                        st.session_state.user_email = response.user.email
                        st.rerun()
                    except Exception as e:
                        st.error(f"登录失败: {str(e)}")
                else:
                    st.warning("请输入邮箱和密码")
        
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
        with st.container(border=True):
            email = st.text_input(t()["email_placeholder"], key="reg_email")
            password = st.text_input(t()["password_placeholder"], type="password", key="reg_password")
            confirm = st.text_input(t()["confirm_password"], type="password", key="reg_confirm")
            
            if st.button(t()["register_submit"], use_container_width=True, type="primary"):
                if not email or not password:
                    st.warning("请填写邮箱和密码")
                elif password != confirm:
                    st.warning("两次输入的密码不一致")
                elif len(password) < 6:
                    st.warning("密码长度至少6位")
                elif supabase:
                    try:
                        response = supabase.auth.sign_up({
                            "email": email,
                            "password": password
                        })
                        st.success("注册成功！请登录")
                        st.session_state.show_register = False
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "User already registered" in error_msg:
                            st.error("该邮箱已注册，请直接登录")
                        else:
                            st.error(f"注册失败: {error_msg}")
        
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

def render_main_app():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        profile = get_user_profile(st.session_state.user_id)
        tier = profile.get("subscription_tier", "free")
        remaining = profile.get("free_trials_remaining", 10)
        
        st.markdown(f"<h3 style='text-align: center;'>{t()['welcome']}, {st.session_state.user_email}</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            st.metric(t()["subscription"], "💎 Pro" if tier == "pro" else "🔒 免费版")
        with col_sub2:
            st.metric(t()["free_trial"], f"{remaining} 次/天")
        
        st.markdown("---")
        st.markdown(f"### {t()['nav_title']}")
        
        apps = {
            "📊 Product Feasibility": {
                "desc": "产品可行性分析 - 挖掘市场与用户之声",
                "key": "feasibility"
            },
            "🔍 AI-DQA": {
                "desc": "设计风险分析 - AI赋能DFMEA",
                "key": "dqa"
            },
            "📈 Para-Vary": {
                "desc": "蒙特卡洛模拟 - 累积公差仿真",
                "key": "paravary"
            }
        }
        
        for app_name, app_info in apps.items():
            with st.container(border=True):
                st.markdown(f"**{app_name}**")
                st.caption(app_info["desc"])
                if st.button("启动", key=app_info["key"], use_container_width=True):
                    st.info("子应用功能即将上线")

def render_admin_panel():
    st.markdown(f"## ⚙️ {t()['admin_panel']}")
    
    if supabase:
        try:
            users = supabase.table("profiles").select("*", count="exact").execute()
            pro_users = supabase.table("profiles").select("*", count="exact")\
                .eq("subscription_tier", "pro").execute()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t()["total_users"], users.count)
            with col2:
                st.metric(t()["pro_users"], pro_users.count)
            with col3:
                st.metric(t()["free_users"], users.count - pro_users.count)
            
            st.markdown("---")
            st.subheader(t()["user_list"])
            
            if users.data:
                user_data = []
                for user in users.data:
                    user_data.append({
                        t()["email_col"]: user.get("email"),
                        t()["subscription_col"]: "💎 Pro" if user.get("subscription_tier") == "pro" else "🔒 Free",
                        t()["trials_left"]: user.get("free_trials_remaining", 10),
                    })
                st.dataframe(user_data, use_container_width=True)
        except Exception as e:
            st.warning(f"无法获取用户数据: {e}")
    else:
        st.warning("Supabase 未连接")
    
    st.markdown("---")
    if st.button(t()["exit_admin"], use_container_width=True):
        st.session_state.admin_mode = False
        st.session_state.authenticated = False
        st.rerun()

def main():
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
        else:
            render_main_app()

if __name__ == "__main__":
    main()
