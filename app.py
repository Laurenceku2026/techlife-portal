import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="TechLife Suite - AI Engineering Platform",
    page_icon="🔧",
    layout="wide"
)

# ==================== 多语言配置 ====================
TEXTS = {
    "zh": {
        "app_name": "TechLife Suite",
        "login_title": "🔐 登录到 TechLife Suite",
        "email": "邮箱地址",
        "password": "密码",
        "login_btn": "登录",
        "register_btn": "📝 注册新账号",
        "forgot_password": "🔑 忘记密码？",
        "logout": "🚪 登出",
        "free_trial": "免费试用次数",
        "remaining": "剩余",
        "today_used": "今日已用",
        "upgrade_to_pro": "💎 升级到专业版",
        "monthly": "月付 $29/月",
        "yearly": "年付 $299/年",
        "subscription": "订阅状态",
        "free_plan": "🔒 免费版",
        "pro_plan": "💎 专业版",
        "expires": "到期时间",
        "unlimited": "无限次",
        "contact": "📧 联系: Techlife2027@gmail.com",
        "admin_panel": "⚙️ 管理员",
        "users": "用户列表",
        "subscriptions": "订阅管理",
        "revenue": "收入统计",
        "nav_title": "🧭 应用导航",
        "welcome": "欢迎回来！",
        "feature_limit": "⚠️ 今日免费次数已用完，请升级到专业版",
        "admin_only": "仅限管理员访问",
        "upgrade_contact": "📞 如需升级到专业版，请联系管理员: Techlife2027@gmail.com",
        "used_info": "今日已使用 {used} / {total} 次",
    },
    "en": {
        "app_name": "TechLife Suite",
        "login_title": "🔐 Login to TechLife Suite",
        "email": "Email",
        "password": "Password",
        "login_btn": "Login",
        "register_btn": "📝 Register",
        "forgot_password": "🔑 Forgot Password?",
        "logout": "🚪 Logout",
        "free_trial": "Free Trials",
        "remaining": "remaining",
        "today_used": "Used today",
        "upgrade_to_pro": "💎 Upgrade to Pro",
        "monthly": "Monthly $29/month",
        "yearly": "Yearly $299/year",
        "subscription": "Subscription",
        "free_plan": "🔒 Free Plan",
        "pro_plan": "💎 Pro Plan",
        "expires": "Expires",
        "unlimited": "Unlimited",
        "contact": "📧 Contact: Techlife2027@gmail.com",
        "admin_panel": "⚙️ Admin",
        "users": "Users",
        "subscriptions": "Subscriptions",
        "revenue": "Revenue",
        "nav_title": "🧭 App Navigation",
        "welcome": "Welcome back!",
        "feature_limit": "⚠️ Daily free trials exceeded. Please upgrade to Pro.",
        "admin_only": "Admin access only",
        "upgrade_contact": "📞 Contact admin to upgrade: Techlife2027@gmail.com",
        "used_info": "Used {used} / {total} today",
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
    """检查并消耗免费试用次数，返回 (是否允许, 剩余次数, 消息)"""
    
    profile = get_user_subscription(user_id)
    tier = profile.get("subscription_tier", "free")
    remaining = profile.get("free_trials_remaining", 10)
    
    # 专业版用户无限使用
    if tier == "pro":
        expiry = profile.get("subscription_expires_at")
        if expiry and datetime.now() > datetime.fromisoformat(expiry):
            return False, 0, "订阅已过期，请联系管理员续费"
        return True, -1, "专业版无限使用"
    
    # 免费版用户检查次数
    used_today = get_today_usage(user_id, app_name)
    
    if used_today >= remaining:
        return False, remaining - used_today, t()["feature_limit"]
    
    # 记录使用
    supabase.table("usage_logs").insert({
        "user_id": user_id,
        "app_name": app_name,
        "analysis_count": 1,
        "used_at": datetime.now().isoformat()
    }).execute()
    
    return True, remaining - used_today - 1, f"{t()['remaining']}: {remaining - used_today - 1}"

def update_user_subscription(user_id: str, tier: str, months: int = 1):
    """更新用户订阅（管理员用）"""
    expires_at = None
    if tier == "pro":
        expires_at = (datetime.now() + timedelta(days=30 * months)).isoformat()
    
    supabase.table("profiles").update({
        "subscription_tier": tier,
        "subscription_expires_at": expires_at
    }).eq("id", user_id).execute()

# ==================== 登录/注册表单 ====================
def login_form():
    st.markdown(f"### {t()['login_title']}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input(t()["email"], key="login_email")
        password = st.text_input(t()["password"], type="password", key="login_password")
        
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
        
        col_reg, col_forgot = st.columns(2)
        with col_reg:
            if st.button(t()["register_btn"], use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
        with col_forgot:
            if st.button(t()["forgot_password"], use_container_width=True):
                st.session_state.reset_password = True
                st.rerun()

def register_form():
    st.markdown(f"### {t()['register_btn']}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input(t()["email"], key="reg_email")
        password = st.text_input(t()["password"], type="password", key="reg_password")
        confirm = st.text_input("确认密码", type="password", key="reg_confirm")
        
        if st.button("注册", type="primary", use_container_width=True):
            if not email or not password:
                st.warning("请填写邮箱和密码")
            elif password != confirm:
                st.warning("两次密码不一致")
            elif len(password) < 6:
                st.warning("密码至少6位")
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
                    st.error(f"注册失败: {str(e)}")
        
        if st.button("← 返回登录", use_container_width=True):
            st.session_state.show_register = False
            st.rerun()

# ==================== 管理员面板 ====================
def admin_panel():
    st.markdown("## ⚙️ 管理员面板")
    
    # 获取统计数据
    users = supabase.table("profiles").select("*", count="exact").execute()
    pro_users = supabase.table("profiles").select("*", count="exact")\
        .eq("subscription_tier", "pro").execute()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总用户数", users.count)
    with col2:
        st.metric("专业版用户", pro_users.count)
    with col3:
        st.metric("免费版用户", users.count - pro_users.count)
    
    st.markdown("---")
    
    # 用户列表
    st.subheader(t()["users"])
    user_list = []
    for user in users.data:
        user_list.append({
            "邮箱": user.get("email"),
            "订阅": user.get("subscription_tier"),
            "剩余次数": user.get("free_trials_remaining", 10),
            "到期时间": (user.get("subscription_expires_at", "") or "")[:10]
        })
    st.dataframe(user_list, use_container_width=True)
    
    # 手动调整订阅
    st.markdown("---")
    st.subheader(t()["subscriptions"])
    
    selected_email = st.selectbox("选择用户", [u.get("email") for u in users.data])
    new_tier = st.selectbox("设置订阅", ["free", "pro"])
    months = st.number_input("月数（专业版）", min_value=1, max_value=12, value=1)
    
    if st.button("更新订阅"):
        # 获取用户ID
        user = supabase.table("profiles").select("id").eq("email", selected_email).execute()
        if user.data:
            update_user_subscription(user.data[0]["id"], new_tier, months)
            st.success("已更新")
            st.rerun()

# ==================== 主应用 ====================
def main_app():
    # 语言切换和菜单
    col1, col2, col3, col4, col5 = st.columns([10, 1, 1, 1, 1])
    with col2:
        if st.button("中文"):
            st.session_state.lang = "zh"
            st.rerun()
    with col3:
        if st.button("English"):
            st.session_state.lang = "en"
            st.rerun()
    with col5:
        if st.button("⚙️", help="管理员入口"):
            # 检查是否是管理员（可以设置特定邮箱）
            admin_emails = ["techlife2027@gmail.com", "laurence_ku2002@yahoo.com.hk"]
            if st.session_state.user_email in admin_emails:
                st.session_state.admin_mode = not st.session_state.admin_mode
                st.rerun()
            else:
                st.warning(t()["admin_only"])
    
    # 侧边栏
    with st.sidebar:
        st.markdown(f"## 🔧 {t()['app_name']}")
        st.markdown("---")
        
        # 用户信息
        st.markdown(f"### 👤 {st.session_state.user_email}")
        
        # 订阅信息
        profile = get_user_subscription(st.session_state.user_id)
        tier = profile.get("subscription_tier", "free")
        remaining = profile.get("free_trials_remaining", 10)
        
        if tier == "pro":
            st.success(t()["pro_plan"])
            expiry = profile.get("subscription_expires_at")
            if expiry:
                st.caption(f"{t()['expires']}: {expiry[:10]}")
        else:
            st.info(t()["free_plan"])
            st.metric(t()["free_trial"], remaining)
        
        st.markdown("---")
        
        # 升级提示
        if tier == "free":
            st.info(t()["upgrade_contact"])
        
        st.markdown("---")
        st.markdown(f"### {t()['nav_title']}")
        
        # 应用列表
        apps = {
            "📊 Product Feasibility": "feasibility",
            "🔍 AI-DQA": "dqa",
            "📈 Para-Vary": "paravary"
        }
        
        app_urls = {
            "feasibility": st.secrets.get("APP_FEASIBILITY_URL", "https://product-feasibility.streamlit.app"),
            "dqa": st.secrets.get("APP_DQA_URL", "https://ai-dqa.streamlit.app"),
            "paravary": st.secrets.get("APP_PARAVARY_URL", "https://para-vary.streamlit.app")
        }
        
        for app_name, app_key in apps.items():
            col_btn, col_info = st.columns([3, 1])
            with col_btn:
                if st.button(app_name, key=app_key, use_container_width=True):
                    # 检查免费次数
                    allowed, remaining_count, msg = check_and_consume_trial(
                        st.session_state.user_id, app_key
                    )
                    if allowed:
                        redirect_url = f"{app_urls[app_key]}?user_id={st.session_state.user_id}&email={st.session_state.user_email}"
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', 
                                   unsafe_allow_html=True)
                    else:
                        st.error(msg)
            
            with col_info:
                if tier == "free":
                    used = get_today_usage(st.session_state.user_id, app_key)
                    st.caption(f"{used}/{remaining}")
        
        st.markdown("---")
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
    
    # 主内容
    if st.session_state.admin_mode:
        admin_panel()
    else:
        st.title(t()["app_name"])
        st.markdown("### AI 赋能的六西格玛设计平台")
        st.markdown(t()["welcome"])
        
        # 功能介绍
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            #### 📊 Product Feasibility
            智能产品可行性分析
            - 市场需求分析
            - 竞品对比
            - 技术可行性评估
            """)
        with col2:
            st.markdown("""
            #### 🔍 AI-DQA
            自动化设计风险分析
            - 风险识别
            - DFMEA 生成
            - 缓解措施建议
            """)
        with col3:
            st.markdown("""
            #### 📈 Para-Vary
            蒙特卡洛参数模拟
            - 灵敏度分析
            - 分布可视化
            - Cpk/PPM 计算
            """)

# ==================== 主程序 ====================
def main():
    if not st.session_state.authenticated:
        if st.session_state.show_register:
            register_form()
        elif st.session_state.reset_password:
            st.markdown("### 🔑 重置密码")
            st.info("请联系管理员重置密码: Techlife2027@gmail.com")
            if st.button("← 返回登录"):
                st.session_state.reset_password = False
                st.rerun()
        else:
            login_form()
    else:
        main_app()

if __name__ == "__main__":
    main()
