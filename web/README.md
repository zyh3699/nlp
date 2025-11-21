# Paper2Agent Web Interface

## 🎨 功能特点

一个美观、现代化的 Web 界面，用于管理 Paper2Agent 项目的完整生命周期。

### ✨ 主要功能

1. **项目管理**
   - 创建新项目
   - 查看所有项目
   - 实时进度跟踪

2. **Pipeline 执行**
   - 可视化步骤流程
   - 一键执行各个步骤
   - 实时状态监控

3. **工具浏览**
   - 查看生成的工具列表
   - 工具详细信息

4. **结果展示**
   - 输出文件管理
   - 质量报告查看
   - 可视化结果展示

5. **实时监控**
   - 执行状态指示器
   - 自动刷新
   - 通知提醒

## 🚀 快速开始

### 安装依赖

Web 界面需要以下 Python 包：

```bash
cd web
source ../.venv/bin/activate
pip install -r requirements.txt
```

### 启动服务

#### 方法 1：使用启动脚本（推荐）

```bash
cd web
bash start.sh
```

#### 方法 2：手动启动

```bash
cd web
source ../.venv/bin/activate
python app.py
```

### 访问界面

打开浏览器访问：**http://localhost:5000**

## 📖 使用指南

### 1. 主页面

主页面显示：
- 项目统计数据（项目总数、工具数、完成项目数、MCP 服务器数）
- 所有项目的卡片视图
- 项目进度条和状态

### 2. 创建新项目

1. 点击顶部导航栏的 **"新建项目"** 或主页的按钮
2. 填写项目信息：
   - 项目名称（例如：Minisom）
   - GitHub 仓库 URL（例如：https://github.com/JustGlowing/minisom）
3. 点击 **"创建项目"**
4. 系统将自动初始化项目目录

### 3. 项目详情页

点击任意项目卡片进入详情页，包含 5 个标签：

#### Pipeline 标签
- 显示 10 个执行步骤
- 绿色勾号表示已完成
- 灰色圆圈表示未完成
- 点击 **"执行"** 按钮运行步骤

**步骤说明**：
1. Setup Project - 项目初始化
2. Clone Repository - 克隆代码仓库
3. Prepare Folders - 创建目录结构
4. Add Context7 MCP - 添加 Context7 工具
5.1. Setup Environment - 环境配置
5.2. Execute Tutorials - 执行教程
5.3. Extract Tools - 提取工具
5.4. Wrap MCP Server - 生成 MCP 服务器
5.5. Generate Coverage - 生成质量报告
6. Launch MCP Server - 启动 MCP 服务

#### 工具标签
- 查看生成的工具模块
- 显示文件名、代码行数、文件大小

#### 输出文件标签
- 查看 `claude_outputs/` 中的 JSON 文件
- 下载输出文件
- 显示文件大小和修改时间

#### 报告标签
- 查看质量报告（Pylint、Coverage 等）
- 点击报告名称在弹窗中查看内容

#### 可视化标签
- 展示生成的图表和可视化结果
- 支持图片预览

### 4. 实时状态监控

顶部导航栏右侧显示系统状态：
- 🟢 **就绪** - 系统空闲
- 🟡 **执行中** - 正在执行步骤

系统每 5 秒自动检查状态。

## 🏗️ 技术架构

### 后端
- **Flask 3.0.0** - Web 框架
- **Flask-CORS** - 跨域支持
- **Python subprocess** - 执行 Shell 脚本
- **RESTful API** - 标准化接口

### 前端
- **Bootstrap 5.3** - UI 框架
- **Bootstrap Icons** - 图标库
- **jQuery 3.7** - DOM 操作
- **Chart.js 4.4** - 数据可视化
- **自定义 CSS** - 渐变色、卡片动画

### 特色设计
- 🎨 **渐变色主题** - 紫色渐变背景
- 📱 **响应式设计** - 适配各种屏幕
- ✨ **流畅动画** - 卡片悬停效果
- 🔔 **Toast 通知** - 操作反馈
- 🎯 **实时更新** - 自动刷新状态

