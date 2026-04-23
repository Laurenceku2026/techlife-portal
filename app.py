import streamlit as st

# --- 1. 初始化配置 ---
st.set_page_config(page_title="TechLife Portal", layout="wide")

# --- 2. 初始化 Session State (用于语言切换) ---
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# --- 3. 多语言字典 (包含侧边栏和主界面的所有文字) ---
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
        "register_btn": "注 册",
        "admin_tooltip": "管理员入口"
    },
    "en": {
        # Sidebar
        "sidebar_title": "TechLife Suite",
        "about_header": "📘 About System",
        "about_text": """
        **TechLife Suite** is an **AI-empowered DFSS (Design for Six Sigma)** platform designed specifically for R&D engineers.

        We are committed to simplifying complex engineering design processes through AI technology, helping teams achieve:

        - **Intelligent Requirement Analysis**: Rapidly decompose Voice of Customer (VOC).
        - **Automated Risk Assessment**: AI-assisted generation of DFMEA.
        - **Parameter Optimization**: Algorithm-driven search for optimal tolerances.

        Let AI become your Chief Quality Engineer.
        """,
        "contact_header": "📧 Contact Us",
        "email_label": "Email: Techlife2027@gmail.com",

        # Main
        "main_title": "TechLife Suite Portal",
        "main_subtitle": "One-stop AI Toolkit for R&D Engineering",
        "email_placeholder": "Enter your email",
        "password_placeholder": "Enter your password",
        "login_btn": "LOG IN",
        "register_btn": "REGISTER",
        "admin_tooltip": "Admin Panel"
    }
}

# 获取当前语言的翻译包
t = translations[st.session_state.language]

# --- 4. 页面布局 ---

# 右上角控制区 (语言切换 + 管理员)
# 使用 columns 来并排布局
col_lang_zh, col_lang_en, col_spacer, col_admin = st.columns([1, 1, 8, 1])

with col_lang_zh:
    # 中文按钮
    if st.button("中文", use_container_width=True, key="btn_zh", disabled=st.session_state.language=='zh'):
        st.session_state.language = 'zh'
        st.rerun()

with col_lang_en:
    # 英文按钮
    if st.button("English", use_container_width=True, key="btn_en", disabled=st.session_state.language=='en'):
        st.session_state.language = 'en'
        st.rerun()

with col_admin:
    # 管理员齿轮
    st.markdown(f"<div style='padding-top: 8px; text-align: center;'>⚙️</div>", unsafe_allow_html=True)
    # 注意：Streamlit 的 st.button 在 columns 中更稳定，这里为了演示用了 markdown 图标，实际功能可加按钮

# --- 5. 侧边栏内容 (根据语言动态变化) ---
with st.sidebar:
    st.title(t["sidebar_title"])

    st.subheader(t["about_header"])
    st.markdown(t["about_text"])

    st.divider()

    st.subheader(t["contact_header"])
    st.markdown(t["email_label"])

# --- 6. 主界面内容 ---

# 居中显示登录框
st.markdown("<br>", unsafe_allow_html=True) # 增加一点顶部间距

# 使用 columns 将登录框居中，并设置宽度
# 这里的 [2, 5, 2] 比例意味着中间的内容区域占屏幕的 5/9，比较宽敞
col1, col2, col3 = st.columns([2, 5, 2])

with col2:
    # 标题
    st.markdown(f"<h1 style='text-align: center;'>{t['main_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray;'>{t['main_subtitle']}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 登录表单容器
    with st.container(border=True):
        email = st.text_input(t["email_placeholder"], key="email_input")
        password = st.text_input(t["password_placeholder"], type="password", key="pass_input")

        # 登录按钮 (全宽)
        login_clicked = st.button(t["login_btn"], use_container_width=True, type="primary")

    # 注册按钮 (全宽，在表单下方)
    st.button(t["register_btn"], use_container_width=True)

# 模拟登录逻辑
if login_clicked:
    if email and password:
        st.success("登录成功！(演示)")
    else:
        st.warning("请输入邮箱和密码")
