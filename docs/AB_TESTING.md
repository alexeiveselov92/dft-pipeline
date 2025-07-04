# A/B Testing with DFT

DFT provides comprehensive A/B testing capabilities for statistical hypothesis testing in experiments. This guide covers all supported test types, configuration options, and best practices.

## Overview

The A/B testing processor allows you to run statistical tests on experiment data through simple pipeline configurations. It supports four main test types:

- **T-Test**: For continuous metrics with normal distribution assumptions
- **Z-Test**: For binary conversion metrics (proportions)
- **CUPED T-Test**: For variance reduction using pre-experiment covariates
- **Bootstrap Test**: Non-parametric testing for robust results

## Quick Start

### Basic Configuration

```yaml
- id: "run_ab_test"
  type: "processor"
  processor_type: "ab_testing"
  config:
    test_type: "ttest"              # ttest, ztest, cuped_ttest, bootstrap
    metric_column: "revenue"        # Column containing the metric to test
    group_column: "experiment_group" # Column containing group assignments
    alpha: 0.05                     # Significance level
    test_direction: "relative"      # relative or absolute effect
```

**Note**: The processor automatically finds all unique groups in your data and compares each group against every other group. No need to specify control/treatment groups!

## Test Types

### 1. T-Test (`ttest`)

Best for testing continuous metrics when data is approximately normally distributed.

**Use cases:**
- Revenue per user
- Session duration
- Rating scores
- Purchase amounts

**Data requirements:**
- Continuous numeric values
- Approximately normal distribution
- Independent observations

**Example:**
```yaml
config:
  test_type: "ttest"
  metric_column: "revenue_per_user"
  group_column: "variant"
  alpha: 0.05
  test_direction: "relative"
  calculate_mde: true
  power: 0.8
```

### 2. Z-Test (`ztest`)

Best for testing binary conversion metrics (success/failure outcomes).

**Use cases:**
- Conversion rates
- Click-through rates
- Signup rates
- Any binary outcome

**Data requirements:**
- Binary values (0/1)
- Large enough sample sizes for normal approximation
- Independent observations

**Example:**
```yaml
config:
  test_type: "ztest"
  metric_column: "converted"      # Must contain 0/1 values
  group_column: "experiment_group"
  alpha: 0.05
  test_direction: "relative"
```

### 3. CUPED T-Test (`cuped_ttest`)

T-test with variance reduction using pre-experiment covariate data. Increases statistical power by reducing noise.

**Use cases:**
- When you have pre-experiment data correlated with your metric
- When you want to increase test sensitivity
- Revenue tests where you have historical revenue data

**Data requirements:**
- Continuous metric values
- Pre-experiment covariate values
- Good correlation between metric and covariate (r > 0.3 recommended)

**Example:**
```yaml
config:
  test_type: "cuped_ttest"
  metric_column: "revenue"
  group_column: "experiment_group"
  covariate_column: "pre_experiment_revenue"  # Required for CUPED
  alpha: 0.05
  test_direction: "relative"
```

### 4. Bootstrap Test (`bootstrap`)

Non-parametric test that makes no assumptions about data distribution. More robust but computationally intensive.

**Use cases:**
- When data doesn't meet parametric assumptions
- Highly skewed distributions
- When you want robust, assumption-free results
- Small sample sizes

**Data requirements:**
- Any numeric data
- No distribution assumptions

**Example:**
```yaml
config:
  test_type: "bootstrap"
  metric_column: "metric_value"
  group_column: "experiment_group"
  alpha: 0.05
  test_direction: "relative"
  n_samples: 1000                 # Number of bootstrap samples
  stratify: false                 # Whether to use stratified sampling
  random_seed: 42                 # For reproducible results
```

## Configuration Options

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `test_type` | Statistical test to use | `"ttest"`, `"ztest"`, `"cuped_ttest"`, `"bootstrap"` |
| `metric_column` | Column containing the metric to test | `"revenue"`, `"converted"` |
| `group_column` | Column containing group assignments | `"experiment_group"` |

**Note**: `control_group` and `treatment_group` are no longer required. The processor automatically detects all groups and compares each against every other.

### Optional Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `alpha` | `0.05` | Significance level (Type I error rate) |
| `test_direction` | `"relative"` | `"relative"` for % change, `"absolute"` for raw difference |
| `calculate_mde` | `true` | Whether to calculate Minimum Detectable Effect |
| `power` | `0.8` | Statistical power for MDE calculation |

