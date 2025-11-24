# 🚀 快速测试步骤

## 测试 minisom_train_som 工具

### 步骤：

1. **访问项目页面**
   ```
   http://localhost:5000/project/Minisom
   ```

2. **选择工具**
   - 左侧工具列表找到并点击 `minisom_train_som`

3. **上传文件**
   - 在 `data_path` 参数处点击"上传文件"按钮
   - 选择 `/home/zephyr/Paper2Agent-main/web/test_data_iris.csv`
   - 等待上传完成（显示文件路径）

4. **填写参数**
   ```
   target_column: label          ⬅️ 重要！必须填写这个
   n_neurons: 10
   m_neurons: 10
   n_iterations: 100
   ```
   
   其他参数保持默认值即可

5. **执行工具**
   - 点击"执行工具"按钮
   - 查看结果

---

## 参数说明

### 必填参数：
- **data_path**: 通过上传按钮选择CSV文件

### 重要可选参数：
- **target_column**: `label` （如果不填，会把标签列当作特征处理，导致错误）
- **n_neurons**: `10` (SOM的行数)
- **m_neurons**: `10` (SOM的列数)
- **n_iterations**: `100` (训练迭代次数，可以少一点如50来快速测试)

### 其他可选参数（可保持默认）：
- sigma: 1.5
- learning_rate: 0.5
- neighborhood_function: gaussian
- random_seed: 0
- topology: rectangular
- out_prefix: (留空，系统自动生成)

---

## 预期输出

成功时会返回类似这样的结果：

```json
{
  "message": "SOM training completed successfully",
  "model_info": {
    "shape": [10, 10],
    "input_len": 4,
    "iterations": 100
  },
  "artifacts": [
    {
      "description": "Trained SOM model (pickle file)",
      "path": "/path/to/Minisom_Agent/tmp/outputs/som_trained_*.pkl"
    },
    {
      "description": "Normalized training data",
      "path": "/path/to/Minisom_Agent/tmp/outputs/som_trained_*_data.npy"
    },
    {
      "description": "Target labels",
      "path": "/path/to/Minisom_Agent/tmp/outputs/som_trained_*_target.npy"
    }
  ]
}
```

---

## 常见错误

### ❌ "Could not convert [...] to numeric"
**原因**: 没有填写 `target_column` 参数，导致 `label` 列被当作特征处理

**解决**: 在 `target_column` 输入框填写 `label`

### ❌ "File not found"
**原因**: 文件上传失败或路径错误

**解决**: 
1. 确认文件已成功上传（输入框显示完整路径）
2. 检查浏览器控制台是否有上传错误
3. 刷新页面重试

### ❌ "Tool minisom_train_som not found"
**原因**: MCP工具加载失败

**解决**: 
1. 检查 Minisom_Agent/src/tools/ 目录存在
2. 重启Web服务器
3. 查看终端日志

---

## 使用 test_data_clusters.csv

如果使用 `test_data_clusters.csv` 文件：

```
data_path: [上传 test_data_clusters.csv]
target_column: cluster        ⬅️ 注意这里是 "cluster" 而不是 "label"
n_neurons: 5
m_neurons: 5
n_iterations: 50
```

---

## 下一步测试

训练完成后，可以测试可视化工具：

1. **minisom_visualize_distance_map**
   - model_path: [从训练结果中复制模型路径]
   - data_path: [上传相同的CSV文件]

2. **minisom_visualize_class_distribution**
   - model_path: [从训练结果中复制]
   - data_path: [上传相同的CSV文件]
   - target_column: label (或 cluster)

---

## 提示

💡 **填写参数时的注意事项：**
- 字符串参数（如 target_column）直接输入文本，不需要引号
- 数值参数会自动转换为数字类型
- 空的参数不会被发送到后端（除非是空字符串）
- 文件路径参数必须通过上传按钮设置

💡 **测试技巧：**
- 第一次测试时用较少的迭代次数（如50）来快速验证
- 成功后再增加迭代次数（如1000）获得更好的结果
- 使用浏览器开发者工具（F12）查看网络请求和响应
