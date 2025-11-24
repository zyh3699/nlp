# 文件上传功能使用指南

## 功能概述

Paper2Agent Web界面现在支持直接上传CSV和其他数据文件，无需手动输入文件路径。

## 支持的文件格式

- CSV (.csv)
- 文本文件 (.txt)
- JSON (.json)
- Excel (.xlsx, .xls)

## 使用方式

### 1. 在工具执行器中上传文件

当您选择一个需要文件路径的工具时（例如包含`file`、`path`或`csv`关键字的参数），系统会自动显示文件上传按钮。

**步骤：**
1. 在左侧选择一个工具
2. 在右侧的参数表单中，找到文件路径参数
3. 点击"上传文件"按钮
4. 选择您的文件
5. 文件会自动上传并填充路径
6. 点击"执行工具"按钮

### 2. 在Claude聊天中上传文件

在与Claude的对话中，您可以直接上传文件并在消息中引用。

**步骤：**
1. 点击聊天输入框左侧的📎（回形针）按钮
2. 选择一个或多个文件上传
3. 上传的文件会显示在输入框上方
4. 输入您的消息，例如："请分析这个CSV文件"
5. 发送消息时，文件路径会自动包含在消息中
6. Claude可以使用MCP工具处理这些文件

**示例对话：**
```
用户: [上传 data.csv] 请使用MiniSom工具分析这个数据集
Claude: 好的，我将使用加载和训练工具来分析您上传的data.csv文件...
```

## 文件存储

- 上传的文件存储在 `web/uploads/` 目录
- 文件名会自动添加时间戳前缀以避免冲突
- 格式：`YYYYMMDD_HHMMSS_原始文件名.csv`

## 技术细节

### 后端API

**文件上传端点：**
```
POST /api/upload
Content-Type: multipart/form-data
```

**返回示例：**
```json
{
  "success": true,
  "filepath": "/home/user/Paper2Agent-main/web/uploads/20250122_143025_data.csv",
  "filename": "20250122_143025_data.csv"
}
```

**工具执行端点：**
```
POST /api/project/{project_name}/execute-mcp-tool
Content-Type: application/json

{
  "tool_name": "load_and_train_som",
  "parameters": {
    "data_file": "__UPLOAD__:/path/to/file.csv",
    "som_shape": [10, 10]
  }
}
```

### 前端JavaScript

**文件上传处理函数：**
- `handleFileUpload(input, targetParamId)` - 工具参数文件上传
- `handleChatFileUpload(input)` - 聊天文件上传
- `updateChatFileList()` - 更新聊天文件列表
- `removeChatFile(index)` - 删除已上传文件

## 安全注意事项

1. **文件大小限制**：最大100MB
2. **文件类型验证**：仅接受指定的文件格式
3. **临时存储**：上传的文件存储在本地，不会上传到云端
4. **清理建议**：定期清理 `web/uploads/` 目录中的旧文件

## 故障排除

### 上传失败
- 检查文件大小是否超过100MB
- 确认文件格式是否受支持
- 查看浏览器控制台的错误信息

### 工具执行失败
- 确认文件已成功上传（显示文件名而非"上传中..."）
- 检查文件格式是否与工具要求匹配
- 查看后端日志：`web/app.py`的输出

### 聊天中看不到文件
- 刷新页面重试
- 检查`chatUploadedFiles`数组（浏览器开发者工具）
- 确认文件上传API返回成功

## 示例场景

### 场景1：分析CSV数据
```
1. 上传 sales_data.csv
2. 在聊天中输入："请使用MCP工具对这个销售数据进行聚类分析"
3. Claude会自动调用相应的MCP工具处理文件
```

### 场景2：直接执行工具
```
1. 左侧选择"load_and_train_som"工具
2. 在data_file参数处点击"上传文件"
3. 选择您的CSV文件
4. 填写其他参数（如som_shape）
5. 点击"执行工具"
```

## 更新日志

- **2025-01-22**: 添加文件上传功能
  - 支持工具参数文件上传
  - 支持聊天中文件上传
  - 自动检测文件类型参数
  - 文件路径自动替换机制
