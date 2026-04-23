import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="TechLife Suite - AI Engineering Platform",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 多语言配置 ====================
TEXTS = {
    "zh": {
        # 侧边栏
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
        
        # 主界面
        "main_title": "TechLife Suite 门户",
        "main_subtitle": "一站式工程研发 AI 工具集",
        "email_placeholder": "请输入邮箱",
        "password_placeholder": "请输入密码",
        "login_btn": "登录",
        "register_btn": "注册新账号",
        "forgot_password": "忘记密码?",
        
        # 注册
        "register_title": "注册新账号",
        "confirm_password": "确认密码",
        "register_submit": "注册",
        "back_to_login": "返回登录",
        
        # 主应用
        "welcome": "欢迎回来",
        "logout": "登出",
        "free_trial": "免费次数",
        "remaining": "剩余",
        "subscription": "订阅",
        "free_plan": "免费版",
        "pro_plan": "专业版",
        "nav_title": "应用导航",
        "admin_panel": "管理员面板",
        
        # 按钮
        "chinese": "中文",
        "english": "English",
        
        # 管理员登录
        "admin_login_title": "管理员登录",
        "admin_username": "用户名",
        "admin_password": "密码",
        "admin_login_btn": "登录",
        "admin_back": "返回用户登录",
        "admin_error": "用户名或密码错误",
        
        # 管理员面板内容
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
        # Sidebar
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 About System",
        "about_text": """
**TechLife Suite** is an **AI-empowered DFSS (Design for Six Sigma)** platform designed specifically for R&D engineers.

We are committed to simplifying complex engineering design processes through AI technology, helping teams achieve:

- **Intelligent Requirement Analysis**: Rapidly decompose Voice of Customer (VOC).
- **Automated Risk Assessment**: AI-assisted generation of DFMEA.
- **Parameter Optimization**: Algorithm-driven search for optimal tolerances.

Let AI become your Chief Quality Engineer.
""",
        "contact_header": "📧 Contact Us",
        "contact_email": "Email: Techlife2027@gmail.com",
        
        # Main
        "main_title": "TechLife Suite Portal",
        "main_subtitle": "One-stop AI Toolkit for R&D Engineering",
        "email_placeholder": "Enter your email",
        "password_placeholder": "Enter your password",
        "login_btn": "LOG IN",
        "register_btn": "REGISTER",
        "forgot_password": "Forgot Password?",
        
        # Register
        "register_title": "Register New Account",
        "confirm_password": "Confirm Password",
        "register_submit": "Register",
        "back_to_login": "Back to Login",
        
        # Main app
        "welcome": "Welcome back",
        "logout": "Logout",
        "free_trial": "Free Trials",
        "remaining": "remaining",
        "subscription": "Subscription",
        "free_plan": "Free",
        "pro_plan": "Pro",
        "nav_title": "App Navigation",
        "admin_panel": "Admin Panel",
        
        # Buttons
        "chinese": "中文",
        "english": "English",
        
        # Admin login
        "admin_login_title": "Admin Login",
        "admin_username": "Username",
        "admin_password": "Password",
        "admin_login_btn": "Login",
        "admin_back": "Back to User Login",
        "admin_error": "Invalid username or password",
        
        # Admin panel content
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

# ==================== 管理员凭证 ====================
ADMIN_USERNAME = "Laurence_ku"
ADMIN_PASSWORD = "Ku_product$2026"

# ==================== 初始化 Supabase ====================
@st.cache_resource
def init_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

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
def get_user_subscription(user_id: str) -> dict:
    response = supabase.table("profiles")\
        .select("subscription_tier, free_trials_remaining, subscription_expires_at")\
        .eq("id", user_id)\
        .execute()
    if response.data:
        return response.data[0]
    return {"subscription_tier": "free", "free_trials_remaining": 10, "subscription_expires_at": None}

def get_today_usage(user_id: str, app_name: str) -> int:
    today = datetime.now().date().isoformat()
    response = supabase.table("usage_logs")\
        .select("analysis_count")\
        .eq("user_id", user_id)\
        .eq("app_name", app_name)\
        .gte("used_at", today)\
        .execute()
    return sum([log.get("analysis_count", 1) for log in response.data])

def check_and_consume_trial(user_id: str, app_name: str) -> tuple:
    profile = get_user_subscription(user_id)
    tier = profile.get("subscription_tier", "free")
    remaining = profile.get("free_trials_remaining", 10)
    
    if tier == "pro":
        expiry = profile.get("subscription_expires_at")
        if expiry and datetime.now() > datetime.fromisoformat(expiry):
            return False, 0, "订阅已过期"
        return True, -1, "专业版无限使用"
    
    used_today = get_today_usage(user_id, app_name)
    if used_today >= remaining:
        return False, remaining - used_today, f"今日免费次数已用完（{remaining}/{remaining}）"
    
    supabase.table("usage_logs").insert({
        "user_id": user_id,
        "app_name": app_name,
        "analysis_count": 1,
        "used_at": datetime.now().isoformat()
    }).execute()
    
    return True, remaining - used_today - 1, f"剩余 {remaining - used_today - 1} 次"

def update_user_subscription(user_id: str, tier: str, months: int = 1):
    expires_at = None
    if tier == "pro":
        expires_at = (datetime.now() + timedelta(days=30 * months)).isoformat()
    
    supabase.table("profiles").update({
        "subscription_tier": tier,
        "subscription_expires_at": expires_at
    }).eq("id", user_id).execute()

# ==================== 侧边栏（始终显示）====================
def render_sidebar():
    with st.sidebar:
        st.title(t()["sidebar_title"])
        
        st.subheader(t()["about_header"])
        st.markdown(t()["about_text"])
        
        st.divider()
        
        st.subheader(t()["contact_header"])
        st.markdown(t()["contact_email"])
        
        # 如果已登录，显示用户信息和登出按钮
        if st.session_state.authenticated:
            st.divider()
            st.markdown(f"**👤 {st.session_state.user_email}**")
            
            profile = get_user_subscription(st.session_state.user_id)
            tier = profile.get("subscription_tier", "free")
            st.caption(f"订阅: {'💎 专业版' if tier == 'pro' else '🔒 免费版'}")
            
            if st.button(t()["logout"], use_container_width=True):
                try:
                    supabase.auth.sign_out()
                except:
                    pass
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_email = None
                st.session_state.admin_mode = False
                st.rerun()

# ==================== 右上角按钮 ====================
def render_top_buttons():
    # 自定义 CSS - 使用更具体的选择器确保红底白字生效
    st.markdown("""
    <style>
    /* 全局按钮样式 - 确保中文和English按钮是红底白字 */
    .stButton button {
        border-radius: 8px !important;
        font-size: 16px !important;
        padding: 10px 20px !important;
    }
    
    /* 针对中文和English按钮的特定样式 - 使用 data-testid 和 key */
    button[kind="secondary"] {
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
    }
    
    /* 更通用的方式 - 通过按钮文本内容定位 */
    .stButton button:has(> div:contains("中文")),
    .stButton button:has(> div:contains("English")) {
        background-color: #dc3545 !important;
        color: white !important;
    }
    
    /* 输入框变大 */
    div[data-testid="stTextInput"] input {
        font-size: 20px !important;
        padding: 14px 18px !important;
        height: auto !important;
        border-radius: 12px !important;
        border: 1px solid #ddd !important;
    }
    
    /* 输入框聚焦效果 */
    div[data-testid="stTextInput"] input:focus {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 2px rgba(220,53,69,0.2) !important;
    }
    
    /* 主标题字体 */
    h1 {
        font-size: 52px !important;
        font-weight: 600 !important;
    }
    h2 {
        font-size: 36px !important;
    }
    h3 {
        font-size: 24px !important;
    }
    
    /* 登录按钮样式 */
    .stButton button[data-testid="baseButton-primary"] {
        background-color: #dc3545 !important;
        font-size: 18px !important;
        padding: 12px 24px !important;
    }
    
    /* 卡片样式 */
    div[data-testid="stContainer"] {
        border-radius: 16px !important;
    }
    
    /* 指标卡片样式 */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa !important;
        border-radius: 12px !important;
        padding: 16px !important;
        text-align: center !important;
    }
    </style>
    
    <script>
    // 简单的JavaScript辅助（Streamlit会自动处理）
    </script>
    """, unsafe_allow_html=True)
    
    # 使用 columns 布局
    col1, col2, col3, col4, col5 = st.columns([8, 1.2, 1.2, 1.2, 1])
    
    with col2:
        # 使用 st.markdown 包装按钮，确保样式
        st.markdown("""
        <style>
        .lang-btn {
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            width: 100%;
            font-weight: 600;
            cursor: pointer;
            text-align: center;
        }
        .lang-btn:hover {
            background-color: #c82333;
        }
        </style>
        """, unsafe_allow_html=True)
        
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

# ==================== 管理员登录表单 ====================
def render_admin_login_form():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['admin_login_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container(border=True):
            username = st.text_input(t()["admin_username"], key="admin_username")
            password = st.text_input(t()["admin_password"], type="password", key="admin_password")
            
            if st.button(t()["admin_login_btn"], use_container_width=True, type="primary"):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_mode = True
                    st.session_state.show_admin_login = False
                    st.session_state.authenticated = True  # 管理员也需要登录状态
                    st.session_state.user_email = "admin@techlife.com"
                    st.session_state.user_id = "admin"
                    st.rerun()
                else:
                    st.error(t()["admin_error"])
        
        if st.button(t()["admin_back"], use_container_width=True):
            st.session_state.show_admin_login = False
            st.rerun()

# ==================== 登录表单 ====================
def render_login_form():
    # 主标题（居中）
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center;'>{t()['main_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray; font-size: 18px;'>{t()['main_subtitle']}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # 登录表单容器（居中）
    col_form1, col_form2, col_form3 = st.columns([1, 2, 1])
    with col_form2:
        with st.container(border=True):
            email = st.text_input(t()["email_placeholder"], key="login_email")
            password = st.text_input(t()["password_placeholder"], type="password", key="login_password")
            
            if st.button(t()["login_btn"], use_container_width=True, type="primary"):
                if email and password:
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

# ==================== 注册表单 ====================
def render_register_form():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['register_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
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
                else:
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

# ==================== 忘记密码表单 ====================
def render_reset_password_form():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['forgot_password']}</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.info("请联系管理员重置密码")
            st.markdown(f"📧 {t()['contact_email']}")
        
        if st.button(t()["back_to_login"], use_container_width=True):
            st.session_state.reset_password = False
            st.rerun()

# ==================== 主应用（登录后）====================
def render_main_app():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # 获取用户信息
        profile = get_user_subscription(st.session_state.user_id)
        tier = profile.get("subscription_tier", "free")
        remaining = profile.get("free_trials_remaining", 10)
        
        # 欢迎信息
        st.markdown(f"<h3 style='text-align: center;'>{t()['welcome']}, {st.session_state.user_email}</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        # 订阅信息卡片
        col_sub1, col_sub2, col_sub3 = st.columns(3)
        with col_sub1:
            st.metric(t()["subscription"], "💎 Pro" if tier == "pro" else "🔒 Free")
        with col_sub2:
            if tier == "free":
                st.metric(t()["free_trial"], remaining)
            else:
                st.metric(t()["free_trial"], "∞")
        with col_sub3:
            used_today_feas = get_today_usage(st.session_state.user_id, "feasibility")
            used_today_dqa = get_today_usage(st.session_state.user_id, "dqa")
            used_today_para = get_today_usage(st.session_state.user_id, "paravary")
            total_used = used_today_feas + used_today_dqa + used_today_para
            st.metric("今日使用", f"{total_used}/{remaining if tier == 'free' else '∞'}")
        
        st.markdown("---")
        
        # 应用导航
        st.markdown(f"### {t()['nav_title']}")
        
        apps = {
            "📊 Product Feasibility": {
                "desc": "产品可行性分析 - 挖掘市场与用户之声",
                "url": st.secrets.get("APP_FEASIBILITY_URL", "https://product-feasibility.streamlit.app"),
                "key": "feasibility"
            },
            "🔍 AI-DQA": {
                "desc": "设计风险分析 - AI赋能DFMEA",
                "url": st.secrets.get("APP_DQA_URL", "https://ai-dqa.streamlit.app"),
                "key": "dqa"
            },
            "📈 Para-Vary": {
                "desc": "蒙特卡洛模拟 - 累积公差仿真",
                "url": st.secrets.get("APP_PARAVARY_URL", "https://para-vary.streamlit.app"),
                "key": "paravary"
            }
        }
        
        for app_name, app_info in apps.items():
            with st.container(border=True):
                col_name, col_desc, col_btn = st.columns([2, 3, 1])
                with col_name:
                    st.markdown(f"**{app_name}**")
                with col_desc:
                    st.caption(app_info["desc"])
                with col_btn:
                    if st.button("启动", key=app_info["key"], use_container_width=True):
                        allowed, _, msg = check_and_consume_trial(st.session_state.user_id, app_info["key"])
                        if allowed:
                            redirect_url = f"{app_info['url']}?user_id={st.session_state.user_id}&email={st.session_state.user_email}"
                            st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', unsafe_allow_html=True)
                        else:
                            st.error(msg)

# ==================== 管理员面板（完整功能）====================
def render_admin_panel():
    st.markdown(f"## ⚙️ {t()['admin_panel']}")
    
    # 获取所有用户数据
    users = supabase.table("profiles").select("*", count="exact").execute()
    pro_users = supabase.table("profiles").select("*", count="exact")\
        .eq("subscription_tier", "pro").execute()
    
    # 统计数据卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t()["total_users"], users.count)
    with col2:
        st.metric(t()["pro_users"], pro_users.count)
    with col3:
        st.metric(t()["free_users"], users.count - pro_users.count)
    with col4:
        # 计算总收入（假设专业版每月29美元）
        total_revenue = pro_users.count * 29
        st.metric("月收入 (USD)", f"${total_revenue}")
    
    st.markdown("---")
    
    # 用户列表
    st.subheader(t()["user_list"])
    
    if users.data:
        user_data = []
        for user in users.data:
            user_data.append({
                t()["email_col"]: user.get("email"),
                t()["subscription_col"]: "💎 Pro" if user.get("subscription_tier") == "pro" else "🔒 Free",
                t()["trials_left"]: user.get("free_trials_remaining", 10),
                t()["expires_col"]: (user.get("subscription_expires_at") or "")[:10] if user.get("subscription_expires_at") else "-",
                "user_id": user.get("id")
            })
        
        # 显示用户表格
        st.dataframe(
            [{k: v for k, v in u.items() if k != "user_id"} for u in user_data],
            use_container_width=True
        )
    else:
        st.info("暂无用户数据")
    
    st.markdown("---")
    
    # 订阅管理
    st.subheader(t()["subscription_mgmt"])
    
    if users.data:
        # 用户选择下拉框
        user_options = [f"{u.get('email')} ({u.get('subscription_tier')})" for u in users.data]
        selected_user_display = st.selectbox(t()["select_user"], user_options)
        
        # 提取选中的用户ID
        selected_email = selected_user_display.split(" ")[0] if selected_user_display else None
        
        # 当前订阅状态
        current_user = next((u for u in users.data if u.get("email") == selected_email), None)
        if current_user:
            st.info(f"当前订阅: **{current_user.get('subscription_tier')}** | 剩余次数: **{current_user.get('free_trials_remaining', 10)}**")
        
        col_sub1, col_sub2, col_sub3 = st.columns(3)
        with col_sub1:
            new_tier = st.selectbox(t()["set_subscription"], ["free", "pro"])
        with col_sub2:
            months = st.number_input(t()["months"], min_value=1, max_value=12, value=1)
        with col_sub3:
            if st.button(t()["update_btn"], use_container_width=True):
                if selected_email:
                    user = supabase.table("profiles").select("id").eq("email", selected_email).execute()
                    if user.data:
                        expires_at = None
                        if new_tier == "pro":
                            expires_at = (datetime.now() + timedelta(days=30 * months)).isoformat()
                        supabase.table("profiles").update({
                            "subscription_tier": new_tier,
                            "subscription_expires_at": expires_at,
                            "free_trials_remaining": 10 if new_tier == "free" else 999
                        }).eq("id", user.data[0]["id"]).execute()
                        st.success(f"已更新 {selected_email} 的订阅为 {new_tier}")
                        st.rerun()
    
    st.markdown("---")
    
    # 退出管理员模式
    if st.button(t()["exit_admin"], use_container_width=True):
        st.session_state.admin_mode = False
        st.session_state.authenticated = False
        st.rerun()

# ==================== 主程序 ====================
def main():
    # 始终渲染侧边栏
    render_sidebar()
    
    # 渲染右上角按钮
    render_top_buttons()
    
    # 根据状态渲染主内容
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
