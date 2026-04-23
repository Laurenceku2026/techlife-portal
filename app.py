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

# --- 4. 自定义 CSS (大字体 + 右上角布局修复) ---
st.markdown("""
    <style>
    /* 放大输入框内的文字和占位符 */
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

    /* 按钮样式 */
    .stButton > button {
        height: 50px !important;
        font-size: 18px !important;
        width: 100%;
    }

    /* 修复右上角布局：确保内容右对齐 */
    .top-right-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }

    /* 语言按钮样式 */
    .lang-btn {
        border: 1px solid #ccc;
        background-color: white;
        color: black;
        padding: 5px 15px;
        border-radius: 5px;
        font-size: 14px;
    }

    .lang-btn.active {
        background-color: #FF4B4B;
        color: white;
        border-color: #FF4B4B;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. 顶部右上角控制栏 (语言 + 齿轮) ---
# 使用列布局将内容推到最右边
col_empty, col_controls = st.columns([3, 1]) # 3:1 的比例，把控件挤到右边

with col_controls:
    # 使用容器确保内部元素右对齐
    top_container = st.container()
    with top_container:
        # 这里使用 HTML/CSS 来精确控制按钮样式和排列
        btn_zh_class = "lang-btn active" if st.session_state.language == 'zh' else "lang-btn"
        btn_en_class = "lang-btn active" if st.session_state.language == 'en' else "lang-btn"

        # 创建两列来放按钮，避免 Streamlit 按钮默认的垂直堆叠问题
        c1, c2, c3 = st.columns([1, 1, 0.5])
        with c1:
            if st.button("中文", key="btn_zh"):
                st.session_state.language = 'zh'
                st.rerun()
        with c2:
            if st.button("English", key="btn_en"):
                st.session_state.language = 'en'
                st.rerun()
        with c3:
            # 齿轮图标作为管理员入口
            st.markdown("<div style='padding-top:10px'>⚙️</div>", unsafe_allow_html=True)
            # 如果需要齿轮可点击，可以使用下面这行代替上面那行：
            # if st.button("⚙️", key="btn_admin"): pass

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
# 居中显示
c1, c2, c3 = st.columns([1, 2, 1]) # 中间列宽为2，两边为1，实现居中

with c2:
    st.markdown(f"<h1 style='text-align: center;'>{t['main_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: grey;'>{t['main_subtitle']}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True) # 间距

    with st.form(key='login_form'):
        email = st.text_input(t["email_placeholder"], placeholder="")
        password = st.text_input(t["password_placeholder"], type="password", placeholder="")
        submit_button = st.form_submit_button(label=t["login_btn"])

        if submit_button:
            # 这里添加登录逻辑
            st.success("登录功能待实现")

    # 注册按钮单独放在下面，或者也可以用 form 里的，看设计需求
    # 这里为了美观，放在 form 外面居中
    c_reg_1, c_reg_2, c_reg_3 = st.columns([1, 2, 1])
    with c_reg_2:
        if st.button(t["register_btn"]):
            st.info("注册功能待实现")
