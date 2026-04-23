import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import stripe  # 需要安装：pip install stripe

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
        "upgrade_to_pro": "升级到专业版",
        "monthly": "月付 $29/月",
        "yearly": "年付 $299/年 (省 $49)",
        "subscription": "订阅状态",
        "free_plan": "🔒 免费版",
        "pro_plan": "💎 专业版",
        "expires": "到期时间",
        "unlimited": "无限次",
        "used_today": "今日已用",
        "contact": "联系: Techlife2027@gmail.com",
        "admin_panel": "⚙️ 管理员",
        "users": "用户",
        "subscriptions": "订阅",
        "revenue": "收入",
        "nav_title": "🧭 应用导航",
        "welcome": "欢迎回来！",
        "feature_limit": "今日免费次数已用完，请升级到专业版",
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
        "free_trial": "Free Trials Remaining",
        "remaining": "remaining",
        "upgrade_to_pro": "Upgrade to Pro",
        "monthly": "Monthly $29/month",
        "yearly": "Yearly $299/year (Save $49)",
        "subscription": "Subscription",
        "free_plan": "🔒 Free Plan",
        "pro_plan": "💎 Pro Plan",
        "expires": "Expires",
        "unlimited": "Unlimited",
        "used_today": "Used today",
        "contact": "Contact: Techlife2027@gmail.com",
        "admin_panel": "⚙️ Admin",
        "users": "Users",
        "subscriptions": "Subscriptions",
        "revenue": "Revenue",
        "nav_title": "🧭 App Navigation",
        "welcome": "Welcome back!",
        "feature_limit": "Daily free trials exceeded. Please upgrade to Pro.",
    }
}

# ==================== 初始化 Supabase ====================
@st.cache_resource
def init_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# ==================== 初始化 Stripe ====================
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

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

t = lambda: TEXTS[st.session_state.lang]

# ==================== 辅助函数 ====================
def check_and_consume_trial(user_id: str, app_name: str) -> tuple:
    """检查并消耗免费试用次数，返回 (是否允许, 剩余次数, 消息)"""
    
    # 获取用户订阅信息
    response = supabase.table("profiles")\
        .select("subscription_tier, free_trials_remaining")\
        .eq("id", user_id)\
        .execute()
    
    if not response.data:
        return False, 0, "用户不存在"
    
    profile = response.data[0]
    tier = profile.get("subscription_tier", "free")
    remaining = profile.get("free_trials_remaining", 0)
    
    # 专业版用户无限使用
    if tier == "pro":
        # 检查订阅是否过期
        expiry = profile.get("subscription_expires_at")
        if expiry and datetime.now() > datetime.fromisoformat(expiry):
            return False, 0, "订阅已过期，请续费"
        return True, -1, "专业版无限使用"
    
    # 免费版用户检查次数
    # 检查今日已用次数
    today = datetime.now().date().isoformat()
    usage_response = supabase.table("usage_logs")\
        .select("analysis_count")\
        .eq("user_id", user_id)\
        .eq("app_name", app_name)\
        .gte("used_at", today)\
        .execute()
    
    used_today = sum([log.get("analysis_count", 1) for log in usage_response.data])
    
    if used_today >= remaining:
        return False, remaining - used_today, "今日免费次数已用完"
    
    # 记录使用
    supabase.table("usage_logs").insert({
        "user_id": user_id,
        "app_name": app_name,
        "analysis_count": 1,
        "used_at": datetime.now().isoformat()
    }).execute()
    
    return True, remaining - used_today - 1, f"剩余 {remaining - used_today - 1} 次"

def create_checkout_session(user_id: str, price_id: str, success_url: str, cancel_url: str):
    """创建 Stripe 结账会话"""
    session = stripe.checkout.Session.create(
        customer_email=st.session_state.user_email,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={'user_id': user_id}
    )
    return session.url

def handle_successful_payment(session_id: str):
    """处理成功支付后的订阅更新"""
    session = stripe.checkout.Session.retrieve(session_id)
    user_id = session.metadata.get('user_id')
    subscription = stripe.Subscription.retrieve(session.subscription)
    
    # 更新数据库
    supabase.table("profiles").update({
        "subscription_tier": "pro",
        "subscription_expires_at": datetime.fromtimestamp(subscription.current_period_end).isoformat()
    }).eq("id", user_id).execute()
    
    # 记录支付
    supabase.table("payments").insert({
        "user_id": user_id,
        "amount": session.amount_total / 100,
        "plan_type": "monthly" if "monthly" in session.metadata.get("plan", "") else "yearly",
        "transaction_id": session.payment_intent,
        "status": "completed",
        "expires_at": datetime.fromtimestamp(subscription.current_period_end).isoformat()
    }).execute()

# ==================== 登录/注册 ====================
def login_form():
    st.markdown(f"### {t()['login_title']}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input(t()["email"], key="login_email")
        password = st.text_input(t()["password"], type="password", key="login_password")
        
        if st.button(t()["login_btn"], type="primary", use_container_width=True):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email, "password": password
                })
                st.session_state.authenticated = True
                st.session_state.user_id = response.user.id
                st.session_state.user_email = response.user.email
                st.rerun()
            except Exception as e:
                st.error(f"登录失败: {str(e)}")
        
        col_reg, col_forgot = st.columns(2)
        with col_reg:
            if st.button(t()["register_btn"], use_container_width=True):
                st.session_state.show_register = True
        with col_forgot:
            if st.button(t()["forgot_password"], use_container_width=True):
                st.session_state.reset_password = True

