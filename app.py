import streamlit as st
import requests
import stripe
from datetime import datetime, timedelta

# ==================== 页面配置 ====================
st.set_page_config(page_title="TechLife Suite", page_icon="🔧", layout="wide")

# ==================== 管理员配置 ====================
ADMIN_USERNAME = "Laurence_ku"
ADMIN_PASSWORD = "Ku_product$2026"
ADMIN_EMAIL = "techlife2027@gmail.com"

# 三个 APP 的 URL
APP_URLS = {
    "feasibility": "https://appuct-feasibility-analysis.streamlit.app",
    "dqa": "https://ai-design-dfmea.streamlit.app",
    "paravary": "https://dfss-stack-tolerance-analysis.streamlit.app"
}

# ==================== Stripe 配置 ====================
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

# ==================== Supabase 配置 ====================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def supabase_get(table: str, user_id: str = None, id_field: str = "id"):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if user_id:
        url += f"?{id_field}=eq.{user_id}"
    response = requests.get(url, headers=HEADERS)
    return response

def supabase_patch(table: str, user_id: str, data: dict):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{user_id}"
    response = requests.patch(url, headers=HEADERS, json=data)
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

def t():
    return TEXTS[st.session_state.lang]

# ==================== 辅助函数 ====================
def get_user_profile(user_id: str):
    if not user_id or user_id == "admin":
        return {"subscription_tier": "free", "free_trials_remaining": 30, "subscription_expires_at": None}
    try:
        response = supabase_get("profiles", user_id)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return {
                "subscription_tier": data.get("subscription_tier", "free"),
                "free_trials_remaining": data.get("free_trials_remaining", 30),
                "subscription_expires_at": data.get("subscription_expires_at")
            }
    except Exception:
        pass
    return {"subscription_tier": "free", "free_trials_remaining": 30, "subscription_expires_at": None}

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

def create_checkout_session(user_id: str, user_email: str, price_id: str):
    try:
        st.write(f"🔍 调试: 创建会话 - 用户: {user_id}, 价格ID: {price_id}")
        session = stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url="https://techlife-app.streamlit.app",
            cancel_url="https://techlife-app.streamlit.app",
            metadata={'user_id': user_id, 'price_id': price_id}
        )
        st.write(f"🔍 调试: 会话创建成功, URL: {session.url}")
        return session.url, None
    except Exception as e:
        st.error(f"❌ Stripe 错误: {e}")
        return None, str(e)

