<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TechLife Suite 门户</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            min-height: 100vh;
            background-color: #f5f5f5;
        }

        /* 左侧边栏 */
        .sidebar {
            width: 320px;
            background-color: #ffffff;
            padding: 30px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: fixed;
            height: 100%;
            overflow-y: auto;
        }

        .logo-area {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
        }
        .logo-area::before {
            content: '';
            display: inline-block;
            width: 24px;
            height: 24px;
            background-color: #007AFF; /* 蓝色图标示意 */
            margin-right: 10px;
        }

        .info-section h3 {
            font-size: 18px;
            margin-top: 0;
            margin-bottom: 15px;
            color: #333;
            display: flex;
            align-items: center;
        }
        .info-section h3::before {
            content: '';
            display: inline-block;
            width: 16px;
            height: 16px;
            background-color: #007AFF;
            margin-right: 8px;
        }

        .info-section p {
            font-size: 14px;
            line-height: 1.6;
            color: #555;
            text-align: justify;
        }

        .info-section ul {
            padding-left: 20px;
            font-size: 14px;
            color: #555;
        }
        .info-section li {
            margin-bottom: 8px;
        }

        .contact-section {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .contact-section h3 {
            font-size: 16px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .contact-section h3::before {
            content: '';
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 1px solid #333;
            margin-right: 8px;
        }
        .contact-section p {
            font-size: 13px;
            color: #666;
            margin: 0;
        }
        .contact-section a {
            color: #007AFF;
            text-decoration: none;
        }

        /* 右侧主内容区 */
        .main-content {
            flex: 1;
            margin-left: 320px; /* 与sidebar宽度一致 */
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }

        /* 顶部语言切换 */
        .top-right-controls {
            position: absolute;
            top: 30px;
            right: 40px;
            display: flex;
            gap: 15px;
            align-items: center;
        }

        .lang-btn {
            background-color: #FF0000; /* 红色背景 */
            color: white; /* 白色字体 */
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            font-weight: 500;
        }
        .lang-btn:hover {
            opacity: 0.9;
        }

        .header-text {
            text-align: center;
            margin-bottom: 40px;
        }
        .header-text h1 {
            font-size: 36px;
            font-weight: 800;
            color: #111;
            margin: 0 0 10px 0;
        }
        .header-text p {
            font-size: 16px;
            color: #666;
            margin: 0;
        }

        /* 登录/注册框 */
        .auth-card {
            background-color: #ffffff;
            width: 400px;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
        }

        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #333; /* 黑色文字 */
            margin-bottom: 8px;
        }
        .input-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc; /* 黑色/灰色边框 */
            border-radius: 6px;
            font-size: 15px;
            box-sizing: border-box;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-group input:focus {
            border-color: #007AFF;
        }

        .password-toggle {
            position: absolute;
            right: 12px;
            top: 38px;
            cursor: pointer;
            color: #999;
            font-size: 14px;
        }

        /* 按钮区域 */
        .button-group {
            display: flex;
            flex-direction: column;
            gap: 15px; /* 按钮间距 */
            margin-top: 10px;
        }

        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 6px;
            font-size: 16px; /* 大字体 */
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
            text-align: center;
        }
        .btn:hover {
            opacity: 0.9;
        }

        .btn-primary {
            background-color: #333; /* 登录按钮：黑色 */
            color: white;
        }

        .btn-secondary {
            background-color: #e0e0e0; /* 注册按钮：浅灰底色 */
            color: #333; /* 黑色文字 */
        }

        /* 响应式 */
        @media (max-width: 900px) {
            .sidebar {
                display: none; /* 移动端隐藏侧边栏 */
            }
            .main-content {
                margin-left: 0;
                padding: 20px;
            }
            .auth-card {
                width: 100%;
                max-width: 350px;
            }
        }
    </style>
</head>
<body>

    <!-- 左侧栏 -->
    <div class="sidebar">
        <div>
            <div class="logo-area">TechLife Suite</div>

            <div class="info-section">
                <h3>关于系统</h3>
                <p>TechLife Suite 是专为研发工程师打造的 AI 辅助 DFX（大设计协同）平台。</p>
                <p>我们致力于通过人工智能技术，简化复杂的工程设计流程，帮助团队实现：</p>
                <ul>
                    <li>智能需求分析：快速拆解客户需求与 QCD。</li>
                    <li>自动初案评估：AI 辅助生成 DFX 报告。</li>
                    <li>参数优化设计：利用算法寻找最优方案。</li>
                </ul>
                <p>让 AI 成为您的智能研发工程师。</p>
            </div>
        </div>

        <div class="contact-section">
            <h3>联系我们</h3>
            <p>邮箱: <a href="mailto:Techlife2022@gmail.com">Techlife2022@gmail.com</a></p>
        </div>
    </div>

    <!-- 右侧主区域 -->
    <div class="main-content">

        <!-- 顶部语言切换 -->
        <div class="top-right-controls">
            <button class="lang-btn">中文</button>
            <button class="lang-btn">English</button>
        </div>

        <!-- 标题 -->
        <div class="header-text">
            <h1>TechLife Suite 门户</h1>
            <p>一站式工程研发 AI 工具箱</p>
        </div>

        <!-- 登录注册卡片 -->
        <div class="auth-card">
            <form>
                <div class="input-group">
                    <label for="username">请输入账号</label>
                    <input type="text" id="username" placeholder="">
                </div>

                <div class="input-group" style="position: relative;">
                    <label for="password">请输入密码</label>
                    <input type="password" id="password" placeholder="">
                    <!-- 模拟的小眼睛图标 -->
                    <span class="password-toggle">👁️</span>
                </div>

                <!-- 两个按钮都在框内 -->
                <div class="button-group">
                    <button type="button" class="btn btn-primary">登录</button>
                    <button type="button" class="btn btn-secondary">注册</button>
                </div>
            </form>
        </div>
    </div>

</body>
</html>
