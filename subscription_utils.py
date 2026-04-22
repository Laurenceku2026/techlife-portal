# subscription_utils.py
import streamlit as st
from supabase import create_client

# 获取 Supabase 客户端（使用缓存）
@st.cache_resource
def get_supabase_client():
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

# 多语言文本
_SUBSCRIPTION_TEXTS = {
    "zh": {
        "fetch_error": "获取订阅信息失败: {}",
        "update_error": "更新使用次数失败: {}",
        "free_limit_warning": "您本月免费次数已用完（{}次）。请升级订阅以继续使用。",
        "usage_left": "本月剩余免费次数: {}",
        "subscription_plan": "订阅计划",
        "pro": "专业版",
        "free": "免费版",
        "unlimited": "无限次使用",
        "upgrade_button": "升级订阅",
        "sync_success": "用户记录已同步",
        "default_insert_error": "创建用户记录失败: {}",
    },
    "en": {
        "fetch_error": "Failed to fetch subscription info: {}",
        "update_error": "Failed to update usage count: {}",
        "free_limit_warning": "You have used up your free trial ({} times). Please upgrade to continue.",
        "usage_left": "Free trial remaining this month: {}",
        "subscription_plan": "Subscription Plan",
        "pro": "Pro",
        "free": "Free",
        "unlimited": "Unlimited usage",
        "upgrade_button": "Upgrade",
        "sync_success": "User record synced",
        "default_insert_error": "Failed to create user record: {}",
    }
}

def _t(key, lang=None):
    if lang is None:
        lang = st.session_state.get("language", "zh")
    return _SUBSCRIPTION_TEXTS[lang].get(key, key)

def get_user_subscription(email: str):
    """
    获取用户订阅信息，返回字典包含：
        subscription_status (str): 'free' 或 'active'
        usage_count (int): 已使用次数
        usage_limit (int): 免费版限制次数
    """
    supabase = get_supabase_client()
    try:
        result = supabase.table("user_authentication")\
            .select("subscription_status, usage_count, usage_limit")\
            .eq("email", email)\
            .execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            # 自动创建默认记录（免费版，10次）
            default = {
                "subscription_status": "free",
                "usage_count": 0,
                "usage_limit": 10
            }
            supabase.table("user_authentication").insert({
                "email": email,
                "subscription_status": default["subscription_status"],
                "usage_count": default["usage_count"],
                "usage_limit": default["usage_limit"]
            }).execute()
            return default
    except Exception as e:
        st.error(_t("fetch_error").format(e))
        return {"subscription_status": "free", "usage_count": 0, "usage_limit": 10}

def increment_usage_count(email: str):
    """免费用户使用次数+1（付费用户不计数）"""
    supabase = get_supabase_client()
    user = get_user_subscription(email)
    if user["subscription_status"] == "active":
        return True
    new_count = user["usage_count"] + 1
    try:
        supabase.table("user_authentication")\
            .update({"usage_count": new_count})\
            .eq("email", email)\
            .execute()
        return True
    except Exception as e:
        st.error(_t("update_error").format(e))
        return False

def can_use_tool(email: str) -> bool:
    """
    检查用户是否有权限使用工具。
    返回 True 表示允许；返回 False 表示拒绝（并自动显示提示）。
    """
    user = get_user_subscription(email)
    if user["subscription_status"] == "active":
        return True
    if user["usage_count"] < user["usage_limit"]:
        return True
    else:
        st.warning(_t("free_limit_warning").format(user["usage_limit"]))
        return False

def get_subscription_display(email: str, lang: str = None):
    """
    获取用于 UI 显示的订阅信息（文本、剩余次数等）
    返回字典：{plan_text, remaining_text, is_pro, used, limit}
    """
    user = get_user_subscription(email)
    is_pro = user["subscription_status"] == "active"
    used = user["usage_count"]
    limit = user["usage_limit"]
    lang = lang or st.session_state.get("language", "zh")
    if is_pro:
        plan_text = _t("pro", lang)
        remaining_text = _t("unlimited", lang)
    else:
        plan_text = _t("free", lang)
        remaining = max(0, limit - used)
        remaining_text = _t("usage_left", lang).format(remaining)
    return {
        "plan_text": plan_text,
        "remaining_text": remaining_text,
        "is_pro": is_pro,
        "used": used,
        "limit": limit
    }