## 📂 目录结构

```
web/
├── app.py                 # Flask 应用主文件
├── requirements.txt       # Python 依赖
├── start.sh              # 启动脚本
├── templates/            # HTML 模板
│   ├── base.html        # 基础模板
│   ├── index.html       # 主页
│   └── project.html     # 项目详情页
└── static/              # 静态资源
    ├── css/
    │   └── style.css    # 自定义样式
    └── js/
        └── main.js      # 前端逻辑
```

## 🔌 API 端点

### 项目管理
- `GET /api/projects` - 获取所有项目列表
- `GET /api/project/<name>` - 获取项目详情
- `POST /api/project/create` - 创建新项目

### Pipeline 执行
- `GET /api/project/<name>/steps` - 获取步骤状态
- `POST /api/project/<name>/execute/<step>` - 执行步骤

### 结果查询
- `GET /api/project/<name>/tools` - 获取工具列表
- `GET /api/project/<name>/outputs` - 获取输出文件
- `GET /api/project/<name>/reports` - 获取报告列表
- `GET /api/project/<name>/visualizations` - 获取可视化文件

### 系统状态
- `GET /api/status` - 获取当前执行状态

## 🎯 工作流示例

### 完整流程演示

1. **启动 Web 界面**
```bash
cd web
bash start.sh
```

2. **创建 MiniSom 项目**
   - 访问 http://localhost:5000
   - 点击 "新建项目"
   - 项目名称：`Minisom`
   - 仓库 URL：`https://github.com/JustGlowing/minisom`
   - 点击 "创建项目"

3. **执行 Pipeline**
   - 点击 Minisom 项目卡片
   - 在 Pipeline 标签下依次执行步骤 1-6
   - 观察实时进度和状态

4. **查看结果**
   - **工具标签**：查看生成的 12 个 MiniSom 工具
   - **输出文件标签**：下载 step1-5 的输出 JSON
   - **报告标签**：查看 Pylint 和 Coverage 报告
   - **可视化标签**：查看训练结果图表

## ⚙️ 配置说明

### 端口配置

默认端口为 5000，可在 `app.py` 中修改：

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### 调试模式

生产环境请关闭 debug 模式：

```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## 🐛 故障排除

### 问题 1: 依赖安装失败

**解决方案**：
```bash
source ../.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 问题 2: 端口已被占用

**解决方案**：
- 修改 `app.py` 中的端口号
- 或停止占用 5000 端口的进程

### 问题 3: 项目不显示

**解决方案**：
- 确保项目目录以 `_Agent` 结尾
- 检查目录权限
- 查看浏览器控制台错误信息

### 问题 4: 步骤执行失败

**解决方案**：
- 检查 Shell 脚本是否有执行权限
- 查看终端输出的错误信息
- 确认环境变量配置正确

## 🔒 安全注意事项

1. **仅本地访问**：默认配置适合本地开发
2. **生产部署**：需要添加身份验证和 HTTPS
3. **输入验证**：项目名称和 URL 需要额外验证
4. **权限控制**：注意文件系统访问权限

## 📝 开发说明

### 添加新功能

1. 在 `app.py` 中添加 API 端点
2. 在对应模板中添加 HTML
3. 在 `main.js` 中添加前端逻辑
4. 更新 `style.css` 添加样式

### 自定义样式

编辑 `static/css/style.css`，使用 CSS 变量：

```css
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}
```

## 📚 相关资源

- [Flask 文档](https://flask.palletsprojects.com/)
- [Bootstrap 5 文档](https://getbootstrap.com/docs/5.3/)
- [Chart.js 文档](https://www.chartjs.org/docs/)
- [Paper2Agent GitHub](https://github.com/your-repo/Paper2Agent)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 与 Paper2Agent 主项目相同
