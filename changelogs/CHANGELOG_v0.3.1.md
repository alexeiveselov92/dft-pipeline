# DFT-Pipeline v0.3.1 - Enhanced A/B Testing

## 🚀 Major A/B Testing Improvements

### ✨ Automatic Multi-Group Comparisons
- **BREAKING CHANGE**: Removed `control_group` and `treatment_group` parameters
- **NEW**: Automatic detection of all groups in data
- **NEW**: Automatic pairwise comparisons of all groups (N groups = N*(N-1)/2 comparisons)
- **BENEFIT**: No need to manually specify which groups to compare - just provide the group column!

### 🔧 Configuration Simplification
**Before (v0.3.0):**
```yaml
config:
  test_type: "ttest"
  metric_column: "revenue"
  group_column: "experiment_group"
  control_group: "control"      # ❌ REMOVED
  treatment_group: "treatment"  # ❌ REMOVED
  alpha: 0.05
```

**After (v0.3.1):**
```yaml
config:
  test_type: "ttest"
  metric_column: "revenue"
  group_column: "experiment_group"
  alpha: 0.05
```

### 🧮 Pandas-Free Architecture
- **REMOVED**: All pandas dependencies from A/B testing code
- **IMPROVED**: Pure PyArrow + NumPy implementation for better performance
- **BENEFIT**: Faster processing and reduced memory usage

### 📚 Updated Documentation
- **UPDATED**: All examples show multi-group experiments (4+ groups)
- **UPDATED**: README.md with pandas-free code examples
- **UPDATED**: AB_TESTING.md with new configuration format
- **ADDED**: Clear explanation of pairwise comparison results

### 🔒 Package Security
- **EXCLUDED**: Development folders (`*for_developing`) from published package
- **CLEAN**: Only production-ready code included in PyPI package

## 🛠 Technical Changes
- Updated `ABTestConfig` model to remove group specification parameters
- Enhanced `DataPreparer` to auto-detect and process all groups
- Maintained backward compatibility for all test types (ttest, ztest, cuped_ttest, bootstrap)
- Preserved all statistical test accuracy and functionality

## 📦 Migration Guide
1. Remove `control_group` and `treatment_group` from your pipeline configurations
2. Ensure your data contains all experiment groups in the `group_column`
3. Expect multiple result rows for experiments with >2 groups
4. Update any downstream processing to handle pairwise comparison results

## 🎯 Example Results
**3 groups** → **3 comparisons**:
- control vs treatment
- control vs variant_a  
- treatment vs variant_a

**4 groups** → **6 comparisons**:
- All possible pairwise combinations automatically generated

---
*This version represents a major step forward in A/B testing capabilities while maintaining full statistical accuracy and expanding support for complex multi-variant experiments.*