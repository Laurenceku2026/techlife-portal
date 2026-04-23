import streamlit as st

# --- 1. 页面配置 ---
st.set_page_config(page_title="TechLife Portal", layout="wide")

# --- 2. 初始化 Session State (用于语言切换和登录状态) ---
if 'language' not in st.session_state:
    st.session_state.language = 'zh'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. 侧边栏 (Sidebar) ---
with st.sidebar:
    st.header("🚀 TechLife Suite")

    # 关于系统
    st.subheader("📘 关于系统")
    st.markdown("""
    **TechLife Suite** 是专为研发工程师打造的 **AI 赋能 DFSS（六西格玛设计）** 平台。

    我们致力于通过人工智能技术，简化复杂的工程设计流程，帮助团队实现：

    - **智能需求分析**：快速拆解客户之声 (VOC)。
    - **自动化风险评估**：AI 辅助生成 DFMEA。
    - **参数优化设计**：利用算法寻找最优容差。

    让 AI 成为您的首席质量工程师。
    """)

    st.divider()

    # 联系我们
    st.subheader("📧 联系我们")
    st.markdown("Email: **Techlife2027@gmail.com**")

# --- 4. 右上角布局：语言切换 + 管理员入口 ---
# 使用列布局将元素推到右侧
# col_spacer 用于占据左侧空间，将内容挤到右边
col_spacer, col_cn, col_en, col_admin = st.columns([10, 1, 1, 0.5])

with col_spacer:
    pass  # 空白占位

with col_cn:
    # 中文按钮
    # 使用 use_container_width=True 让按钮填满列宽
    if st.button("中文", use_container_width=True, key="btn_cn", type="primary" if st.session_state.language == 'zh' else "secondary"):
        st.session_state.language = 'zh'
        st.rerun()

with col_en:
    # 英文按钮
    if st.button("English", use_container_width=True, key="btn_en", type="primary" if st.session_state.language == 'en' else "secondary"):
        st.session_state.language = 'en'
        st.rerun()

with col_admin:
    # 管理员入口 (齿轮图标)
    # 使用 help 参数添加鼠标悬停提示
    if st.button("⚙️", help="管理员入口", key="btn_admin"):
        st.toast("跳转到管理员页面...", icon="🔧")
        # 这里可以添加跳转逻辑，例如 st.switch_page("admin.py")

st.markdown("---")  # 分割线

# --- 5. 主界面内容 ---
# 根据语言显示不同内容
if st.session_state.language == 'zh':
    title = "TechLife Suite 门户"
    subtitle = "一站式工程研发 AI 工具集"
    email_label = "邮箱"
    password_label = "密码"
    login_btn = "登录"
    register_btn = "注册"
else:
    title = "TechLife Suite Portal"
    subtitle = "One-stop AI Toolkit for R&D Engineering"
    email_label = "Email"
    password_label = "Password"
    login_btn = "Login"
    register_btn = "Register"

# 居中显示标题
st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: grey;'>{subtitle}</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 登录表单 (居中)
col1, col2, col3 = st.columns([1, 0.5, 1])
with col2:
    with st.form("login_form"):
        email = st.text_input(email_label)
        password = st.text_input(password_label, type="password")

        # 登录按钮
        submitted = st.form_submit_button(login_btn, use_container_width=True)
        if submitted:
            if email and password:
                st.success("登录成功！")
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("请输入邮箱和密码")

    # 注册按钮 (在表单下方，居中)
    st.button(register_btn, use_container_width=True, disabled=st.session_state.logged_in)

# 如果已登录，显示简单的欢迎信息
if st.session_state.logged_in:
    st.balloons()
    st.success(f"**Welcome back, {email}!**")
