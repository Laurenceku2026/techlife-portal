import streamlit as st
from supabase import create_client, Client

# ================== 1. 语言配置字典 (在这里管理所有文字) ==================
# 这是一个简单的翻译表，你可以根据需要添加更多文字
TRANSLATIONS = {
    "zh": {
        "app_title": "🚀 TechLife Suite 门户",
        "app_desc": "一站式工程研发 AI 工具集",
        "login_tab": "登录",
        "signup_tab": "注册",
        "email_label": "邮箱",
        "password_label": "密码",
        "login_btn": "登录",
        "signup_btn": "注册",
        "logout_btn": "退出登录",
        "premium_status": "👑 高级会员",
        "free_status": "⚠️ 免费版",
        "upgrade_btn": "💳 升级会员",
        "welcome_msg": "🛠️ 我的工具箱",
        "tool_1_name": "1. 📊 产品可行性分析",
        "tool_1_desc": "基于25年经验的AI产品分析师。",
        "tool_2_name": "2. 🔍 AI 风险分析 (AI-DQA)",
        "tool_2_desc": "基于知识图谱的可靠性工程助手。",
        "tool_3_name": "3. 📐 公差分析 (Para-Vary)",
        "tool_3_desc": "蒙特卡洛模拟与公差堆叠分析。",
        "open_tool": "打开工具",
        "locked_msg": "🔒 仅限会员使用",
        "login_success": "登录成功！",
        "login_fail": "登录失败：",
        "signup_success": "注册成功！请检查邮箱验证。",
        "payment_success": "🎉 支付成功！您现在是高级会员！"
    },
    "en": {
        "app_title": "🚀 TechLife Suite Portal",
        "app_desc": "One-stop AI Toolkit for Engineering R&D",
        "login_tab": "Login",
        "signup_tab": "Sign Up",
        "email_label": "Email",
        "password_label": "Password",
        "login_btn": "Login",
        "signup_btn": "Sign Up",
        "logout_btn": "Logout",
        "premium_status": "👑 Premium Member",
        "free_status": "⚠️ Free Plan",
        "upgrade_btn": "💳 Upgrade ($9.9/mo)",
        "welcome_msg": "🛠️ My Toolkits",
        "tool_1_name": "1. 📊 Product Feasibility",
        "tool_1_desc": "AI analyst with 25 years of experience.",
        "tool_2_name": "2. 🔍 AI Risk Analysis (AI-DQA)",
        "tool_2_desc": "Knowledge graph based reliability assistant.",
        "tool_3_name": "3. 📐 Tolerance Analysis (Para-Vary)",
        "tool_3_desc": "Monte Carlo simulation & stack-up analysis.",
        "open_tool": "Open Tool",
        "locked_msg": "🔒 Premium Only",
        "login_success": "Login Successful!",
        "login_fail": "Login Failed: ",
        "signup_success": "Sign up successful! Please verify email.",
        "payment_success": "🎉 Payment Successful! You are Premium!"
    }
}

# ================== 2. 初始化设置 ==================
st.set_page_config(page_title="TechLife Suite", layout="centered")

# 初始化 Supabase (请确保在 Secrets 中配置了密钥)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 初始化语言状态 (默认为中文)
if "current_lang" not in st.session_state:
    st.session_state.current_lang = "zh"

# 初始化用户状态
if "user" not in st.session_state:
    st.session_state.user = None

# 获取当前语言的翻译函数
def t(key):
    return TRANSLATIONS[st.session_state.current_lang][key]

# ================== 3. 辅助函数 ==================
def sync_profile(user):
    if user:
        # 检查用户是否存在于 profiles 表
        data, count = supabase.table("profiles").select("id").eq("id", user.id).execute()
        if not data:
            supabase.table("profiles").insert({
                "id": user.id,
                "email": user.email,
                "is_premium": False
            }).execute()

def check_subscription(user_id):
    data, count = supabase.table("profiles").select("is_premium").eq("id", user_id).execute()
    if data and len(data) > 0:
        return data['is_premium']
    return False

# ================== 4. 顶部语言切换栏 ==================
def render_language_switcher():
    col1, col2 = st.columns() # 左边占位，右边放按钮
    with col2:
        # 使用分段控制器作为语言切换按钮
        lang_options = {"中文": "zh", "English": "en"}
        # 找到当前语言对应的标签
        current_label = [k for k, v in lang_options.items() if v == st.session_state.current_lang]
        
        # 当用户点击切换时，更新 session_state 并重新运行
        new_lang_label = st.segmented_control("Language", list(lang_options.keys()), default=current_label, key="lang_switcher")
        if lang_options[new_lang_label] != st.session_state.current_lang:
            st.session_state.current_lang = lang_options[new_lang_label]
            st.rerun()

# ================== 5. 主程序逻辑 ==================
def main():
    # 渲染顶部的语言切换器
    render_language_switcher()

    user = st.session_state.user

    # --- 场景 A: 用户未登录 ---
    if not user:
        st.title(t("app_title"))
        st.write(t("app_desc"))
        
        tab1, tab2 = st.tabs([t("login_tab"), t("signup_tab")])
        
        with tab1:
            email = st.text_input(t("email_label"), key="login_email")
            pwd = st.text_input(t("password_label"), type="password", key="login_pwd")
            if st.button(t("login_btn")):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                    if res.user:
                        st.session_state.user = res.user
                        sync_profile(res.user)
                        st.success(t("login_success"))
                        st.rerun()
                    else:
                        st.error(t("login_fail") + res.message)
                except Exception as e:
                    st.error(str(e))
        
        with tab2:
            new_email = st.text_input(t("email_label"), key="reg_email")
            new_pwd = st.text_input(t("password_label"), type="password", key="reg_pwd")
            if st.button(t("signup_btn")):
                try:
                    res = supabase.auth.sign_up({"email": new_email, "password": new_pwd})
                    if res.user:
                        st.success(t("signup_success"))
                        st.session_state.user = res.user
                        sync_profile(res.user)
                        st.rerun()
                except Exception as e:
                    st.error(str(e))

    # --- 场景 B: 用户已登录 ---
    else:
        is_premium = check_subscription(user.id)
        
        # 侧边栏
        st.sidebar.title(f"👤 {user.email}")
        if is_premium:
            st.sidebar.success(t("premium_status"))
        else:
            st.sidebar.warning(t("free_status"))
            if st.sidebar.button(t("upgrade_btn")):
                # 这里可以放 Stripe 链接
                st.info("支付功能开发中...")
        
        if st.sidebar.button(t("logout_btn")):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

        # 主界面
        st.title(t("welcome_msg"))
        
        # 工具 1
        st.subheader(t("tool_1_name"))
        st.write(t("tool_1_desc"))
        c1, c2 = st.columns()
        with c1:
            st.button(t("open_tool"), key="btn_1", use_container_width=True)
        with c2:
            if not is_premium:
                st.info(t("locked_msg"))
        st.markdown("---")

        # 工具 2
        st.subheader(t("tool_2_name"))
        st.write(t("tool_2_desc"))
        c1, c2 = st.columns()
        with c1:
            st.button(t("open_tool"), key="btn_2", use_container_width=True)
        with c2:
            if not is_premium:
                st.info(t("locked_msg"))

        st.markdown("---")

        # 工具 3
        st.subheader(t("tool_3_name"))
        st.write(t("tool_3_desc"))
        c1, c2 = st.columns()
        with c1:
            st.button(t("open_tool"), key="btn_3", use_container_width=True)
        with c2:
            if not is_premium:
                st.info(t("locked_msg"))

if __name__ == "__main__":
    main()
