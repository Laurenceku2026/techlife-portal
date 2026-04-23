import streamlit as st

# --- 页面配置 ---
st.set_page_config(page_title="TechLife Suite 门户", layout="wide")

# --- 自定义 CSS 样式 ---
st.markdown("""
<style>
    /* 全局设置 */
    .stApp {
        background-color: #f5f5f5;
        overflow-x: hidden;
    }

    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* --- 左侧侧边栏样式 --- */
    .sidebar-content {
        padding: 40px 20px;
        color: #333;
    }
    .sidebar-content h1 {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        color: #111;
    }
    .sidebar-content p {
        font-size: 14px;
        line-height: 1.6;
        color: #555;
    }
    .contact-info {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #eee;
        font-size: 13px;
        color: #777;
    }

    /* --- 右侧登录框悬浮层 --- */
    .login-card {
        position: absolute; /* 绝对定位，脱离文档流 */
        top: 50%;            /* 垂直居中 */
        right: 10%;          /* 距离右侧 10% */
        transform: translateY(-50%); /* 精确垂直居中修正 */
        width: 380px;
        background-color: white;
        padding: 35px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); /* 柔和阴影 */
        z-index: 100;        /* 确保在最上层 */
        border: 1px solid #e0e0e0;
    }

    /* 登录框内的标题 */
    .login-title {
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #111;
    }
    .login-subtitle {
        text-align: center;
        font-size: 13px;
        color: #888;
        margin-bottom: 30px;
    }

    /* 输入框样式 - 纯黑色线条和文字 */
    .stTextInput > div > div > input {
        color: #000 !important; /* 输入文字黑色 */
        border-color: #000 !important; /* 边框黑色 */
    }
    /* 解决 Streamlit 输入框聚焦时的蓝色边框，改为黑色 */
    .stTextInput input:focus {
        border-color: #000 !important;
        box-shadow: 0 0 0 1px #000 !important;
    }

    /* 按钮区域布局 */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 10px;
    }

    /* 注册按钮样式 (黑色) */
    .register-btn button {
        background-color: #000;
        color: white;
        border: 1px solid #000;
    }
    .register-btn button:hover {
        background-color: #333;
        border-color: #333;
    }

    /* 登录按钮样式 (白色底，黑色边框) */
    .login-btn button {
        background-color: white;
        color: black;
        border: 1px solid #000;
    }
    .login-btn button:hover {
        background-color: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# --- 页面布局 ---

# 创建两列：左侧 30%，右侧 70%
col_left, col_right = st.columns([3, 7])

# --- 左侧内容 ---
with col_left:
    st.markdown("""
    <div class="sidebar-content">
        <h1>TechLife Suite</h1>
        <h3>关于系统</h3>
        <p>TechLife Suite 是专为开发工程师打造的 AI 辅助开发平台。我们致力于通过人工智能技术，简化复杂的工程设计流程。</p>
        <ul>
            <li><strong>智能需求分析：</strong>快速拆解用户需求。</li>
            <li><strong>自动代码生成：</strong>AI 辅助生成高质量代码。</li>
            <li><strong>系统自动优化：</strong>持续监控系统性能。</li>
        </ul>

        <div class="contact-info">
            <p><strong>联系我们</strong></p>
            <p>邮箱: techlife@example.com</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 右侧内容 (背景区域) ---
with col_right:
    # 这里主要作为背景，登录框会通过 CSS 悬浮在上面

    # 1. 右上角的语言切换 (使用列布局模拟)
    c1, c2 = st.columns([6, 1])
    with c2:
        # 简单的语言切换按钮
        st.button("中文", use_container_width=True)
        st.button("English", use_container_width=True)

    # 2. 使用 HTML 注入悬浮的登录框
    st.markdown("""
    <div class="login-card">
        <div class="login-title">TechLife Suite 门户</div>
        <div class="login-subtitle">一站式工程设计 AI 工具箱</div>

        <!-- 这里使用 Streamlit 的组件占位，通过 JS 或 CSS 很难直接控制 Streamlit 原生组件进入 HTML 字符串，
             所以我们在 HTML 下方放置真正的 Streamlit 组件，并用 CSS 隐藏原生位置，或者直接用 HTML 表单 -->

        <!-- 方案：使用纯 HTML 表单模拟界面，或者使用 Streamlit 组件覆盖。
             为了保证功能可用，我们在下面放置真实的组件，并用 CSS 绝对定位到这里 -->
    </div>
    """, unsafe_allow_html=True)

    # --- 真正的交互组件 (通过 CSS 定位到右侧中间) ---
    # 我们创建一个空的容器，然后用 CSS 把它移动到登录框的位置

    # 输入框
    username = st.text_input("请输入邮箱", key="user_input", label_visibility="collapsed")
    password = st.text_input("请输入密码", key="pass_input", label_visibility="collapsed")

    # 按钮列
    # 注意：我们需要给这些按钮加上自定义 class 才能应用上面的 CSS
    # 这里使用 columns 来并排或堆叠按钮
    col_btn1, col_btn2 = st.columns(2, gap="small")

    with col_btn1:
        # 登录按钮
        login_clicked = st.button("登录", key="login_btn")

    with col_btn2:
        # 注册按钮
        register_clicked = st.button("注册", key="register_btn")

    # --- 强制将上面的组件移动到右侧悬浮位置 ---
    # 这是一个稍微高级的技巧，利用 CSS 将刚才生成的 input 和 button 移动
    st.markdown("""
    <style>
        /* 找到刚才生成的输入框和按钮的父容器，强制移动位置 */
        /* 注意：Streamlit 的组件层级很深，我们需要精准定位 */

        /* 隐藏默认的顶部间距 */
        .element-container {
            margin-bottom: 0 !important;
        }

        /* 定位输入框 1 (用户名) */
        div[data-baseweb="input"] {
            position: absolute;
            top: 50%;
            right: 10%;
            transform: translateY(-20px);
            width: 380px;
            z-index: 101;
            background: transparent;
        }
        /* 定位输入框 2 (密码) */
        div[data-baseweb="input"]:nth-of-type(2) {
            top: 50%;
            transform: translateY(40px);
        }

        /* 定位按钮容器 */
        div[data-testid="stHorizontalBlock"] {
            position: absolute;
            top: 50%;
            right: 10%;
            transform: translateY(110px);
            width: 380px;
            z-index: 102;
            gap: 10px !important;
        }

        /* 修正按钮样式以匹配设计 */
        button[kind="secondary"] {
            background-color: white;
            color: black;
            border: 1px solid black;
            width: 100%;
        }
         button[kind="secondary"]:hover {
            background-color: #f0f0f0;
            border-color: black;
        }
    </style>
    """, unsafe_allow_html=True)
