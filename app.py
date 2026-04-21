import streamlit as st
from st_supabase_connection import SupabaseConnection

# 页面配置
st.set_page_config(page_title="TechLife Suite", layout="wide")

# 1. 建立 Supabase 连接（从 secrets 读取）
conn = st.connection("supabase", type=SupabaseConnection)
supabase = conn.client  # 原生 supabase-py 客户端

# 2. 初始化 session_state 中的登录状态
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None

# 3. 登出函数
def logout():
    supabase.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.rerun()

# 4. 登录/注册表单（纯手动实现，无第三方组件）
def auth_form():
    with st.form("auth_form"):
        email = st.text_input("邮箱")
        password = st.text_input("密码", type="password")
        mode = st.radio("模式", ["登录", "注册"], horizontal=True)
        submitted = st.form_submit_button("提交")

        if submitted:
            try:
                if mode == "登录":
                    # 使用 Supabase 原生登录
                    resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if resp.user:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error("登录失败，请检查邮箱和密码")
                else:  # 注册
                    resp = supabase.auth.sign_up({"email": email, "password": password})
                    if resp.user:
                        st.success("注册成功！请登录。")
                    else:
                        st.error("注册失败，可能邮箱已存在")
            except Exception as e:
                st.error(f"认证出错: {e}")

# 5. 主界面
if not st.session_state.authenticated:
    st.title("🔐 欢迎使用 TechLife Suite")
    st.markdown("请登录或注册以继续")
    auth_form()
else:
    # 侧边栏显示用户信息和登出按钮
    st.sidebar.success(f"已登录: {st.session_state.user_email}")
    if st.sidebar.button("🚪 登出"):
        logout()

    # 主区域展示三个工具
    st.title("🚀 TechLife Suite")
    st.markdown("请选择您要使用的 AI 分析工具：")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📊 产品可行性分析")
        st.link_button("立即使用", "https://product.techlife-suite.com")
    with col2:
        st.markdown("### ⚙️ DFMEA 分析")
        st.link_button("立即使用", "https://para-vary.techlife-suite.com")
    with col3:
        st.markdown("### 📏 公差分析")
        st.link_button("立即使用", "https://stack-tolerance.techlife-suite.com")
