# Tutorial-to-Tool Mapping: Basic Usage

## Overview
This document provides exact mapping between tutorial sections and extracted tools, demonstrating complete coverage and fidelity.

## Tutorial Structure Analysis

### Tutorial File
- **Path**: `notebooks/basic_usage/basic_usage_execution_final.ipynb`
- **Original**: `repo/minisom/examples/BasicUsage.ipynb`
- **Reference**: https://github.com/JustWhyKing/minisom/blob/master/examples/BasicUsage.ipynb

---

## Section-by-Section Mapping

### Section 1: Data Loading and Normalization
**Tutorial Code** (Cell 727667c8):
```python
import pandas as pd
import numpy as np
columns=['area', 'perimeter', 'compactness', 'length_kernel', 'width_kernel',
         'asymmetry_coefficient', 'length_kernel_groove', 'target']
data = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt',
                   names=columns, sep='\t+', engine='python')
target = data['target'].values
label_names = {1:'Kama', 2:'Rosa', 3:'Canadian'}
data = data[data.columns[:-1]]
# data normalization
data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)
data = data.values
```

**Extracted Tool**: `minisom_train_som`
- ✅ Data loading from CSV/TXT (parameterized file path)
- ✅ Target extraction (parameterized column name)
- ✅ Z-score normalization (exact formula)
- ✅ Label mapping support (parameterized dictionary)

**Parameters Added**:
- `data_path`: User's data file (replaces hardcoded URL)
- `target_column`: Column name to exclude (replaces hardcoded 'target')

**Parameters Preserved**:
- Normalization formula: `(data - mean) / std`
- Column-wise statistics (axis=0)

---

### Section 2: SOM Initialization and Training
**Tutorial Code** (Cell 489bf04a):
```python
# Initialization and training
n_neurons = 9
m_neurons = 9
som = MiniSom(n_neurons, m_neurons, data.shape[1], sigma=1.5, learning_rate=.5,
              neighborhood_function='gaussian', random_seed=0, topology='rectangular')

som.pca_weights_init(data)
som.train(data, 1000, verbose=False)  # random training
```

**Extracted Tool**: `minisom_train_som`
- ✅ MiniSom initialization (exact parameters)
- ✅ PCA weight initialization (exact call: `som.pca_weights_init(data)`)
- ✅ Training (exact call: `som.train(data, 1000, verbose=False)`)

**Parameters Added**:
- `n_neurons`: Grid dimension 1 (tutorial value: 9)
- `m_neurons`: Grid dimension 2 (tutorial value: 9)
- `sigma`: Neighborhood spread (tutorial value: 1.5)
- `learning_rate`: Initial learning rate (tutorial value: 0.5)
- `neighborhood_function`: Function type (tutorial value: 'gaussian')
- `random_seed`: Reproducibility seed (tutorial value: 0)
- `topology`: Map topology (tutorial value: 'rectangular')
- `n_iterations`: Training iterations (tutorial value: 1000)

**Parameters NOT Added**:
- ❌ No additional parameters in `pca_weights_init()` call
- ❌ No additional parameters in `train()` call beyond tutorial

---

### Section 3: Distance Map Visualization
**Tutorial Code** (Cell a4cd501b):
```python
plt.figure(figsize=(9, 9))

plt.pcolor(som.distance_map().T, cmap='bone_r')  # plotting the distance map as background
plt.colorbar()

# Plotting the response for each pattern in the iris dataset
# different colors and markers for each label
markers = ['o', 's', 'D']
colors = ['C0', 'C1', 'C2']
for cnt, xx in enumerate(data):
    w = som.winner(xx)  # getting the winner
    # place a marker on the winning position for the sample xx
    plt.plot(w[0]+.5, w[1]+.5, markers[target[cnt]-1], markerfacecolor='None',
             markeredgecolor=colors[target[cnt]-1], markersize=12, markeredgewidth=2)

plt.show()
```

**Extracted Tool**: `minisom_visualize_distance_map`
- ✅ Figure creation (parameterized figsize)
- ✅ Distance map calculation (exact call: `som.distance_map().T`)
- ✅ Pseudocolor plot (exact: `plt.pcolor(..., cmap='bone_r')`)
- ✅ Colorbar (exact call: `plt.colorbar()`)
- ✅ Marker shapes (exact list: `['o', 's', 'D']`)
- ✅ Marker colors (exact list: `['C0', 'C1', 'C2']`)
- ✅ Winner calculation (exact call: `som.winner(xx)`)
- ✅ Marker positioning (exact formula: `w[0]+.5, w[1]+.5`)
- ✅ Marker properties (exact: markersize=12, markeredgewidth=2)

**Parameters Added**:
- `figsize`: Figure dimensions (tutorial value: (9, 9))

**Data Structures Preserved**:
- ✅ Marker list: `['o', 's', 'D']` (not converted to string)
- ✅ Color list: `['C0', 'C1', 'C2']` (not converted to string)
- ✅ Indexing formula: `target[cnt]-1` (exact from tutorial)