# ==================== 管理员面板 ====================
def admin_panel():
    st.markdown("## ⚙️ 管理员面板")
    
    # 获取统计数据
    users = supabase.table("profiles").select("*", count="exact").execute()
    pro_users = supabase.table("profiles").select("*", count="exact")\
        .eq("subscription_tier", "pro").execute()
    payments = supabase.table("payments").select("amount").execute()
    total_revenue = sum([p.get("amount", 0) for p in payments.data])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总用户数", users.count)
    with col2:
        st.metric("专业版用户", pro_users.count)
    with col3:
        st.metric("免费版用户", users.count - pro_users.count)
    with col4:
        st.metric("总收入 (USD)", f"${total_revenue:.2f}")
    
    st.markdown("---")
    
    # 用户列表
    st.subheader("用户列表")
    user_data = []
    for user in users.data:
        user_data.append({
            "邮箱": user.get("email"),
            "订阅": user.get("subscription_tier"),
            "剩余次数": user.get("free_trials_remaining", 0),
            "注册时间": user.get("created_at", "")[:10]
        })
    st.dataframe(user_data, use_container_width=True)
    
    # 手动调整用户订阅
    st.markdown("---")
    st.subheader("手动调整订阅")
    selected_email = st.selectbox("选择用户", [u.get("email") for u in users.data])
    new_tier = st.selectbox("设置订阅", ["free", "pro"])
    
    if st.button("更新订阅"):
        supabase.table("profiles").update({"subscription_tier": new_tier})\
            .eq("email", selected_email).execute()
        st.success("已更新")
        st.rerun()

# ==================== 主应用 ====================
def main_app():
    # 语言切换
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
            if st.session_state.user_email == "techlife2027@gmail.com":  # 管理员邮箱
                st.session_state.admin_mode = not st.session_state.admin_mode
                st.rerun()
            else:
                st.warning("仅限管理员")
    
    # 侧边栏
    with st.sidebar:
        st.markdown(f"## 🔧 {t()['app_name']}")
        st.markdown("---")
        
        # 用户信息
        st.markdown(f"### 👤 {st.session_state.user_email}")
        
        # 订阅信息
        response = supabase.table("profiles")\
            .select("subscription_tier, free_trials_remaining, subscription_expires_at")\
            .eq("id", st.session_state.user_id).execute()
        
        if response.data:
            profile = response.data[0]
            tier = profile.get("subscription_tier", "free")
            remaining = profile.get("free_trials_remaining", 10)
            expires_at = profile.get("subscription_expires_at")
            
            if tier == "pro":
                st.success(f"{t()['pro_plan']}")
                if expires_at:
                    st.caption(f"{t()['expires']}: {expires_at[:10]}")
            else:
                st.info(f"{t()['free_plan']}")
                st.metric(t()["free_trial"], remaining)
        
        st.markdown("---")
        
        # 升级按钮
        if tier == "free":
            st.markdown(f"### {t()['upgrade_to_pro']}")
            if st.button(t()["monthly"], use_container_width=True):
                # 创建 Stripe 结账
                session_url = create_checkout_session(
                    st.session_state.user_id,
                    "price_monthly_id",  # 在 Stripe 创建
                    "https://app.techlife-suite.com/success",
                    "https://app.techlife-suite.com/cancel"
                )
                st.markdown(f'<meta http-equiv="refresh" content="0; url={session_url}">', 
                           unsafe_allow_html=True)
            
            if st.button(t()["yearly"], use_container_width=True):
                session_url = create_checkout_session(
                    st.session_state.user_id,
                    "price_yearly_id",  # 在 Stripe 创建
                    "https://app.techlife-suite.com/success",
                    "https://app.techlife-suite.com/cancel"
                )
                st.markdown(f'<meta http-equiv="refresh" content="0; url={session_url}">', 
                           unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"### {t()['nav_title']}")
        
        # 应用列表
        apps = {
            "📊 Product Feasibility": "feasibility",
            "🔍 AI-DQA": "dqa",
            "📈 Para-Vary": "paravary"
        }
        
        for app_name, app_key in apps.items():
            if st.button(app_name, use_container_width=True):
                # 检查免费次数
                allowed, remaining, msg = check_and_consume_trial(
                    st.session_state.user_id, app_key
                )
                if allowed:
                    redirect_url = f"https://{app_key}.streamlit.app?user_id={st.session_state.user_id}"
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', 
                               unsafe_allow_html=True)
                else:
                    st.error(msg)
        
        st.markdown("---")
        if st.button(t()["logout"], use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.authenticated = False
            st.rerun()
    
    # 主内容
    if st.session_state.admin_mode:
        admin_panel()
    else:
        st.title(t()["app_name"])
        st.markdown(f"### {t()['welcome']}")
        
        # 功能介绍
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 📊 Product Feasibility\n产品可行性分析")
        with col2:
            st.markdown("#### 🔍 AI-DQA\n设计风险分析")
        with col3:
            st.markdown("#### 📈 Para-Vary\n蒙特卡洛模拟")

# ==================== 主程序 ====================
def main():
    if not st.session_state.authenticated:
        login_form()
    else:
        main_app()

if __name__ == "__main__":
    main()
