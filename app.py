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
        # 通用
        "app_name": "TechLife Suite",
        "welcome_title": "欢迎来到 TechLife 工具集",
        "subtitle": "AI 赋能的六西格玛设计平台",
        
        # 侧边栏
        "about_system": "📘 关于系统",
        "about_system_title": "设计六西格玛 (DFSS) 的真正意义",
        "about_text": """
**什么是 DFSS？**

DFSS 的核心是回答一个根本问题：一个产品由多个组件组装而成，每个组件都有自己的公差和变异。当它们组合在一起时，组装后产品的最终变异是多少？我们如何才能获得最优的设计？

**DFSS 不是什么 vs 实际是什么：**

| 不是什么 | 实际是什么 |
|---------|-----------|
| 创造力的引擎 | 风险管控与返工减少的引擎 |
| 只为统计学家准备 | 理解 Y=f(x) 的实用方法 |
| 创新的保证 | 容纳创新的容器 |
| 总是需要6σ能力 | 成本与稳健性之间的权衡工具 |

**三种最实用的方法：**

1. **蒙特卡罗模拟** - 对于任何超过4个变量且具有非线性行为的公差累积，使用蒙特卡罗模拟将节省数月的生产调试时间
2. **AI自动化DFMEA** - 人的直觉很宝贵，但记忆有限。让AI记住每一个项目中的每一次失败
3. **量化市场需求** - 在量化市场需求之前不要进行任何设计。最好的DFSS执行也无法挽救一个没人想要的产品

**工具集：**
- 📊 Product Feasibility - 挖掘市场与用户之声
- 🔍 AI-DQA - 自动化设计风险分析
- 📈 Para-Vary - 累积公差蒙特卡罗仿真
""",
        "core_principles": "🎯 核心理念",
        "principle_1": "做对的产品，而不仅仅是把产品做对",
        "principle_2": "上游质量 - 在问题被设计进去之前就将其捕获",
        "principle_3": "AI将个人经验 + 行业知识 + 实时数据转化为可执行的结论",
        
        "contact": "📧 联系我们",
        "email": "Techlife2027@gmail.com",
        "author": "作者：古念松 (Laurence Ku)",
        "author_desc": "近30年研发经验 | 香港中文大学硕士 | 半导体、LED光学、智能家居、清洁电器",
        
        # 登录表单
        "login_title": "🔐 登录",
        "email": "邮箱地址",
        "password": "密码",
        "login_btn": "登录",
        "register_btn": "📝 注册新账号",
        "forgot_password": "🔑 忘记密码？",
        "demo_account": "💡 演示账号: techlife2027@gmail.com",
        
        # 注册表单
        "register_title": "📝 注册新账号",
        "confirm_password": "确认密码",
        "register_submit": "注册",
        "back_to_login": "← 返回登录",
        "password_mismatch": "两次输入的密码不一致",
        "password_too_short": "密码长度至少6位",
        "register_success": "注册成功！请登录",
        
        # 主界面
        "logout": "🚪 登出",
        "free_trial": "免费试用次数",
        "remaining": "剩余",
        "today_used": "今日已用",
        "upgrade_to_pro": "💎 升级到专业版",
        "subscription": "订阅状态",
        "free_plan": "🔒 免费版",
        "pro_plan": "💎 专业版",
        "expires": "到期时间",
        "unlimited": "无限次",
        "nav_title": "🧭 应用导航",
        "welcome": "欢迎回来！",
        "admin_only": "仅限管理员访问",
        "upgrade_contact": "📞 如需升级，请联系管理员",
        
        # 管理员面板
        "admin_panel": "⚙️ 管理员面板",
        "total_users": "总用户数",
        "pro_users": "专业版用户",
        "free_users": "免费版用户",
        "user_list": "用户列表",
        "subscription_mgmt": "订阅管理",
        "select_user": "选择用户",
        "set_subscription": "设置订阅",
        "months": "月数",
        "update_btn": "更新订阅",
        
        # 按钮
        "chinese": "中文",
        "english": "English",
        "admin_tooltip": "管理员入口",
    },
    "en": {
        # General
        "app_name": "TechLife Suite",
        "welcome_title": "Welcome to TechLife Toolset",
        "subtitle": "AI-Powered Design for Six Sigma Platform",
        
        # Sidebar
        "about_system": "📘 About System",
        "about_system_title": "The Truth of Design for Six Sigma",
        "about_text": """
**What is DFSS?**

The core of DFSS answers a fundamental question: A product is assembled from many components, each with its own tolerance and variation. When combined, what is the final variation of the assembly? How can we achieve an optimal design?

**What DFSS is NOT vs What it ACTUALLY IS:**

| What DFSS is NOT | What DFSS ACTUALLY IS |
|-----------------|----------------------|
| A creativity engine | A risk mitigation & rework reduction engine |
| Only for statisticians | A practical way to understand Y=f(x) |
| A guarantee of innovation | A container that organizes innovation |
| Always needing 6σ capability | A trade-off tool between cost and robustness |

**Three Most Practical Takeaways:**

1. **Monte Carlo Simulation** - Use for any stack-up with more than 4 variables and non-linear behavior. It will save months of debugging in production
2. **Automate DFMEA with AI** - Human intuition is valuable, but memory is limited. Let AI remember every failure from every project
3. **Quantify Market Need** - Do not design anything until you have quantified the market need. The best DFSS execution cannot save a product nobody wants

**Toolset:**
- 📊 Product Feasibility - Voice of Market & Users
- 🔍 AI-DQA - Automated Design Risk Analysis
- 📈 Para-Vary - Monte Carlo Tolerance Simulation
""",
        "core_principles": "🎯 Core Principles",
        "principle_1": "Make the right product - not just the product right",
        "principle_2": "Upstream quality - catch issues before they are designed in",
        "principle_3": "AI transforms experience + industry knowledge + real-time data into actionable insights",
        
        "contact": "📧 Contact Us",
        "email": "Techlife2027@gmail.com",
        "author": "Author: Laurence Ku",
        "author_desc": "30 years R&D experience | CUHK Mphil | Semiconductor, LED Optics, Smart Home, Floor Care",
        
        # Login form
        "login_title": "🔐 Login",
        "email": "Email",
        "password": "Password",
        "login_btn": "Login",
        "register_btn": "📝 Register",
        "forgot_password": "🔑 Forgot Password?",
        "demo_account": "💡 Demo: techlife2027@gmail.com",
        
        # Register form
        "register_title": "📝 Register New Account",
        "confirm_password": "Confirm Password",
        "register_submit": "Register",
        "back_to_login": "← Back to Login",
        "password_mismatch": "Passwords do not match",
        "password_too_short": "Password must be at least 6 characters",
        "register_success": "Registration successful! Please login.",
        
        # Main interface
        "logout": "🚪 Logout",
        "free_trial": "Free Trials",
        "remaining": "remaining",
        "today_used": "Used today",
        "upgrade_to_pro": "💎 Upgrade to Pro",
        "subscription": "Subscription",
        "free_plan": "🔒 Free Plan",
        "pro_plan": "💎 Pro Plan",
        "expires": "Expires",
        "unlimited": "Unlimited",
        "nav_title": "🧭 App Navigation",
        "welcome": "Welcome back!",
        "admin_only": "Admin access only",
        "upgrade_contact": "📞 Contact admin to upgrade",
        
        # Admin panel
        "admin_panel": "⚙️ Admin Panel",
        "total_users": "Total Users",
        "pro_users": "Pro Users",
        "free_users": "Free Users",
        "user_list": "User List",
        "subscription_mgmt": "Subscription Management",
        "select_user": "Select User",
        "set_subscription": "Set Subscription",
        "months": "Months",
        "update_btn": "Update Subscription",
        
        # Buttons
        "chinese": "中文",
        "english": "English",
        "admin_tooltip": "Admin Panel",
    }
}

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
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "show_register" not in st.session_state:
    st.session_state.show_register = False