---

### Section 4: Scatter Plot Visualization
**Tutorial Code** (Cell 7dd10cf8):
```python
w_x, w_y = zip(*[som.winner(d) for d in data])
w_x = np.array(w_x)
w_y = np.array(w_y)

plt.figure(figsize=(10, 9))
plt.pcolor(som.distance_map().T, cmap='bone_r', alpha=.2)
plt.colorbar()

for c in np.unique(target):
    idx_target = target==c
    plt.scatter(w_x[idx_target]+.5+(np.random.rand(np.sum(idx_target))-.5)*.8,
                w_y[idx_target]+.5+(np.random.rand(np.sum(idx_target))-.5)*.8,
                s=50, c=colors[c-1], label=label_names[c])
plt.legend(loc='upper right')
plt.grid()
plt.show()
```

**Extracted Tool**: `minisom_visualize_scatter_map`
- ✅ Winner coordinate extraction (exact: `zip(*[som.winner(d) for d in data])`)
- ✅ Array conversion (exact: `np.array(w_x)`)
- ✅ Figure creation (parameterized figsize)
- ✅ Distance map background (exact: alpha=.2)
- ✅ Scatter plot with offset (exact formula: `+.5+(np.random.rand(n)-.5)*.8`)
- ✅ Class-based coloring (exact indexing: `colors[c-1]`)
- ✅ Legend placement (exact: `loc='upper right'`)
- ✅ Grid overlay (exact call: `plt.grid()`)

**Parameters Added**:
- `figsize`: Figure dimensions (tutorial value: (10, 9))

**Formulas Preserved**:
- ✅ Random offset: `+.5+(np.random.rand(n)-.5)*.8` (exact formula)
- ✅ Class indexing: `c-1` (exact from tutorial)
- ✅ Point size: `s=50` (exact from tutorial)

---

### Section 5: Activation Frequency Visualization
**Tutorial Code** (Cell 9ad664ad):
```python
plt.figure(figsize=(7, 7))
frequencies = som.activation_response(data)
plt.pcolor(frequencies.T, cmap='Blues')
plt.colorbar()
plt.show()
```

**Extracted Tool**: `minisom_visualize_activation_frequencies`
- ✅ Figure creation (parameterized figsize)
- ✅ Frequency calculation (exact call: `som.activation_response(data)`)
- ✅ Pseudocolor plot (exact: `plt.pcolor(frequencies.T, cmap='Blues')`)
- ✅ Colorbar (exact call: `plt.colorbar()`)

**Parameters Added**:
- `figsize`: Figure dimensions (tutorial value: (7, 7))

**Parameters NOT Added**:
- ❌ No additional parameters in `activation_response()` call

---

### Section 6: Class Distribution Pie Charts
**Tutorial Code** (Cell eac4a83d):
```python
import matplotlib.gridspec as gridspec

labels_map = som.labels_map(data, [label_names[t] for t in target])

fig = plt.figure(figsize=(9, 9))
the_grid = gridspec.GridSpec(n_neurons, m_neurons, fig)
for position in labels_map.keys():
    label_fracs = [labels_map[position][l] for l in label_names.values()]
    plt.subplot(the_grid[n_neurons-1-position[1], position[0]], aspect=1)
    patches, texts = plt.pie(label_fracs)

plt.legend(patches, label_names.values(), bbox_to_anchor=(3.5, 6.5), ncol=3)
plt.show()
```

**Extracted Tool**: `minisom_visualize_class_distribution`
- ✅ Labels map creation (exact call: `som.labels_map(data, labels)`)
- ✅ Figure creation (parameterized figsize)
- ✅ Grid specification (exact: `gridspec.GridSpec(n_neurons, m_neurons, fig)`)
- ✅ Subplot positioning (exact indexing: `[n_neurons-1-position[1], position[0]]`)
- ✅ Pie chart creation (exact call: `plt.pie(label_fracs)`)
- ✅ Legend placement (exact: `bbox_to_anchor=(3.5, 6.5), ncol=3`)

**Parameters Added**:
- `n_neurons`: Grid dimension 1 (tutorial value: 9)
- `m_neurons`: Grid dimension 2 (tutorial value: 9)
- `figsize`: Figure dimensions (tutorial value: (9, 9))

**Formulas Preserved**:
- ✅ Grid indexing: `[n_neurons-1-position[1], position[0]]` (exact)
- ✅ Label fraction extraction: `[labels_map[position][l] for l in label_names.values()]` (exact)

---

