import streamlit as st
from supabase import create_client, Client

# --- 1. 页面配置 ---
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
        "subtitle": "All-in-One AI Toolkit for R&D Engineering",
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

# --- 5. 切换语言函数 ---
def toggle_language():
    if st.session_state.language == 'zh':
        st.session_state.language = 'en'
    else:
        st.session_state.language = 'zh'

# --- 6. 获取当前语言文本 ---
t = translations[st.session_state.language]

# --- 7. 侧边栏 (Sidebar) ---
with st.sidebar:
    st.header("🚀 TechLife Suite")

    # 关于系统介绍
    st.subheader("📘 关于系统")
    if st.session_state.language == 'zh':
        st.markdown("""
        **TechLife Suite** 是专为研发工程师打造的 **AI 赋能 DFSS（六西格玛设计）** 平台。
        
        我们致力于通过人工智能技术，简化复杂的工程设计流程，帮助团队实现：
        
        - **智能需求分析**：快速拆解客户之声 (VOC)。
        - **自动化风险评估**：AI 辅助生成 DFMEA。
        - **参数优化设计**：利用算法寻找最优容差。
        
        让 AI 成为您的首席质量工程师。
        """)
    else:
        st.markdown("""
        **TechLife Suite** is an **AI-empowered DFSS (Design for Six Sigma)** platform designed for R&D engineers.
        
        We aim to simplify complex engineering design processes through AI, helping teams achieve:
        
        - **Smart Requirement Analysis**: Rapidly decompose Voice of Customer (VOC).
        - **Automated Risk Assessment**: AI-assisted DFMEA generation.
        - **Parameter Optimization**: Algorithm-driven tolerance design.
        
        Let AI be your Chief Quality Engineer.
        """)

    st.divider()

    # 联系方式
    st.markdown("### 📧 联系我们")
    st.markdown("Email: Techlife2027@gmail.com")

# --- 8. 主界面布局 ---
# 使用容器来控制右上角布局
header_container = st.container()
with header_container:
    # 创建两列，左边占大部分，右边放按钮
    col1, col2 = st.columns([10, 1])

    with col1:
        # 左上角可以放标题（可选）
        pass

    with col2:
        # 右上角：语言切换 + 管理员入口
        # 使用两列来并排显示
        lang_col, admin_col = st.columns([1, 1])

        with lang_col:
            # 语言切换按钮
            st.button(
                t["language_toggle"],
                on_click=toggle_language,
                key="lang_btn",
                help="切换语言 / Switch Language"
            )

        with admin_col:
            # 管理员入口（齿轮图标）
            st.button(
                "⚙️",
                key="admin_btn",
                help=t["admin"],
                on_click=lambda: st.toast("管理员功能开发中...", icon="🚧")
            )

# --- 9. 主内容区 ---
st.markdown("<br><br>", unsafe_allow_html=True)  # 增加一点顶部间距

# 居中显示欢迎信息
col_center_1, col_center_2, col_center_3 = st.columns([1, 2, 1])
with col_center_2:
    st.markdown(f"<h1 style='text-align: center;'>{t['app_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray;'>{t['subtitle']}</p>", unsafe_allow_html=True)

    st.markdown("---")

    # 登录表单
    with st.form("login_form"):
        email = st.text_input(t["email"])
        password = st.text_input(t["password"], type="password")

        # 提交按钮
        submitted = st.form_submit_button(t["login"])
        if submitted:
            # 这里只是演示，实际应调用 Supabase 登录
            if email and password:
                st.session_state.logged_in = True
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("请输入邮箱和密码")

    # 注册按钮（放在登录下方）
    if st.button(t["register"]):
        st.info("注册功能开发中...")

# --- 10. 登录后显示的内容（演示用） ---
if st.session_state.logged_in:
    st.success("您已登录！这里是您的仪表盘。")
    if st.button(t["logout"]):
        st.session_state.logged_in = False
        st.rerun()
