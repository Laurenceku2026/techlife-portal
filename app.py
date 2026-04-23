import streamlit as st
from supabase import create_client, Client

# --- 1. 页面配置 ---
st.set_page_config(page_title="TechLife Portal", layout="centered")

# --- 2. 侧边栏 (Sidebar) ---
with st.sidebar:
    # 标题
    st.header("🚀 TechLife Suite")

    # 关于系统介绍
    st.subheader("📘 关于系统")
    st.markdown("""
    **TechLife Suite** 是专为研发工程师打造的 **AI 赋能 DFSS（六西格玛设计）** 平台。
    
    我们致力于通过人工智能技术，简化复杂的工程设计流程，帮助团队实现：
    
    - **智能需求分析**：快速拆解客户之声 (VOC)。
    - **自动化风险评估**：AI 辅助生成 DFMEA。
    - **参数优化设计**：利用算法寻找最优容差。
    
    让 AI 成为您的首席质量工程师。
    """)

    st.divider() # 分割线

    # 工具列表（占位）
    st.caption("可用工具:")
    st.markdown("- 🛠️ VOC 分析助手")
    st.markdown("- 🛠️ 智能 FMEA 生成器")
    st.markdown("- 🛠️ 容差设计计算器")

    st.divider()

    # 联系方式
    st.markdown("#### 📧 联系我们")
    st.markdown("Techlife2027@gmail.com")

# --- 3. 多语言字典 ---
translations = {
    "zh": {
        "welcome_title": "欢迎使用 TechLife 门户",
        "welcome_text": "请登录以访问您的 AI 工程工具。",
        "login_btn": "登录",
        "register_btn": "注册",
        "email_label": "邮箱",
        "password_label": "密码",
    },
    "en": {
        "welcome_title": "Welcome to TechLife Portal",
        "welcome_text": "Please login to access your AI engineering tools.",
        "login_btn": "Login",
        "register_btn": "Register",
        "email_label": "Email",
        "password_label": "Password",
    }
}

# --- 4. 语言切换逻辑 ---
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

def toggle_language():
    st.session_state.language = 'en' if st.session_state.language == 'zh' else 'zh'

# 在侧边栏或顶部添加语言切换（这里放在侧边栏底部比较整洁）
with st.sidebar:
    st.divider()
    if st.session_state.language == 'zh':
        st.button("🇺🇸 English", on_click=toggle_language, use_container_width=True)
    else:
        st.button("🇨🇳 中文", on_click=toggle_language, use_container_width=True)

# 获取当前语言文本
t = translations[st.session_state.language]

# --- 5. 主界面布局 (Main) ---
# 使用列来居中内容，但不分两列显示业务逻辑
col1, col2, col3 = st.columns([1, 2, 1]) # 中间列宽，两边窄，实现居中效果

with col2:
    st.title(t["welcome_title"])
    st.write(t["welcome_text"])
    
    st.markdown("---")

    # 登录表单
    with st.form("login_form"):
        email = st.text_input(t["email_label"])
        password = st.text_input(t["password_label"], type="password")
        
        # 两个大按钮并排
        c1, c2 = st.columns(2)
        with c1:
            submit_login = st.form_submit_button(t["login_btn"], type="primary", use_container_width=True)
        with c2:
            submit_register = st.form_submit_button(t["register_btn"], use_container_width=True)

    # --- 6. 简单的逻辑模拟 ---
    if submit_login:
        if email and password:
            st.success(f"模拟登录成功: {email}")
            # 这里后续接入 Supabase 登录逻辑
        else:
            st.warning("请输入邮箱和密码")

    if submit_register:
        if email and password:
            st.info(f"模拟注册请求: {email}")
            # 这里后续接入 Supabase 注册逻辑
        else:
            st.warning("请输入邮箱和密码")
