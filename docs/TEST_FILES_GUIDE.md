# 测试文件使用指南

## 📁 测试文件位置

已创建两个测试CSV文件在：
```
/home/zephyr/Paper2Agent-main/web/
├── test_data_iris.csv        # 鸢尾花数据集 (30行 × 5列)
└── test_data_clusters.csv    # 聚类数据集 (22行 × 4列)
```

## 📊 文件格式说明

### 1. test_data_iris.csv (鸢尾花数据集)

**用途：** 适合测试分类和可视化工具

**数据结构：**
- **特征列** (数值型):
  - `feature1`: 花萼长度 (4.4-7.2)
  - `feature2`: 花萼宽度 (2.2-3.9)
  - `feature3`: 花瓣长度 (1.3-6.1)
  - `feature4`: 花瓣宽度 (0.1-2.5)
- **标签列** (分类):
  - `label`: 品种 (setosa, versicolor, virginica)

**数据示例：**
```csv
feature1,feature2,feature3,feature4,label
5.1,3.5,1.4,0.2,setosa
7.0,3.2,4.7,1.4,versicolor
6.3,3.3,6.0,2.5,virginica
```

**数据分布：**
- setosa: 10个样本
- versicolor: 10个样本
- virginica: 10个样本
- 总计: 30个样本

---

### 2. test_data_clusters.csv (聚类数据集)

**用途：** 适合测试聚类和基础训练工具

**数据结构：**
- **特征列** (数值型):
  - `x`: X坐标 (2.2-12.9)
  - `y`: Y坐标 (2.9-13.6)
  - `z`: Z坐标 (1.4-11.2)
- **标签列** (分类):
  - `cluster`: 簇标签 (A, B, C)

**数据示例：**
```csv
x,y,z,cluster
2.5,3.2,1.8,A
7.2,8.5,6.3,B
12.5,13.2,10.8,C
```

**数据分布：**
- Cluster A: 8个样本 (低值区域)
- Cluster B: 7个样本 (中值区域)
- Cluster C: 7个样本 (高值区域)
- 总计: 22个样本

---

## 🧪 如何使用测试文件

### 方法1: Web界面 - 工具执行器

1. **打开项目页面**
   ```
   http://localhost:5000/project/Minisom
   ```

2. **选择工具**
   - 左侧工具列表选择 `minisom_train_som`

3. **上传文件**
   - 在 `data_path` 参数处点击"上传文件"按钮
   - 选择 `test_data_iris.csv` 或 `test_data_clusters.csv`

4. **设置参数**
   ```
   target_column: label (对于iris) 或 cluster (对于clusters)
   n_neurons: 10
   m_neurons: 10
   n_iterations: 100
   ```

5. **执行**
   - 点击"执行工具"按钮
   - 查看结果输出

### 方法2: Web界面 - Claude聊天

1. **配置API**
   - 选择"API 模式"
   - 输入 Anthropic API Key

2. **上传并对话**
   ```
   [点击📎上传 test_data_iris.csv]
   
   用户: 请使用 minisom_train_som 工具训练一个 10x10 的SOM，
        target_column 是 label，训练100次迭代
   
   Claude: [自动调用工具执行]
   ```

3. **后续分析**
   ```
   用户: 请可视化距离地图
   Claude: [调用 minisom_visualize_distance_map]
   ```

### 方法3: 直接路径方式（传统方法）

如果不想上传文件，也可以直接输入路径：
```
data_path: /home/zephyr/Paper2Agent-main/web/test_data_iris.csv
```

---

## 🔧 推荐的工具测试流程

### 完整测试流程（使用iris数据）

```
1. minisom_train_som
   - data_path: [上传 test_data_iris.csv]
   - target_column: label
   - n_neurons: 10
   - m_neurons: 10
   - n_iterations: 100
   ↓ 输出: som_trained_*.pkl

2. minisom_visualize_distance_map
   - model_path: [从上一步输出获取]
   - data_path: [相同文件]
   ↓ 输出: distance_map_*.png

3. minisom_visualize_class_distribution
   - model_path: [从步骤1输出]
   - data_path: [相同文件]
   - target_column: label
   ↓ 输出: class_distribution_*.png

4. minisom_visualize_activation_frequencies
   - model_path: [从步骤1输出]
   - data_path: [相同文件]
   ↓ 输出: activation_frequencies_*.png
```