if "reset_password" not in st.session_state:
    st.session_state.reset_password = False

def t():
    return TEXTS[st.session_state.lang]

# ==================== 辅助函数 ====================
def get_user_subscription(user_id: str) -> dict:
    """获取用户订阅信息"""
    response = supabase.table("profiles")\
        .select("subscription_tier, free_trials_remaining, subscription_expires_at")\
        .eq("id", user_id)\
        .execute()
    
    if response.data:
        return response.data[0]
    return {"subscription_tier": "free", "free_trials_remaining": 10, "subscription_expires_at": None}

def get_today_usage(user_id: str, app_name: str) -> int:
    """获取今日使用次数"""
    today = datetime.now().date().isoformat()
    response = supabase.table("usage_logs")\
        .select("analysis_count")\
        .eq("user_id", user_id)\
        .eq("app_name", app_name)\
        .gte("used_at", today)\
        .execute()
    
    return sum([log.get("analysis_count", 1) for log in response.data])

def check_and_consume_trial(user_id: str, app_name: str) -> tuple:
    """检查并消耗免费试用次数"""
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
        return False, remaining - used_today, t()["feature_limit"] if "feature_limit" in t() else "今日免费次数已用完"
    
    supabase.table("usage_logs").insert({
        "user_id": user_id,
        "app_name": app_name,
        "analysis_count": 1,
        "used_at": datetime.now().isoformat()
    }).execute()
    
    return True, remaining - used_today - 1, f"{t()['remaining']}: {remaining - used_today - 1}"

