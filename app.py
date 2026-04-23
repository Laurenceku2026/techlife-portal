import streamlit as st

# --- 页面配置 ---
st.set_page_config(
    page_title="TechLife Suite 门户",
    layout="centered"
)

# --- 自定义 CSS 样式 ---
# 注意：为了防止 Python 解析错误，CSS 单位（如 100vh）已做处理或确保在字符串内
st.markdown("""
<style>
    /* 全局背景与字体 */
    .stApp {
        background-color: #f0f2f6;
        font-family: "Microsoft YaHei", sans-serif;
    }

    /* 隐藏默认的 Streamlit 菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- 登录框容器样式 --- */
    .login-container {
        background-color: white;
        padding: 40px 50px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: 400px;
        margin-top: 50px;
        /* 修复点：确保 vh 单位被正确识别为字符串 */
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* 标题样式 */
    .main-title {
        color: #000000;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
    }

    .sub-title {
        color: #666666;
        font-size: 14px;
        margin-bottom: 30px;
        text-align: center;
    }

    /* --- 输入框样式（黑色线条和文字）--- */
    /* Streamlit 的输入框结构比较深，需要针对性覆盖 */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input {
        color: #000000 !important; /* 输入文字黑色 */
        border: 1px solid #000000 !important; /* 边框黑色 */
        border-radius: 4px;
        height: 45px;
    }

    /* 标签文字颜色 */
    .stTextInput > label,
    .stPasswordInput > label {
        color: #000000 !important;
        font-weight: bold;
        font-size: 14px;
    }

    /* 去掉输入框聚焦时的蓝色/红色高亮，保持黑色 */
    .stTextInput > div > div > input:focus,
    .stPasswordInput > div > div > input:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }

    /* --- 按钮区域布局 --- */
    .button-row {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin-top: 20px;
        width: 100%;
    }

    /* 按钮通用样式 */
    .custom-button {
        width: 100%;
        height: 45px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    
    .custom-button:hover {
        opacity: 0.9;
    }

    /* 登录按钮 - 黑色 */
    .login-btn {
        background-color: #000000;
        color: white;
    }

    /* 注册按钮 - 白色背景黑色边框 */
    .register-btn {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 页面布局 ---
# 使用列布局来模拟左右结构（左侧图/文字，右侧登录）
col1, col2 = st.columns([1, 1])

with col1:
    # 这里可以放左侧的图片或介绍文字
    st.markdown("<br>", unsafe_allow_html=True) # 顶部留白
    st.image("https://via.placeholder.com/500x300?text=TechLife+Image", use_column_width=True)
    st.markdown("""
    ### 关于系统
    - **智能需求分析**：快速拆解用户需求
    - **自动代码生成**：AI 辅助生成代码
    - **系统自动优化**：持续监控系统性能
    """)

with col2:
    # 登录框主体
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    st.markdown('<div class="main-title">TechLife Suite 门户</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">一站式工作协同 AI 工具集</div>', unsafe_allow_html=True)

    # 输入框
    username = st.text_input("请输入邮箱")
    password = st.text_input("请输入密码", type="password")

    # 按钮布局
    # 注意：Streamlit 原生按钮无法直接应用自定义 CSS 类名，
    # 这里使用 HTML 按钮配合 JS 或 Form 提交来模拟，或者使用 st.columns 放置原生按钮
    
    # 方案：使用 st.columns 放置两个原生按钮，并尝试通过 CSS 类名 hack (Streamlit 1.20+)
    # 如果原生按钮难以完全自定义，可以使用 HTML form
    
    # 这里使用最简单的 HTML 按钮模拟（仅作展示效果，实际需配合 JS 或 Form）
    col_btn_1, col_btn_2 = st.columns(2)
    
    with col_btn_1:
        # 注册按钮
        if st.button("注册", key="register_btn"):
            st.info("点击了注册")
            
    with col_btn_2:
        # 登录按钮
        if st.button("登录", key="login_btn"):
            st.success("点击了登录")

    st.markdown('</div>', unsafe_allow_html=True) # 结束 login-container
