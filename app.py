import streamlit as st

# --- 1. 页面配置 ---
st.set_page_config(page_title="TechLife Portal", layout="wide")

# --- 2. 初始化 Session State ---
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# --- 3. 自定义 CSS (重点：放大输入框字体) ---
st.markdown("""
    <style>
    /* 放大输入框内的文字和占位符 */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input {
        font-size: 18px !important;
        height: 50px !important; /* 增加高度以匹配大字体 */
    }
    
    /* 放大输入框的标签（如 "邮箱"） */
    .stTextInput > label,
    .stPasswordInput > label {
        font-size: 18px !important;
        font-weight: 600;
    }

    /* 调整按钮高度以匹配 */
    .stButton > button {
        height: 50px !important;
        font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. 多语言字典 ---
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
        "email_link": "Techlife2027@gmail.com",

        "main_title": "TechLife Suite 门户",
        "main_subtitle": "一站式工程研发 AI 工具集",
        "email_label": "请输入邮箱",
        "password_label": "请输入密码",
        "login_btn": "登录",
        "register_btn": "注册",
        "admin_tooltip": "管理员入口"
    },
    "en": {
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 About System",
        "about_text": """
        **TechLife Suite** is an **AI-empowered DFSS (Design for Six Sigma)** platform designed specifically for R&D engineers.

        We are committed to simplifying complex engineering design processes through AI, helping teams achieve:

        - **Intelligent Requirement Analysis**: Rapidly decompose Voice of Customer (VOC).
        - **Automated Risk Assessment**: AI-assisted generation of DFMEA.
        - **Parameter Optimization**: Algorithms to find optimal tolerances.

        Let AI be your Chief Quality Engineer.
        """,
        "contact_header": "📧 Contact Us",
        "email_link": "Techlife2027@gmail.com",

        "main_title": "TechLife Suite Portal",
        "main_subtitle": "One-stop AI Toolkit for R&D Engineering",
        "email_label": "Please enter email",
        "password_label": "Please enter password",
        "login_btn": "Log In",
        "register_btn": "Sign Up",
        "admin_tooltip": "Admin Panel"
    }
}

# 获取当前语言的翻译文本
t = translations[st.session_state.language]

# --- 5. 侧边栏 ---
with st.sidebar:
    st.title(t["sidebar_title"])

    st.subheader(t["about_header"])
    st.markdown(t["about_text"])

    st.divider()

    st.subheader(t["contact_header"])
    st.markdown(f"📧 Email: {t['email_link']}")

# --- 6. 主界面布局 ---

# 顶部右上角控制区 (语言切换 + 管理员)
# 使用列布局将内容推到最右边
col_lang_1, col_lang_2, col_admin, col_space = st.columns([1, 1, 1, 10])

with col_lang_1:
    # 中文按钮
    if st.button("中文", key="btn_zh", use_container_width=True):
        st.session_state.language = 'zh'
        st.rerun()

with col_lang_2:
    # 英文按钮
    if st.button("English", key="btn_en", use_container_width=True):
        st.session_state.language = 'en'
        st.rerun()

with col_admin:
    # 管理员齿轮图标
    st.markdown(f"<div style='padding-top: 8px; text-align: center;'>⚙️</div>", unsafe_allow_html=True)
    # 注意：Streamlit原生图标按钮较难直接放在列中且不带边框，这里用Markdown模拟或可以用 st.button("⚙️")
    if st.button("⚙️", key="btn_admin", help=t["admin_tooltip"], use_container_width=True):
        st.toast("管理员入口 (功能开发中)")

# 页面主体内容 (居中)
st.markdown("<br><br>", unsafe_allow_html=True) # 增加一点顶部间距

# 标题部分
st.markdown(f"<h1 style='text-align: center; font-weight: 800;'>{t['main_title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666; font-size: 18px;'>{t['main_subtitle']}</p>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# 登录表单区域
# 使用列布局来限制表单的最大宽度，避免在大屏幕上拉得太长
c1, c2, c3 = st.columns([2, 3, 2]) # 左右留白，中间放表单

with c2:
    with st.form("login_form"):
        email = st.text_input("", placeholder=t["email_label"])
        password = st.text_input("", placeholder=t["password_label"], type="password")

        # 登录按钮样式
        submit = st.form_submit_button(t["login_btn"])
        if submit:
            if email and password:
                st.success("登录成功！")
            else:
                st.error("请输入邮箱和密码")

    # 注册按钮 (在表单外，居中)
    st.markdown(
        """
        <style>
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 50px;
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    if st.button(t["register_btn"]):
        st.info("注册功能开发中")
