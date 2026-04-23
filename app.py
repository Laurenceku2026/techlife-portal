import streamlit as st

# --- 1. 页面配置 ---
st.set_page_config(page_title="TechLife Suite 门户", layout="wide", page_title="TechLife Suite")

# --- 2. 核心 CSS 样式 (深度定制) ---
# 这里修复了之前的 SyntaxError，并强制修正了颜色和边框
st.markdown("""
    <style>
    /* --- 全局背景重置 --- */
    /* 强制主背景为白色，去除 Streamlit 默认灰边 */
    .stApp {
        background-color: #FFFFFF;
        padding-top: 50px;
    }
    /* 隐藏默认的 Header 和 Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- 登录框容器定制 --- */
    .login-box {
        background-color: #FFFFFF;
        padding: 40px;
        border: 1px solid #000000; /* 黑色实线边框 */
        border-radius: 0px; /* 去除圆角，硬朗风格 */
        box-shadow: 5px 5px 0px #000000; /* 硬朗的投影 */
        max-width: 450px;
        margin-left: auto; /* 靠右对齐 */
    }

    /* --- 输入框深度定制 --- */
    /* 修复 Python 解析错误的写法，强制单位在字符串内 */
    div[data-baseweb="input"] > input {
        height: 45px !important;
        border-radius: 0px !important;
        border: 1px solid #CCCCCC !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-size: 16px;
        margin-bottom: 15px;
    }

    /* 输入框获得焦点时的样式 */
    div[data-baseweb="input"] > input:focus {
        border: 2px solid #000000 !important;
        box-shadow: none !important;
    }

    /* --- 按钮样式 --- */
    /* 登录按钮 */
    .stButton > button {
        width: 100%;
        height: 45px;
        background-color: #000000;
        color: #FFFFFF;
        font-size: 18px;
        font-weight: bold;
        border-radius: 0px;
        border: 1px solid #000000;
        margin-bottom: 10px;
    }
    .stButton > button:hover {
        background-color: #333333;
        border-color: #333333;
        color: #FFFFFF;
    }

    /* --- 侧边栏样式 --- */
    section[data-testid="stSidebar"] {
        background-color: #F0F2F6;
        border-right: 1px solid #DDDDDD;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 页面布局 (左右分栏) ---

# 使用列布局：左侧 1 份，右侧 1 份
col_left, col_right = st.columns([1, 1], gap="large")

# --- 左侧内容 ---
with col_left:
    st.markdown("### 关于系统")
    st.markdown("""
    **TechLife Suite** 是专为研发工程师打造的 **AI 赋能 DFSS（六西格玛设计）** 平台。

    我们致力于通过人工智能技术，简化复杂的工程设计流程，帮助团队实现：

    - **智能需求分析**：快速拆解客户之声 (VOC)。
    - **自动化风险评估**：AI 辅助生成 DFMEA。
    - **参数优化设计**：利用算法寻找最优容差。

    *让 AI 成为您的首席质量工程师。*
    """)

    st.markdown("---")
    st.markdown("**📧 联系我们**")
    st.markdown("邮箱: `Techlife2027@gmail.com`")

# --- 右侧内容 (登录框) ---
with col_right:
    # 标题
    st.markdown("<h2 style='text-align: center; font-family: sans-serif;'>TechLife Suite 门户</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>— 一站式工程研发 AI 工具集 —</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # 使用容器包裹，应用自定义 CSS 类
    with st.container():
        # 这里使用一个 dummy container 来承载 CSS 类（Streamlit 原生不支持直接给容器加 class，所以用 HTML 模拟或强制样式）
        # 为了稳定性，我们直接在代码块中写表单

        with st.form("login_form"):
            # 邮箱输入
            email = st.text_input("请输入邮箱", placeholder="example@techlife.com")

            # 密码输入
            password = st.text_input("请输入密码", type="password", placeholder="••••••••")

            # 登录按钮 (在 form 内部)
            submit = st.form_submit_button("登 录")

            if submit:
                if email and password:
                    st.success("登录成功！")
                else:
                    st.error("请输入邮箱和密码")

    # 注册按钮 (在 form 外部，居中)
    st.markdown("""
        <div style="text-align: center; margin-top: 10px;">
            还没有账号？ <a href="#" style="color: #000; font-weight: bold; text-decoration: underline;">立即注册</a>
        </div>
        """, unsafe_allow_html=True)