### Section 7: Training Error Tracking
**Tutorial Code** (Cell 1e3c199b):
```python
som = MiniSom(10, 10, data.shape[1], sigma=1.5, learning_rate=.5,
              neighborhood_function='gaussian', random_seed=10)

max_iter = 200
q_error = []
t_error = []
d_error = []

for i in range(max_iter):
    rand_i = np.random.randint(len(data))
    som.update(data[rand_i], som.winner(data[rand_i]), i, max_iter)
    q_error.append(som.quantization_error(data))
    t_error.append(som.topographic_error(data))
    d_error.append(som.distortion_measure(data))

plt.subplot(3,1,1)
plt.plot(np.arange(max_iter), q_error)
plt.ylabel('quantization error')
plt.subplot(3,1,2)
plt.plot(np.arange(max_iter), t_error)
plt.ylabel('topographic error')
plt.subplot(3,1,3)
plt.plot(np.arange(max_iter), d_error)
plt.ylabel('divergence measure')
plt.xlabel('iteration index')
plt.tight_layout()
plt.show()
```

**Extracted Tool**: `minisom_track_training_errors`
- ✅ MiniSom initialization (exact parameters)
- ✅ Error list initialization (exact: `q_error = []`)
- ✅ Training loop (exact: `for i in range(max_iter)`)
- ✅ Random sample selection (exact: `np.random.randint(len(data))`)
- ✅ Update call (exact: `som.update(data[rand_i], som.winner(data[rand_i]), i, max_iter)`)
- ✅ Error tracking (exact calls to quantization_error, topographic_error, distortion_measure)
- ✅ Subplot layout (exact: 3 rows, 1 column)
- ✅ Plot formatting (exact y-labels, x-label)
- ✅ Tight layout (exact call: `plt.tight_layout()`)

**Parameters Added**:
- `n_neurons`: Grid dimension 1 (tutorial value: 10)
- `m_neurons`: Grid dimension 2 (tutorial value: 10)
- `max_iter`: Training iterations (tutorial value: 200)
- `random_seed`: Reproducibility (tutorial value: 10)

**Parameters NOT Added**:
- ❌ No additional parameters in `update()` call
- ❌ No additional parameters in error calculation calls

**Formulas Preserved**:
- ✅ Random index: `np.random.randint(len(data))` (exact)
- ✅ X-axis: `np.arange(max_iter)` (exact)

---

## Coverage Summary

### ✅ Complete Coverage
- **7 tutorial sections** → **6 extracted tools**
- Sections 1-2 combined into `minisom_train_som` (natural workflow grouping)
- All tutorial code represented in extracted tools
- No tutorial functionality omitted

### ✅ Exact Function Calls
All library function calls preserved exactly:
1. `som.pca_weights_init(data)` - NO added parameters
2. `som.train(data, 1000, verbose=False)` - EXACT parameters
3. `som.distance_map()` - NO added parameters
4. `som.winner(xx)` - NO added parameters
5. `som.activation_response(data)` - NO added parameters
6. `som.labels_map(data, labels)` - EXACT parameters
7. `som.update(data[i], som.winner(data[i]), i, max_iter)` - EXACT parameters
8. `som.quantization_error(data)` - NO added parameters
9. `som.topographic_error(data)` - NO added parameters
10. `som.distortion_measure(data)` - NO added parameters

### ✅ Exact Data Structures
All data structures preserved:
1. Marker list: `['o', 's', 'D']`
2. Color list: `['C0', 'C1', 'C2']`
3. Indexing formulas: `target[cnt]-1`, `colors[c-1]`
4. Position offsets: `w[0]+.5, w[1]+.5`
5. Random offset: `+.5+(np.random.rand(n)-.5)*.8`
6. Grid indexing: `[n_neurons-1-position[1], position[0]]`

### ✅ No Added Parameters
Zero function parameters added that weren't in original tutorial:
- ✅ All MiniSom calls use exact tutorial parameters or library defaults
- ✅ No convenience parameters added
- ✅ No "helpful" enhancements added
- ✅ No generalized patterns substituted

### ✅ Real-World Adaptation
Parameterized only tutorial-specific values:
- File paths (tutorial: hardcoded URL)
- Column names (tutorial: hardcoded 'target')
- Label mappings (tutorial: specific to seeds dataset)
- Grid sizes (tutorial: specific values)
- Hyperparameters (tutorial: specific values)

---

## Validation Checklist

### Tutorial Fidelity
- [✓] All tutorial sections covered
- [✓] All tutorial visualizations reproduced
- [✓] All tutorial algorithms preserved
- [✓] Exact function calls maintained
- [✓] Exact data structures maintained
- [✓] No added function parameters
- [✓] No generalized patterns

### Real-World Applicability
- [✓] User data file inputs
- [✓] Configurable parameters
- [✓] Production error handling
- [✓] Workflow integration
- [✓] No hardcoded paths
- [✓] No demonstration shortcuts

### Code Quality
- [✓] Type annotations
- [✓] Clear documentation
- [✓] Standardized returns
- [✓] High-resolution outputs
- [✓] Absolute file paths
- [✓] Environment variable support

---

## Conclusion

**100% tutorial coverage** with **exact fidelity** while enabling **real-world application**.

Every line of analytical code from the tutorial is represented in the extracted tools, with exact preservation of:
- Function calls and parameters
- Data structures and formulas
- Visualization styles and settings
- Error tracking methodology

No compromises made. Ready for testing.
