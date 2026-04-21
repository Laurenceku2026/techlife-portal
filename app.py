import streamlit as st
from supabase import create_client, Client
from st_login_form import login_form
import time

# ================== 配置区域 ==================
st.set_page_config(page_title="TechLife Suite", layout="wide")

# 你的三个工具的子域名地址（请替换为你实际配置的子域名）
TOOL_LINKS = {
    "product-feasibility": "https://product.techlife-suite.com",   # 产品可行性分析
    "dfmea": "https://para-vary.techlife-suite.com",              # DFMEA 分析（你用的是 para-vary）
    "tolerance": "https://stack-tolerance.techlife-suite.com"     # 公差分析
}

# ================== 初始化 Supabase 客户端 ==================
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# ================== 核心认证逻辑 ==================
# 使用第三方组件 st_login_form 构建登录/注册窗口
# 该组件会自动处理与 Supabase 的交互，并将登录状态存入 st.session_state
try:
    supabase_conn = login_form(
        supabase_connection=supabase,
        user_tablename="user_authentication"
    )
except Exception as e:
    st.error(f"登录组件初始化失败: {e}")
    st.stop()

# 检查登录状态
if st.session_state.get("authenticated", False):
    # 成功登录后，显示欢迎信息和工具入口
    user_name = st.session_state.get("username", "User")
    st.sidebar.success(f"👋 欢迎回来, {user_name}!")
    if st.sidebar.button("🚪 登出"):
        # 登出逻辑：清空 session_state 中的关键状态并刷新页面
        for key in ["authenticated", "username"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    # 主界面展示三个工具的入口
    st.title("🚀 TechLife Suite")
    st.markdown("请选择您要使用的AI分析工具：")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📊 产品可行性分析")
        st.link_button("立即使用", TOOL_LINKS["product-feasibility"])
    with col2:
        st.markdown("### ⚙️ DFMEA 分析")
        st.link_button("立即使用", TOOL_LINKS["dfmea"])
    with col3:
        st.markdown("### 📏 公差分析")
        st.link_button("立即使用", TOOL_LINKS["tolerance"])
else:
    # 未登录状态，页面提示
    st.title("🔐 欢迎来到 TechLife Suite")
    st.markdown("请使用右侧表单登录或注册，开始您的AI分析之旅。")