### CUPED-Specific Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `covariate_column` | Yes | Column containing pre-experiment covariate data |

### Bootstrap-Specific Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_samples` | `1000` | Number of bootstrap resamples |
| `stratify` | `false` | Use stratified sampling by categories |
| `random_seed` | `None` | Seed for reproducible results |

## Data Preparation

### Required Data Format

Your data must include:

1. **Group column**: Identifies which experimental group each observation belongs to
2. **Metric column**: Contains the values to be tested
3. **Date column**: For microbatch processing (optional but recommended)

### Example Data Formats

**For T-test/Bootstrap (continuous metrics):**
```csv
user_id,experiment_group,revenue,event_date
1,control,25.50,2024-01-01
2,treatment,28.20,2024-01-01
3,variant_a,30.10,2024-01-01
4,variant_b,26.80,2024-01-01
5,control,22.30,2024-01-01
```

**For Z-test (binary metrics):**
```csv
user_id,experiment_group,converted,event_date
1,control,0,2024-01-01
2,treatment,1,2024-01-01
3,variant_a,1,2024-01-01
4,variant_b,0,2024-01-01
5,control,1,2024-01-01
```

**For CUPED (with pre-experiment data):**
```csv
user_id,experiment_group,revenue,pre_revenue,event_date
1,control,25.50,24.20,2024-01-01
2,treatment,28.20,26.80,2024-01-01
3,variant_a,30.10,28.50,2024-01-01
4,variant_b,26.80,25.90,2024-01-01
5,control,22.30,21.50,2024-01-01
```

## Microbatch Integration

A/B tests work seamlessly with microbatch processing for cumulative experiment analysis:

```yaml
variables:
  microbatch:
    event_time_column: "event_date"
    batch_size: "day"
    lookback: 0
    begin: "2024-01-01T00:00:00"

steps:
  - id: "extract_experiment_data"
    type: "source"
    source_type: "postgresql"
    config:
      query: |
        SELECT user_id, experiment_group, revenue, event_date
        FROM experiment_results
        WHERE experiment_name = 'feature_test'
          AND event_date >= '2024-01-01'  -- Fixed experiment start
          AND event_date < '{{ batch_end.strftime('%Y-%m-%d') }}'  -- Cumulative to current batch
```

### Cumulative Analysis Benefits

- **Statistical power increases over time** as sample size grows
- **Track experiment progress** and early stopping decisions
- **Handle late-arriving data** through microbatch lookback
- **Automated daily/hourly updates** of experiment results

## Understanding Results

### Output Columns

Each row represents one pairwise comparison between groups:

| Column | Description |
|--------|-------------|
| `group_1` | Name of first group in comparison |
| `group_2` | Name of second group in comparison |
| `mean_1` | Mean value of metric for group 1 |
| `mean_2` | Mean value of metric for group 2 |
| `std_1` | Standard deviation for group 1 |
| `std_2` | Standard deviation for group 2 |
| `size_1` | Sample size for group 1 |
| `size_2` | Sample size for group 2 |
| `method` | Statistical test method used (t-test, z-test, etc.) |
| `method_params` | JSON string with test parameters |
| `alpha` | Significance level used (e.g., 0.05) |
| `pvalue` | P-value of the statistical test |
| `effect` | Effect size (mean_2 - mean_1 or relative difference) |
| `significant` | Boolean: true if p-value < alpha |
| `ci_length` | Length of confidence interval |
| `ci_lower` | Lower bound of confidence interval |
| `ci_upper` | Upper bound of confidence interval |
| `mde_1` | Minimum Detectable Effect for group 1 |
| `mde_2` | Minimum Detectable Effect for group 2 |
| `covariate_1` | Covariate value for group 1 (0 if not applicable) |
| `covariate_2` | Covariate value for group 2 (0 if not applicable) |
| `test_type` | Type of test conducted (ttest, ztest, bootstrap, cuped_ttest) |
| `metric_column` | Name of the metric column analyzed |
| `group_column` | Name of the group column used |
| `covariate_column` | Name of covariate column (empty if not used) |

**Note**: With N groups, you'll get N*(N-1)/2 comparison rows (e.g., 4 groups = 6 comparisons).

### Interpreting Results

**Statistical Significance:**
- `pvalue < 0.05`: Result is statistically significant
- `significant = true`: Reject null hypothesis of no difference

**Effect Size:**
- **Relative effect**: Percentage change (e.g., 0.15 = 15% increase)
- **Absolute effect**: Raw difference in metric units