def update_user_subscription(user_id: str, tier: str, months: int = 1):
    """更新用户订阅"""
    expires_at = None
    if tier == "pro":
        expires_at = (datetime.now() + timedelta(days=30 * months)).isoformat()
    
    supabase.table("profiles").update({
        "subscription_tier": tier,
        "subscription_expires_at": expires_at
    }).eq("id", user_id).execute()

# ==================== UI 组件 ====================
def render_language_switcher():
    """渲染语言切换按钮"""
    col1, col2, col3, col4 = st.columns([10, 1, 1, 1])
    with col2:
        if st.button(t()["chinese"], key="lang_zh", use_container_width=True):
            if st.session_state.lang != "zh":
                st.session_state.lang = "zh"
                st.rerun()
    with col3:
        if st.button(t()["english"], key="lang_en", use_container_width=True):
            if st.session_state.lang != "en":
                st.session_state.lang = "en"
                st.rerun()
    with col4:
        if st.button("⚙️", key="admin_btn", help=t()["admin_tooltip"], use_container_width=True):
            admin_emails = ["techlife2027@gmail.com", "laurence_ku2002@yahoo.com.hk"]
            if st.session_state.get("user_email") in admin_emails:
                st.session_state.admin_mode = not st.session_state.admin_mode
                st.rerun()
            else:
                st.warning(t()["admin_only"])
    return col1, col2, col3, col4

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown(f"## 🔧 {t()['app_name']}")
        st.markdown("---")
        
        # 关于系统
        st.markdown(f"### {t()['about_system']}")
        with st.expander(t()["about_system_title"], expanded=True):
            st.markdown(t()["about_text"])
        
        st.markdown("---")
        
        # 核心理念
        st.markdown(f"### {t()['core_principles']}")
        st.info(f"✅ {t()['principle_1']}")
        st.info(f"✅ {t()['principle_2']}")
        st.info(f"✅ {t()['principle_3']}")
        
        st.markdown("---")
        
        # 联系信息
        st.markdown(f"### {t()['contact']}")
        st.markdown(f"✉️ {t()['email']}")
        st.markdown("---")
        st.caption(t()["author"])
        st.caption(t()["author_desc"])

