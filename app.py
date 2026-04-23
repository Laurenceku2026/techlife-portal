import streamlit as st
from supabase import create_client, Client
import os

# --- 1. 初始化配置 (保持不变) ---
st.set_page_config(page_title="TechLife Portal", layout="wide")

# 模拟 Supabase 客户端 (请确保你的 secrets 已配置)
# 在实际运行中，请确保 .streamlit/secrets.toml 中有 SUPABASE_URL 和 SUPABASE_KEY
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. 多语言字典 ---
translations = {
    "zh": {
        "app_title": "TechLife 门户",
        "login": "登录",
        "logout": "退出登录",
        "admin_panel": "管理员入口",
        "language": "English", # 点击切换为英文
        "welcome": "欢迎回来",
        "credits_left": "剩余免费次数",
        "is_premium": "会员状态",
        "upgrade": "升级会员"
    },
    "en": {
        "app_title": "TechLife Portal",
        "login": "Login",
        "logout": "Logout",
        "admin_panel": "Admin Panel",
        "language": "中文", # 点击切换为中文
        "welcome": "Welcome back",
        "credits_left": "Credits Left",
        "is_premium": "Premium Status",
        "upgrade": "Upgrade"
    }
}

# --- 3. 辅助函数 ---
def get_text(key):
    lang = st.session_state.get("language", "zh")
    return translations[lang].get(key, key)

def switch_language():
    current_lang = st.session_state.get("language", "zh")
    st.session_state.language = "en" if current_lang == "zh" else "zh"
    st.rerun()

# --- 4. 页面主逻辑 ---
def main():
    # 初始化 Session State
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "language" not in st.session_state:
        st.session_state.language = "zh"
    if "user_data" not in st.session_state:
        st.session_state.user_data = None

    # --- 顶部导航栏布局 ---
    # 使用列布局将内容推到右侧
    header_cols = st.columns() # 左、中、右 比例
    
    with header_cols:
        st.title(get_text("app_title"))
    
    # 只有登录状态下才显示右上角的工具栏
    if st.session_state.logged_in:
        with header_cols:
            # 使用 container 让内容右对齐
            with st.container():
                # 内部再分两列，放置 语言按钮 和 管理员齿轮
                tool_cols = st.columns(2)
                
                # 1. 语言切换按钮 (左侧)
                with tool_cols:
                    if st.button(get_text("language"), use_container_width=True):
                        switch_language()
                
                # 2. 管理员入口 (右侧 - 齿轮图标)
                with tool_cols:
                    # 使用图标作为按钮
                    if st.button("⚙️", help=get_text("admin_panel"), use_container_width=True):
                        # 跳转到管理员页面
                        st.switch_page("pages/1_🛠️_Admin_Panel.py") 
                        # 注意：确保你的 admin 页面文件名匹配，或者使用 st.navigate
    else:
        # 未登录时的占位，保持布局平衡
        with header_cols:
            st.write("")<websource>source_group_web_1</websource>

    st.divider() # 分割线

    # --- 登录逻辑 ---
    if not st.session_state.logged_in:
        st.header(get_text("login"))
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button(get_text("login")):
            # 这里替换为你实际的 Supabase 登录逻辑
            # try:
            #     response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            #     if response.user:
            #         st.session_state.logged_in = True
            #         st.session_state.user_data = response.user
            #         st.rerun()
            # except Exception as e:
            #     st.error(e)
            
            # 模拟登录成功 (仅用于演示布局)
            if email and password: 
                st.session_state.logged_in = True
                st.session_state.user_data = {"email": email}
                st.rerun()

    # --- 主界面逻辑 (登录后显示) ---
    else:
        st.subheader(f"{get_text("welcome")}, {st.session_state.user_data['email']}")
        
        # 这里显示你的主要功能
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"💳 {get_text("is_premium")}: Free")
        with col2:
            st.info(f"⚡ {get_text("credits_left")}: 10")
            
        st.button(get_text("logout"), on_click=lambda: setattr(st.session_state, 'logged_in', False))

if __name__ == "__main__":
    main()
