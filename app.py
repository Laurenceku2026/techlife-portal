import streamlit as st

# --- 1. 页面配置 (已修复重复参数错误) ---
st.set_page_config(page_title="TechLife Suite 门户", layout="wide")

# --- 2. 深度定制 CSS (还原黑白硬线条风格) ---
st.markdown("""
    <style>
    /* --- 全局背景 --- */
    .stApp {
        background-color: #FFFFFF; /* 强制纯白背景 */
    }

    /* --- 输入框样式：白底、黑框、直角 --- */
    /* 修复了之前的 100vh 报错，并强制样式 */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important; /* 黑色实线边框 */
        border-radius: 0px !important; /* 去除圆角 */
        height: 50px !important;
        box-shadow: none !important;
    }

    /* 输入框获得焦点时的样式 */
    .stTextInput > div > div > input:focus,
    .stPasswordInput > div > div > input:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }

    /* --- 按钮样式：黑底白字、直角 --- */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #000000 !important;
        border-radius: 0px !important; /* 去除圆角 */
        height: 50px !important;
        font-weight: bold;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #333333 !important;
        border-color: #333333 !important;
    }

    /* --- 隐藏默认元素 --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 页面布局 ---
# 使用列布局实现左侧文字、右侧登录框
col_left, col_right = st.columns([1, 1]) # 1:1 比例

# --- 左侧内容 ---
with col_left:
    st.markdown("<br><br>", unsafe_allow_html=True) # 顶部留白
    st.title("TechLife Suite")
    st.subheader("关于系统")
    st.markdown("""
    **TechLife Suite** 是专为研发工程师打造的 **AI 赋能 DFSS** 平台。

    我们致力于通过人工智能技术，简化复杂的工程设计流程：

    - **智能需求分析**：快速拆解客户之声。
    - **自动化风险评估**：AI 辅助生成 DFMEA。
    - **参数优化设计**：利用算法寻找最优容差。

    让 AI 成为您的首席质量工程师。
    """)
    st.info("邮箱: Techlife2027@gmail.com")

# --- 右侧登录框 ---
with col_right:
    # 使用容器居中内容
    with st.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: left; color: black; border-bottom: 2px solid black; padding-bottom: 10px;'>门户登录</h2>", unsafe_allow_html=True)

        with st.form(key='login_form'):
            email = st.text_input("邮箱", placeholder="请输入邮箱地址")
            password = st.text_input("密码", type="password", placeholder="请输入密码")

            # 两个按钮并排显示
            col_btn_1, col_btn_2 = st.columns(2)
            with col_btn_1:
                submit = st.form_submit_button("登 录")
            with col_btn_2:
                register = st.form_submit_button("注 册")

            if submit:
                st.success("登录成功（演示）")
            if register:
                st.info("注册功能（演示）")
