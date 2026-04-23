import streamlit as st
from supabase import create_client, Client

# --- 1. 初始化配置 ---
st.set_page_config(page_title="TechLife Portal", layout="wide")

# --- 2. 模拟 Supabase 连接 (请确保在 Streamlit Secrets 中配置了这些) ---
# 这里为了演示不报错，先注释掉实际的连接，你需要确保你的 secrets 配置正确
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 3. 多语言字典 ---
translations = {
    "zh": {
        "app_title": "TechLife Suite 门户",
        "subtitle": "一站式工程研发 AI 工具集",
        "login": "登录",
        "register": "注册",
        "logout": "退出登录",
        "admin": "管理员入口",
        "language_toggle": "English",
        "email": "邮箱",
        "password": "密码",
    },
    "en": {
        "app_title": "TechLife Suite Portal",
        "subtitle": "One-stop AI Toolkit for R&D",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "admin": "Admin Panel",
        "language_toggle": "中文",
        "email": "Email",
        "password": "Password",
    }
}

# --- 4. 初始化 Session State ---
if 'language' not in st.session_state:
    st.session_state.language = 'zh'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# --- 5. 页面切换逻辑 ---
def switch_language():
    if st.session_state.language == 'zh':
        st.session_state.language = 'en'
    else:
        st.session_state.language = 'zh'
    # 强制重跑以更新界面
    st.rerun()

def go_to_admin():
    st.session_state.page = "admin"
    st.rerun()

def go_to_home():
    st.session_state.page = "home"
    st.rerun()

def login_success(email):
    st.session_state.logged_in = True
    st.session_state.user_email = email
    st.session_state.page = "home"
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.page = "home"
    st.rerun()

# --- 6. 页面组件 ---

def show_admin_panel():
    t = translations[st.session_state.language]
    st.header(f"🛠️ {t['admin']}")
    st.write("这里可以管理用户、查看订阅状态和充值记录。")
    st.button("返回主页", on_click=go_to_home)

def show_home():
    t = translations[st.session_state.language]

    # --- 顶部导航栏 (关键修改部分) ---
    # 创建一个顶部容器
    header_container = st.container()
    with header_container:
        # 使用列布局将内容推到最右边
        # col1 占据大部分宽度，col2 和 col3 占据右侧空间
        h_col1, h_col2, h_col3 = st.columns([10, 1, 1])

        with h_col2:
            # 语言切换按钮
            st.button(
                t['language_toggle'],
                on_click=switch_language,
                use_container_width=True
            )

        with h_col3:
            # 管理员入口 (齿轮图标)
            if st.session_state.logged_in:
                 # 这里可以加一个判断，比如只有特定邮箱才能看到管理员入口
                 # if st.session_state.user_email == "admin@techlife.com":
                st.button(
                    "⚙️",
                    on_click=go_to_admin,
                    help=t['admin'],
                    use_container_width=True
                )

    st.markdown("---") # 分割线

    # --- 主体内容 ---
    if not st.session_state.logged_in:
        # 登录/注册表单
        col1, col2 = st.columns([1, 1])
        with col1:
            st.header(t['login'])
            email = st.text_input(t['email'], key="login_email")
            password = st.text_input(t['password'], type="password", key="login_pwd")
            if st.button(t['login']):
                # 这里模拟登录成功
                # 实际应调用 supabase.auth.sign_in_with_password
                login_success(email)

        with col2:
            st.header(t['register'])
            r_email = st.text_input(t['email'], key="reg_email")
            r_pwd = st.text_input(t['password'], type="password", key="reg_pwd")
            if st.button(t['register']):
                # 这里模拟注册
                st.success("注册成功！请登录。")

    else:
        # 已登录状态
        st.success(f"已登录: {st.session_state.user_email}")
        if st.button(t['logout']):
            logout()

        st.subheader("🚀 欢迎使用 AI 工具集")
        st.write("这里将展示各种研发工具...")

# --- 7. 主程序入口 ---
def main():
    # 初始化页面状态
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    if st.session_state.page == 'admin':
        show_admin_panel()
    else:
        show_home()

if __name__ == "__main__":
    main()
