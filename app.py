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
    """GET 请求"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if user_id:
        url += f"?{id_field}=eq.{user_id}"
    response = requests.get(url, headers=HEADERS)
    return response

def supabase_patch(table: str, user_id: str, data: dict):
    """PATCH 请求（更新）"""
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
        "upgrade_title": "💎 升级到专业版",
        "upgrade_features": "**专业版功能：**",
        "feature_1": "- ✅ 无限次使用所有应用",
        "feature_2": "- ✅ 优先技术支持",
        "feature_3": "- ✅ 导出完整报告",
        "monthly": "📅 月付 $29/月",
        "yearly": "📅 年付 $299/年 (省 $49)",
        "upgrade_success": "✅ 升级成功！您是专业版用户了！",
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
        "upgrade_title": "💎 Upgrade to Pro",
        "upgrade_features": "**Pro Features:**",
        "feature_1": "- ✅ Unlimited access to all apps",
        "feature_2": "- ✅ Priority support",
        "feature_3": "- ✅ Export full reports",
        "monthly": "📅 Monthly $29/month",
        "yearly": "📅 Yearly $299/year (Save $49)",
        "upgrade_success": "✅ Upgrade successful! You are now a Pro user!",
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
        return {"subscription_tier": "free", "free_trials_remaining": 30}
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
    """创建 Stripe Checkout Session"""
    try:
        session = stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url="https://techlife-app.streamlit.app?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://techlife-app.streamlit.app",
            metadata={
                'user_id': user_id,
                'price_id': price_id
            }
        )
        return session.url, None
    except Exception as e:
        return None, str(e)

def render_upgrade_section(tier: str, user_id: str, user_email: str):
    """渲染升级到专业版的界面"""
    if tier == "pro":
        return
    
    st.markdown("---")
    st.markdown(f"### {t()['upgrade_title']}")
    st.markdown(t()["upgrade_features"])
    st.markdown(t()["feature_1"])
    st.markdown(t()["feature_2"])
    st.markdown(t()["feature_3"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t()["monthly"], key="monthly_btn", use_container_width=True):
            url, error = create_checkout_session(
                user_id=user_id,
                user_email=user_email,
                price_id=st.secrets["STRIPE_PRICE_MONTHLY"]
            )
            if url:
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
            else:
                st.error(f"创建支付会话失败: {error}")
    
    with col2:
        if st.button(t()["yearly"], key="yearly_btn", use_container_width=True):
            url, error = create_checkout_session(
                user_id=user_id,
                user_email=user_email,
                price_id=st.secrets["STRIPE_PRICE_YEARLY"]
            )
            if url:
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
            else:
                st.error(f"创建支付会话失败: {error}")

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
                    st.caption(f"📅 到期: {expires_at[:10]}")
            
            if st.button(t()["logout"], use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_email = None
                st.session_state.admin_mode = False
                st.rerun()
            
            # 升级按钮
            render_upgrade_section(tier, st.session_state.user_id, st.session_state.user_email)

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
            
            if submitted:
                if email and password:
                    try:
                        auth_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
                        auth_headers = {
                            "apikey": SUPABASE_KEY,
                            "Content-Type": "application/json"
                        }
                        auth_data = {"email": email, "password": password}
                        response = requests.post(auth_url, headers=auth_headers, json=auth_data)
                        
                        if response.status_code == 200:
                            data = response.json()
                            user_id = data.get("user", {}).get("id")
                            
                            st.session_state.authenticated = True
                            st.session_state.user_id = user_id
                            st.session_state.user_email = email
                            st.rerun()
                        else:
                            st.error(f"登录失败: {response.json().get('msg', '未知错误')}")
                    except Exception as e:
                        st.error(f"登录失败: {e}")
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
                        auth_headers = {
                            "apikey": SUPABASE_KEY,
                            "Content-Type": "application/json"
                        }
                        auth_data = {"email": email, "password": password}
                        response = requests.post(auth_url, headers=auth_headers, json=auth_data)
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
        
        st.markdown(f"<h3 style='text-align: center;'>{t()['welcome']}, {st.session_state.user_email}</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        # 三个指标卡片
        col_sub1, col_sub2, col_sub3 = st.columns(3)
        with col_sub1:
            st.metric(t()["subscription"], "💎 Pro" if tier == "pro" else "🔒 Free")
        with col_sub2:
            if tier == "free":
                st.metric(t()["free_trial"], remaining)
            else:
                st.metric(t()["free_trial"], "∞")
        with col_sub3:
            # 总使用次数 + 刷新按钮放在同一卡片内
            col_usage, col_refresh = st.columns([3, 1])
            with col_usage:
                st.metric(t()["total_usage"], total_usage)
            with col_refresh:
                if st.button("🔄", key="refresh_btn", help="刷新数据"):
                    st.rerun()
        
        st.markdown("---")
        st.markdown(f"### {t()['nav_title']}")
        st.caption(t()["open_new_tab"])
        
        apps = {
            "📊 Product Feasibility": {
                "desc": "产品可行性分析 - 挖掘市场与用户之声",
                "desc_en": "Product Feasibility - Voice of Market & Users",
                "key": "feasibility",
                "url": APP_URLS["feasibility"]
            },
            "🔍 AI-DQA": {
                "desc": "设计风险分析 - AI赋能DFMEA",
                "desc_en": "Design Risk Analysis - AI-powered DFMEA",
                "key": "dqa",
                "url": APP_URLS["dqa"]
            },
            "📈 Para-Vary": {
                "desc": "蒙特卡洛模拟 - 累积公差仿真",
                "desc_en": "Monte Carlo Simulation - Tolerance Stack-up",
                "key": "paravary",
                "url": APP_URLS["paravary"]
            }
        }
        
        for app_name, app_info in apps.items():
            with st.container(border=True):
                col_name, col_desc, col_btn = st.columns([2, 3, 1])
                with col_name:
                    st.markdown(f"**{app_name}**")
                with col_desc:
                    desc = app_info["desc"] if st.session_state.lang == "zh" else app_info["desc_en"]
                    st.caption(desc)
                with col_btn:
                    lang_param = "zh" if st.session_state.lang == "zh" else "en"
                    full_url = f"{app_info['url']}?user_id={st.session_state.user_id}&email={st.session_state.user_email}&lang={lang_param}&trials_left={remaining}"
                    
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
        if response.status_code == 200:
            users = response.json()
        else:
            users = []
        
        pro_users = [u for u in users if u.get("subscription_tier") == "pro"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t()["total_users"], len(users))
        with col2:
            st.metric(t()["pro_users"], len(pro_users))
        with col3:
            st.metric(t()["free_users"], len(users) - len(pro_users))
        
        st.markdown("---")
        st.subheader(t()["user_list"])
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    t()["email_col"]: user.get("email"),
                    t()["subscription_col"]: "💎 Pro" if user.get("subscription_tier") == "pro" else "🔒 Free",
                    t()["trials_left"]: user.get("free_trials_remaining", 30),
                })
            st.dataframe(user_data, use_container_width=True)
        else:
            st.info("暂无用户数据")
        
        st.markdown("---")
        st.subheader(t()["subscription_mgmt"])
        
        if users:
            user_options = [f"{u.get('email')} ({u.get('subscription_tier')})" for u in users]
            selected_user_display = st.selectbox(t()["select_user"], user_options)
            selected_email = selected_user_display.split(" ")[0] if selected_user_display else None
            selected_user = next((u for u in users if u.get("email") == selected_email), None)
            
            if selected_user:
                col_sub1, col_sub2 = st.columns(2)
                with col_sub1:
                    current_tier = selected_user.get("subscription_tier", "free")
                    new_tier = st.selectbox(t()["set_subscription"], ["free", "pro"], 
                                            index=0 if current_tier == "free" else 1)
                with col_sub2:
                    new_trials = st.number_input(t()["set_trials"], min_value=0, max_value=100, 
                                                  value=selected_user.get("free_trials_remaining", 30))
                
                if st.button(t()["update_btn"], use_container_width=True):
                    patch_resp = supabase_patch("profiles", selected_user.get("id"), {
                        "subscription_tier": new_tier,
                        "free_trials_remaining": new_trials
                    })
                    if patch_resp.status_code in [200, 204]:
                        st.success(f"已更新 {selected_email}")
                        st.rerun()
                    else:
                        st.error(f"更新失败: {patch_resp.text}")
        
        st.markdown("---")
        st.subheader(t()["batch_ops"])
        if st.button(t()["reset_all_trials"], use_container_width=True):
            users_resp = supabase_get("profiles")
            if users_resp.status_code == 200:
                for user in users_resp.json():
                    if user.get("subscription_tier") == "free":
                        supabase_patch("profiles", user.get("id"), {"free_trials_remaining": 30})
                st.success("所有免费用户次数已重置为 30 次")
                st.rerun()
            else:
                st.error("重置失败")
        
    except Exception as e:
        st.warning(f"无法获取数据: {e}")
    
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