**Confidence Interval:**
- Range of plausible effect sizes
- If interval excludes 0, result is significant
- Narrower intervals indicate more precise estimates

### Example Results Interpretation

```csv
control_group,treatment_group,control_mean,treatment_mean,effect,pvalue,significant,ci_lower,ci_upper,method
control,treatment,100.0,115.0,0.15,0.023,true,0.025,0.275,t-test
control,variant_a,100.0,125.0,0.25,0.001,true,0.120,0.380,t-test
treatment,variant_a,115.0,125.0,0.087,0.145,false,-0.032,0.206,t-test
```

**Interpretation:** 
- **Control vs Treatment**: 15% increase, statistically significant (p=0.023)
- **Control vs Variant A**: 25% increase, highly significant (p=0.001) 
- **Treatment vs Variant A**: 8.7% increase, not significant (p=0.145)

Variant A performs best, significantly better than control. Treatment vs Variant A difference is not conclusive.

## Best Practices

### 1. Choose the Right Test

- **T-test**: Normal-ish continuous data, good for most revenue/time metrics
- **Z-test**: Binary outcomes only (conversion, click rates)
- **CUPED**: When you have good pre-experiment data (correlation > 0.3)
- **Bootstrap**: Non-normal data, small samples, or when in doubt

### 2. Sample Size Planning

```yaml
# Calculate required sample size before experiment
config:
  calculate_mde: true  # Shows minimum detectable effect
  power: 0.8          # 80% power is standard
  alpha: 0.05         # 5% significance level
```

### 3. Multiple Testing

When testing multiple metrics, consider:
- Bonferroni correction: Divide alpha by number of tests
- Focus on primary metric for decision-making
- Use secondary metrics for insights, not decisions

### 4. Data Quality

- **Remove outliers** that could skew results
- **Check for imbalanced randomization** (group sizes should be similar)
- **Validate data pipeline** before running tests
- **Handle missing values** appropriately

### 5. Experiment Duration

- **Plan minimum duration** based on business cycles (weekdays vs weekends)
- **Don't peek too early** - statistical significance will fluctuate
- **Consider practical significance** alongside statistical significance

## Advanced Use Cases

### Multi-Armed Tests

For comparing multiple treatment variants:

```yaml
# Run separate tests for each treatment vs control
- id: "test_treatment_a_vs_control"
  config:
    control_group: "control"
    treatment_group: "treatment_a"

- id: "test_treatment_b_vs_control"  
  config:
    control_group: "control"
    treatment_group: "treatment_b"
```

### Segmented Analysis

Test effects within specific user segments:

```yaml
# Filter data for specific segment before testing
- id: "extract_mobile_users"
  type: "source"
  config:
    query: |
      SELECT * FROM experiment_data 
      WHERE platform = 'mobile'
      AND event_date >= '2024-01-01'
```

### Time-Based Analysis

Track how effects change over time:

```yaml
variables:
  microbatch:
    batch_size: "day"  # Daily results show effect evolution
```

## Troubleshooting

### Common Issues

**"Sample has zero variance"**
- All users in a group have identical metric values
- Check data pipeline for bugs
- Consider if metric is appropriate for testing

**"Cannot calculate relative effect when control mean is zero"**
- Control group average is zero
- Use `test_direction: "absolute"` instead
- Check if metric definition is correct

**"Low correlation between metric and covariate"**
- CUPED warning when correlation < 0.1
- Consider different covariate or use regular t-test
- Pre-experiment data may not be predictive

**"Does not meet normal approximation requirements"**
- Z-test warning when sample size too small
- Need at least 5 expected successes and failures per group
- Increase sample size or use bootstrap test

### Performance Tips

- **Use appropriate batch sizes** for microbatch processing
- **Filter data** before testing to reduce processing time
- **Set reasonable bootstrap samples** (1000 is usually sufficient)
- **Consider stratification** for bootstrap when groups are unbalanced

## Examples

See the `examples/ab_testing/` directory for complete working examples of all test types with sample data and pipeline configurations.

## API Reference

For programmatic usage, the A/B testing processor can be imported and used directly:

```python
from dft.processors.ab_testing import ABTestProcessor
from dft.processors.ab_testing.models import ABTestConfig

# Create processor
processor = ABTestProcessor()

# Configure test
config = ABTestConfig(
    test_type="ttest",
    metric_column="revenue",
    group_column="experiment_group",
    control_group="control",
    treatment_group="treatment"
)

# Run test
results = processor.process(data, **config.__dict__)
```