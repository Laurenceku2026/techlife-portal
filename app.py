import streamlit as st

# --- 1. 页面配置 ---
st.set_page_config(page_title="TechLife Suite", layout="wide")

# --- 2. 初始化 Session State ---
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# --- 3. 多语言字典 ---
translations = {
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
        "email_label": "邮箱: Techlife2027@gmail.com",
        "main_title": "TechLife Suite 门户",
        "main_subtitle": "一站式工程研发 AI 工具集",
        "email_placeholder": "请输入邮箱",
        "password_placeholder": "请输入密码",
        "login_btn": "登 录",
        "register_btn": "注 册"
    },
    "en": {
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 About System",
        "about_text": """
        **TechLife Suite** is a platform designed for R&D engineers, featuring **AI-empowered DFSS**.

        We are committed to simplifying complex engineering design processes through AI:

        - **Intelligent Requirement Analysis**: Rapidly deconstruct Voice of Customer (VOC).
        - **Automated Risk Assessment**: AI-assisted DFMEA generation.
        - **Parameter Optimization**: Find optimal tolerances using algorithms.

        Let AI become your Chief Quality Engineer.
        """,
        "contact_header": "📧 Contact Us",
        "email_label": "Email: Techlife2027@gmail.com",
        "main_title": "TechLife Suite Portal",
        "main_subtitle": "One-stop AI Toolkit for R&D Engineering",
        "email_placeholder": "Please enter email",
        "password_placeholder": "Please enter password",
        "login_btn": "LOG IN",
        "register_btn": "REGISTER"
    }
}

t = translations[st.session_state.language]

# --- 4. 核心 CSS 样式 (修复颜色和边框) ---
st.markdown("""
    <style>
    /* 1. 强制覆盖输入框样式：白底、黑框、直角 */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input {
        background-color: #FFFFFF !important; /* 纯白背景 */
        color: #000000 !important; /* 黑色文字 */
        border: 1px solid #000000 !important; /* 黑色边框 */
        border-radius: 0px !important; /* 直角 */
        height: 50px !important;
        font-size: 16px !important;
        box-shadow: none !important;
    }

    /* 2. 修复占位符颜色 (灰色) */
    ::placeholder {
        color: #888888 !important;
        opacity: 1;
    }

    /* 3. 登录按钮：黑底白字，直角 */
    .stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #000000 !important;
        border-radius: 0px !important;
        height: 50px !important;
        font-size: 18px !important;
        width: 100%;
        font-weight: bold;
    }

    /* 4. 注册按钮：白底黑框黑字，直角 */
    .register-btn > div > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 0px !important;
        height: 50px !important;
        font-size: 16px !important;
        width: 100%;
    }

    /* 5. 移除 Streamlit 默认的内边距，让布局更紧凑 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. 顶部语言切换 ---
col1, col2, col3 = st.columns([1, 1, 1])
with col3:
    # 简单的按钮组切换语言
    c1, c2 = st.columns(2)
    with c1:
        if st.button("中文", key="zh"):
            st.session_state.language = 'zh'
            st.rerun()
    with c2:
        if st.button("English", key="en"):
            st.session_state.language = 'en'
            st.rerun()

st.markdown("---")

# --- 6. 侧边栏 ---
with st.sidebar:
    st.title(t["sidebar_title"])
    st.markdown(f"### {t['about_header']}")
    st.markdown(t["about_text"])
    st.markdown("---")
    st.markdown(f"### {t['contact_header']}")
    st.markdown(t["email_label"])

# --- 7. 主界面登录框 ---
# 使用列布局居中，左右留白比例为 1:2:1
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    # 标题
    st.markdown(f"### {t['main_title']}")
    st.caption(t["main_subtitle"])
    st.markdown("<br>", unsafe_allow_html=True)

    # 登录表单
    with st.form(key='login_form'):
        email = st.text_input("", placeholder=t["email_placeholder"])
        password = st.text_input("", placeholder=t["password_placeholder"], type="password")
        submit_button = st.form_submit_button(label=t["login_btn"])

        if submit_button:
            st.success("登录功能待实现")

    # 注册按钮 (使用自定义 class 来应用 CSS 样式)
    st.markdown("<br>", unsafe_allow_html=True)
    # 这里用一个容器包裹注册按钮，以便通过 CSS 选中它
    st.markdown('<div class="register-btn">', unsafe_allow_html=True)
    if st.button(t["register_btn"], key="register"):
        st.info("注册功能待实现")
    st.markdown('</div>', unsafe_allow_html=True)
