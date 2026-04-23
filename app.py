import streamlit as st

# --- 1. 页面配置 ---
st.set_page_config(page_title="TechLife Portal", layout="wide")

# --- 2. 初始化 Session State ---
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# --- 3. 多语言字典 ---
translations = {
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
        "email_label": "邮箱: Techlife2027@gmail.com",

        # 主界面
        "main_title": "TechLife Suite 门户",
        "main_subtitle": "一站式工程研发 AI 工具集",
        "email_placeholder": "请输入邮箱",
        "password_placeholder": "请输入密码",
        "login_btn": "登 录",
        "register_btn": "注 册"
    },
    "en": {
        # 侧边栏
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 About System",
        "about_text": """
        **TechLife Suite** is a platform designed for R&D engineers, featuring **AI-empowered DFSS (Design for Six Sigma)**.

        We are committed to simplifying complex engineering design processes through AI, helping teams achieve:

        - **Intelligent Requirement Analysis**: Rapidly deconstruct Voice of Customer (VOC).
        - **Automated Risk Assessment**: AI-assisted DFMEA generation.
        - **Parameter Optimization**: Find optimal tolerances using algorithms.

        Let AI become your Chief Quality Engineer.
        """,
        "contact_header": "📧 Contact Us",
        "email_label": "Email: Techlife2027@gmail.com",

        # 主界面
        "main_title": "TechLife Suite Portal",
        "main_subtitle": "One-stop AI Toolkit for R&D Engineering",
        "email_placeholder": "Please enter email",
        "password_placeholder": "Please enter password",
        "login_btn": "LOG IN",
        "register_btn": "REGISTER"
    }
}

# 获取当前语言包
t = translations[st.session_state.language]

# --- 4. 自定义 CSS ---
st.markdown("""
    <style>
    /* 全局背景 */
    .stApp {
        background-color: #f5f5f5;
    }

    /* 放大输入框内的文字 */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input {
        font-size: 18px !important;
        height: 50px !important;
    }

    /* 放大输入框的标签 */
    .stTextInput > label,
    .stPasswordInput > label {
        font-size: 18px !important;
        font-weight: 600;
    }

    /* 统一按钮高度和字体 */
    .stButton > button {
        height: 50px !important;
        font-size: 18px !important;
        width: 100%;
        border-radius: 8px;
    }

    /* 右上角语言切换按钮样式 */
    .top-right-container {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. 顶部右上角控制栏 ---
# 使用列布局将内容推到最右边
col_empty, col_controls = st.columns([3, 1])

with col_controls:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("中文", key="btn_zh"):
            st.session_state.language = 'zh'
            st.rerun()
    with c2:
        if st.button("English", key="btn_en"):
            st.session_state.language = 'en'
            st.rerun()

st.markdown("---") # 分隔线

# --- 6. 侧边栏内容 ---
with st.sidebar:
    st.title(t["sidebar_title"])

    st.subheader(t["about_header"])
    st.markdown(t["about_text"])

    st.divider()

    st.subheader(t["contact_header"])
    st.markdown(t["email_label"])

# --- 7. 主界面登录框 ---
# 使用列布局实现居中，比例 1:2:1 表示中间宽，两边窄
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    # 标题区域
    st.markdown(f"<h1 style='text-align: center; font-family: sans-serif;'>{t['main_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: grey; font-size: 16px;'>{t['main_subtitle']}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True) # 增加一点间距

    # 登录表单
    with st.form(key='login_form'):
        email = st.text_input("", placeholder=t["email_placeholder"])
        password = st.text_input("", placeholder=t["password_placeholder"], type="password")

        # 登录按钮
        submit_button = st.form_submit_button(label=t["login_btn"])

        if submit_button:
            if email and password:
                st.success("登录成功！")
            else:
                st.warning("请输入邮箱和密码")

    # 注册按钮（放在表单下方，独立显示）
    # 使用 columns 再次居中这个按钮，使其宽度与上面的输入框对齐
    r_col1, r_col2, r_col3 = st.columns([0.2, 0.6, 0.2])
    with r_col2:
        if st.button(t["register_btn"]):
            st.info("注册功能待实现")