# ==================== UI 组件 ====================
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
            remaining = profile.get("free_trials_remaining", 30)
            total_usage = get_user_total_usage(st.session_state.user_id)
            
            st.caption(f"📋 {t()['subscription']}: {'💎 Pro' if tier == 'pro' else '🔒 Free'}")
            if tier == "free":
                st.caption(f"🎫 {t()['free_trial']}: {remaining}")
                st.caption(f"📊 {t()['total_usage']}: {total_usage}")
            else:
                st.caption(f"🎫 {t()['free_trial']}: ∞")
                expires_at = profile.get("subscription_expires_at")
                if expires_at:
                    st.caption(f"📅 {t()['expires_at']}: {expires_at[:10]}")
            
            if st.button(t()["logout"], use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_email = None
                st.session_state.admin_mode = False
                st.rerun()
            
            # 侧边栏升级按钮（红底白字）
            if tier == "free":
                st.markdown("---")
                st.markdown(f"### 💎 {t()['upgrade_title']}")
                st.markdown(f"**{t()['pro_features_title']}**")
                st.markdown(t()["pro_feature_1"])
                st.markdown(t()["pro_feature_2"])
                st.markdown(t()["pro_feature_3"])
                if st.button(t()["monthly"], key="sidebar_monthly_btn", use_container_width=True, type="primary"):
                    url, error = create_checkout_session(
                        st.session_state.user_id, st.session_state.user_email,
                        st.secrets["STRIPE_PRICE_MONTHLY"]
                    )
                    if url:
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                    else:
                        st.error(f"创建支付会话失败: {error}")
                if st.button(t()["yearly"], key="sidebar_yearly_btn", use_container_width=True, type="primary"):
                    url, error = create_checkout_session(
                        st.session_state.user_id, st.session_state.user_email,
                        st.secrets["STRIPE_PRICE_YEARLY"]
                    )
                    if url:
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                    else:
                        st.error(f"创建支付会话失败: {error}")

def render_top_buttons():
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
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
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

def render_login_form():
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
                    auth_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
                    auth_headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
                    response = requests.post(auth_url, headers=auth_headers, json={"email": email, "password": password})
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.authenticated = True
                        st.session_state.user_id = data.get("user", {}).get("id")
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error(f"登录失败: {response.json().get('msg', '未知错误')}")
                except Exception as e:
                    st.error(f"登录失败: {e}")
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
                    st.warning("请填写邮箱和密码")
                elif password != confirm:
                    st.warning("两次输入的密码不一致")
                elif len(password) < 6:
                    st.warning("密码长度至少6位")
                else:
                    try:
                        auth_url = f"{SUPABASE_URL}/auth/v1/signup"
                        auth_headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
                        response = requests.post(auth_url, headers=auth_headers, json={"email": email, "password": password})
                        if response.status_code == 200:
                            st.success(t()["register_success"])
                            st.session_state.show_register = False
                            st.rerun()
                        else:
                            error_msg = response.json().get("msg", "注册失败")
                            if "User already registered" in error_msg:
                                st.error(t()["email_exists"])
                            else:
                                st.error(f"注册失败: {error_msg}")
                    except Exception as e:
                        st.error(f"注册失败: {e}")
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
        remaining = profile.get("free_trials_remaining", 30)
        total_usage = get_user_total_usage(st.session_state.user_id)
        
        # 第一行：欢迎语 + 刷新按钮
        col_welcome, col_refresh = st.columns([6, 1])
        with col_welcome:
            st.markdown(f"<h3 style='text-align: left; margin:0;'>{t()['welcome']}, {st.session_state.user_email}</h3>", unsafe_allow_html=True)
        with col_refresh:
            if st.button("🔄", key="refresh_btn", help="刷新数据", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        # 第二行：四个卡片
        col_card1, col_card2, col_card3, col_upgrade = st.columns([1, 1, 1, 1.2])
        
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
        
        with col_upgrade:
            if tier == "free":
                st.markdown(f"<div style='text-align: center; font-weight: 500; margin-bottom: 8px;'>{t()['upgrade_title']}</div>", unsafe_allow_html=True)
                # 主页面支付按钮不加 type="primary"，保持默认颜色
                if st.button(t()["monthly"], key="main_monthly_btn", use_container_width=True):
                    url, error = create_checkout_session(
                        st.session_state.user_id, st.session_state.user_email,
                        st.secrets["STRIPE_PRICE_MONTHLY"]
                    )
                    if url:
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                    else:
                        st.error(f"创建支付会话失败: {error}")
                if st.button(t()["yearly"], key="main_yearly_btn", use_container_width=True):
                    url, error = create_checkout_session(
                        st.session_state.user_id, st.session_state.user_email,
                        st.secrets["STRIPE_PRICE_YEARLY"]
                    )
                    if url:
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                    else:
                        st.error(f"创建支付会话失败: {error}")
            else:
                st.markdown(f"<div style='text-align: center; font-weight: 500; margin-bottom: 8px;'>{t()['upgrade_title']}</div>", unsafe_allow_html=True)
                st.success("✅ 已是专业版", icon="🎉")
        
        st.markdown("---")
        st.markdown(f"### {t()['nav_title']}")
        st.caption(t()["open_new_tab"])
        
        apps = {
            "📊 Product Feasibility": {
                "desc": "产品可行性分析 - 挖掘市场与用户之声",
                "desc_en": "Product Feasibility - Voice of Market & Users",
                "url": APP_URLS["feasibility"]
            },
            "🔍 AI-DQA": {
                "desc": "设计风险分析 - AI赋能DFMEA",
                "desc_en": "Design Risk Analysis - AI-powered DFMEA",
                "url": APP_URLS["dqa"]
            },
            "📈 Para-Vary": {
                "desc": "蒙特卡洛模拟 - 累积公差仿真",
                "desc_en": "Monte Carlo Simulation - Tolerance Stack-up",
                "url": APP_URLS["paravary"]
            }
        }
        
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
                    full_url = f"{info['url']}?user_id={st.session_state.user_id}&email={st.session_state.user_email}&lang={lang_param}&trials_left={remaining}"
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

def render_admin_panel():
    st.markdown(f"## ⚙️ {t()['admin_panel']}")
    try:
        response = supabase_get("profiles")
        users = response.json() if response.status_code == 200 else []
        
        auth_users = {}
        try:
            auth_response = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
            if auth_response.status_code == 200:
                data = auth_response.json()
                user_list = data.get("users", []) if isinstance(data, dict) else data
                for u in user_list:
                    auth_users[u.get("id")] = {
                        "created_at": u.get("created_at", ""),
                        "last_sign_in_at": u.get("last_sign_in_at", ""),
                        "email_confirmed_at": u.get("email_confirmed_at", ""),
                    }
        except Exception as e:
            st.warning(f"获取用户详细信息失败: {e}")
        
        pro_users = [u for u in users if u.get("subscription_tier") == "pro"]
        confirmed_count = sum(1 for u in users if auth_users.get(u.get("id"), {}).get("email_confirmed_at"))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric(t()["total_users"], len(users))
        with col2: st.metric("已确认邮箱", confirmed_count)
        with col3: st.metric(t()["pro_users"], len(pro_users))
        with col4: st.metric(t()["free_users"], len(users) - len(pro_users))
        
        st.markdown("---")
        st.subheader(t()["user_list"])
        
        if users:
            user_data = []
            for user in users:
                ai = auth_users.get(user.get("id"), {})
                user_data.append({
                    t()["email_col"]: user.get("email"),
                    "邮箱确认": "✅" if ai.get("email_confirmed_at") else "❌",
                    t()["subscription_col"]: "💎 Pro" if user.get("subscription_tier") == "pro" else "🔒 Free",
                    "剩余次数": user.get("free_trials_remaining", 30),
                    "注册时间": (ai.get("created_at", "-")[:10]) if ai.get("created_at") else "-",
                    "最后登录": (ai.get("last_sign_in_at", "-")[:10]) if ai.get("last_sign_in_at") else "-",
                    "到期时间": user.get("subscription_expires_at", "-")[:10] if user.get("subscription_expires_at") else "-",
                })
            with st.container(height=400):
                st.dataframe(user_data, use_container_width=True)
        else:
            st.info("暂无用户数据")
        
        st.markdown("---")
        st.subheader(t()["subscription_mgmt"])
        
        if users:
            user_options = [f"{u.get('email')} ({u.get('subscription_tier')})" for u in users]
            selected = st.selectbox(t()["select_user"], user_options, key="admin_select_user")
            selected_email = selected.split(" ")[0]
            selected_user = next((u for u in users if u.get("email") == selected_email), None)
            
            if selected_user:
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    new_tier = st.selectbox(t()["set_subscription"], ["free", "pro"], 
                                            index=0 if selected_user.get("subscription_tier") == "free" else 1, key="admin_new_tier")
                with col_s2:
                    new_trials = st.number_input(t()["set_trials"], min_value=0, max_value=100, 
                                                  value=selected_user.get("free_trials_remaining", 30), key="admin_new_trials")
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button(t()["update_btn"], use_container_width=True, key="admin_update_btn", type="primary"):
                        update_data = {"subscription_tier": new_tier, "free_trials_remaining": new_trials}
                        if new_tier == "pro":
                            months = st.number_input("月数", min_value=1, max_value=12, value=1, key="admin_months")
                            update_data["subscription_expires_at"] = (datetime.now() + timedelta(days=30 * months)).isoformat()
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
                            reset_response = requests.post(f"{SUPABASE_URL}/auth/v1/recover", headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"}, json=reset_data)
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
                
    except Exception as e:
        st.warning(f"无法获取数据: {e}")
    
    st.markdown("---")
    if st.button(t()["exit_admin"], use_container_width=True, key="admin_exit"):
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