def render_login_form():
    """渲染登录表单（居中）"""
    # 使用 columns 实现居中
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 标题
        st.markdown(f"<h2 style='text-align: center;'>{t()['login_title']}</h2>", unsafe_allow_html=True)
        st.markdown("")
        
        # 登录表单容器
        with st.container(border=True):
            email = st.text_input(t()["email"], key="login_email", placeholder="your@email.com")
            password = st.text_input(t()["password"], type="password", key="login_password", placeholder="••••••••")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button(t()["login_btn"], type="primary", use_container_width=True):
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
        
        # 注册和忘记密码链接
        col_reg, col_forgot = st.columns(2)
        with col_reg:
            if st.button(t()["register_btn"], use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
        with col_forgot:
            if st.button(t()["forgot_password"], use_container_width=True):
                st.session_state.reset_password = True
                st.rerun()
        
        # 演示账号提示
        st.caption(t()["demo_account"])

def render_register_form():
    """渲染注册表单"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['register_title']}</h2>", unsafe_allow_html=True)
        
        with st.container(border=True):
            email = st.text_input(t()["email"], key="reg_email", placeholder="your@email.com")
            password = st.text_input(t()["password"], type="password", key="reg_password", placeholder="••••••••")
            confirm = st.text_input(t()["confirm_password"], type="password", key="reg_confirm", placeholder="••••••••")
            
            if st.button(t()["register_submit"], type="primary", use_container_width=True):
                if not email or not password:
                    st.warning("请填写邮箱和密码")
                elif password != confirm:
                    st.warning(t()["password_mismatch"])
                elif len(password) < 6:
                    st.warning(t()["password_too_short"])
                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": email,
                            "password": password
                        })
                        st.success(t()["register_success"])
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
    """渲染重置密码表单"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"<h2 style='text-align: center;'>{t()['forgot_password']}</h2>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.info("请联系管理员重置密码")
            st.markdown(f"📧 {t()['email']}")
        
        if st.button(t()["back_to_login"], use_container_width=True):
            st.session_state.reset_password = False
            st.rerun()

def render_admin_panel():
    """渲染管理员面板"""
    st.markdown(f"## {t()['admin_panel']}")
    
    # 统计数据
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
    
    # 用户列表
    st.subheader(t()["user_list"])
    user_data = []
    for user in users.data:
        user_data.append({
            "Email": user.get("email"),
            "Subscription": user.get("subscription_tier"),
            "Trials Left": user.get("free_trials_remaining", 10),
            "Expires": (user.get("subscription_expires_at") or "")[:10] if user.get("subscription_expires_at") else "-"
        })
    st.dataframe(user_data, use_container_width=True)
    
    # 订阅管理
    st.markdown("---")
    st.subheader(t()["subscription_mgmt"])
    
    selected_email = st.selectbox(t()["select_user"], [u.get("email") for u in users.data])
    new_tier = st.selectbox(t()["set_subscription"], ["free", "pro"])
    months = st.number_input(t()["months"], min_value=1, max_value=12, value=1)
    
    if st.button(t()["update_btn"]):
        user = supabase.table("profiles").select("id").eq("email", selected_email).execute()
        if user.data:
            update_user_subscription(user.data[0]["id"], new_tier, months)
            st.success("已更新")
            st.rerun()

def render_main_app():
    """渲染主应用（登录后）"""
    # 语言切换和管理员按钮
    render_language_switcher()
    
    # 侧边栏
    render_sidebar()
    
    # 主内容
    if st.session_state.admin_mode:
        render_admin_panel()
        return
    
    # 欢迎标题（居中）
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center;'>{t()['welcome_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>{t()['subtitle']}</p>", unsafe_allow_html=True)
        st.markdown("---")
    
    # 用户信息卡片
    profile = get_user_subscription(st.session_state.user_id)
    tier = profile.get("subscription_tier", "free")
    remaining = profile.get("free_trials_remaining", 10)
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric(t()["subscription"], "💎 Pro" if tier == "pro" else "🔒 Free")
    with col_info2:
        if tier == "free":
            st.metric(t()["free_trial"], remaining)
        else:
            st.metric(t()["subscription"], t()["unlimited"])
    with col_info3:
        if tier == "pro":
            expiry = profile.get("subscription_expires_at")
            if expiry:
                st.metric(t()["expires"], expiry[:10])
    
    st.markdown("---")
    
    # 应用导航
    st.markdown(f"### {t()['nav_title']}")
    
    apps = {
        "📊 Product Feasibility": {
            "desc": "挖掘市场与用户之声 | 产品可行性分析",
            "url": st.secrets.get("APP_FEASIBILITY_URL", "https://product-feasibility.streamlit.app"),
            "key": "feasibility"
        },
        "🔍 AI-DQA": {
            "desc": "自动化设计风险分析 | AI赋能DFMEA",
            "url": st.secrets.get("APP_DQA_URL", "https://ai-dqa.streamlit.app"),
            "key": "dqa"
        },
        "📈 Para-Vary": {
            "desc": "累积公差蒙特卡罗仿真 | 参数灵敏度分析",
            "url": st.secrets.get("APP_PARAVARY_URL", "https://para-vary.streamlit.app"),
            "key": "paravary"
        }
    }
    
    for app_name, app_info in apps.items():
        with st.container(border=True):
            col_app_name, col_app_desc, col_app_btn = st.columns([2, 3, 1])
            with col_app_name:
                st.markdown(f"### {app_name}")
            with col_app_desc:
                st.markdown(app_info["desc"])
            with col_app_btn:
                if st.button("启动 →", key=app_info["key"], use_container_width=True):
                    allowed, _, msg = check_and_consume_trial(st.session_state.user_id, app_info["key"])
                    if allowed:
                        redirect_url = f"{app_info['url']}?user_id={st.session_state.user_id}&email={st.session_state.user_email}"
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', unsafe_allow_html=True)
                    else:
                        st.error(msg)
    
    st.markdown("---")
    
    # 登出按钮
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
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

# ==================== 主程序 ====================
def main():
    # 自定义 CSS
    st.markdown("""
    <style>
    .stButton button {
        border-radius: 8px;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 8px;
    }
    .stMetric {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        if st.session_state.show_register:
            render_register_form()
        elif st.session_state.reset_password:
            render_reset_password_form()
        else:
            # 未登录时也显示侧边栏
            render_sidebar()
            render_login_form()
    else:
        render_main_app()

if __name__ == "__main__":
    main()