### 快速测试流程（使用clusters数据）

```
1. minisom_train_som
   - data_path: [上传 test_data_clusters.csv]
   - target_column: cluster
   - n_neurons: 5
   - m_neurons: 5
   - n_iterations: 50
   ↓ 快速训练完成

2. minisom_visualize_distance_map
   ↓ 查看聚类效果
```

---

## 📋 工具与文件匹配表

| 工具名称 | 推荐文件 | 是否需要target_column | 说明 |
|---------|---------|---------------------|------|
| minisom_train_som | 两者都可 | 可选 | 基础训练工具 |
| minisom_visualize_distance_map | 两者都可 | 否 | 距离地图 |
| minisom_visualize_scatter_map | iris (更好) | 否 | 散点图 |
| minisom_visualize_activation_frequencies | 两者都可 | 否 | 激活频率 |
| minisom_visualize_class_distribution | iris | 是 (必须) | 类别分布 |
| minisom_track_training_errors | 两者都可 | 否 | 训练误差 |

---

## 🎯 预期输出示例

### 训练成功输出：
```json
{
  "success": true,
  "result": {
    "message": "SOM training completed successfully",
    "model_info": {
      "shape": [10, 10],
      "input_len": 4,
      "iterations": 100
    },
    "artifacts": [
      {
        "description": "Trained SOM model (pickle file)",
        "path": "/path/to/som_trained_*.pkl"
      },
      {
        "description": "Normalized training data",
        "path": "/path/to/som_trained_*_data.npy"
      }
    ]
  }
}
```

### 可视化成功输出：
```json
{
  "success": true,
  "result": {
    "message": "Distance map visualization created",
    "artifacts": [
      {
        "description": "Distance map with markers",
        "path": "/path/to/distance_map_*.png"
      }
    ]
  }
}
```

---

## ❗ 常见问题

### Q: 上传后显示"上传中..."不消失
**A:** 检查文件大小和网络连接，刷新页面重试

### Q: 工具执行失败："File not found"
**A:** 确认文件已成功上传，路径应该显示 `__UPLOAD__:/path/...`

### Q: 训练时间过长
**A:** 减少 `n_iterations` 参数，例如从1000改为100

### Q: 可视化工具找不到模型
**A:** 确保先执行 `minisom_train_som` 并记录输出的模型路径

---

## 📖 数据格式要求总结

**MiniSom工具接受的CSV格式：**

✅ **必须有列标题** (第一行)
✅ **特征列必须是数值型** (int或float)
✅ **可选的标签列** (字符串或数值)
✅ **无缺失值** (NaN会导致错误)
✅ **逗号分隔** (.csv) 或制表符分隔 (.txt)

**示例有效格式：**
```csv
col1,col2,col3,label
1.0,2.0,3.0,A
4.0,5.0,6.0,B
```

**示例无效格式：**
```csv
1.0,2.0,3.0      ❌ 缺少列标题
col1,col2,NaN    ❌ 包含缺失值
"a","b","c"      ❌ 非数值数据
```

---

## 🚀 快速开始命令

**启动Web服务器：**
```bash
cd /home/zephyr/Paper2Agent-main
source .venv/bin/activate
python web/app.py
```

**浏览器访问：**
```
http://localhost:5000
```

**直接访问项目页面：**
```
http://localhost:5000/project/Minisom
```

---

## 📊 数据生成说明

这些测试文件是基于经典数据集创建的：

- **test_data_iris.csv**: 基于Iris数据集的精简版
- **test_data_clusters.csv**: 人工生成的3簇数据，簇间分离明显

如需生成更多测试数据，可以运行：
```python
import numpy as np
import pandas as pd

# 生成随机数据
np.random.seed(42)
data = np.random.randn(50, 4)
df = pd.DataFrame(data, columns=['f1', 'f2', 'f3', 'f4'])
df['label'] = np.random.choice(['A', 'B', 'C'], 50)
df.to_csv('test_data_custom.csv', index=False)
```
