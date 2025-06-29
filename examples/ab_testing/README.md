# A/B Testing Examples

This directory contains working examples of A/B testing using the DFT framework. These examples use CSV files as data sources, making them easy to run without requiring database connections.

## Available Examples

### 1. T-Test Example (`ab_test_ttest_example.yml`)
- **Purpose**: Test continuous metrics (e.g., revenue, time spent, ratings)
- **Data**: `experiment_data_ttest.csv` with metric values for all experiment groups
- **Use case**: When your metric is a continuous variable and data is approximately normally distributed
- **Groups**: Automatically compares all groups against each other (no need to specify control/treatment)

### 2. Z-Test Example (`ab_test_ztest_example.yml`) 
- **Purpose**: Test binary conversion metrics (e.g., click-through rates, signup rates)
- **Data**: `experiment_data_ztest.csv` with 0/1 conversion values for all experiment groups
- **Use case**: When your metric is a binary outcome (success/failure)
- **Groups**: Automatically compares all groups against each other (no need to specify control/treatment)

### 3. CUPED T-Test Example (`ab_test_cuped_example.yml`)
- **Purpose**: Test continuous metrics with variance reduction using pre-experiment data
- **Data**: `experiment_data_cuped.csv` with both metric and covariate values for all experiment groups
- **Use case**: When you have pre-experiment data correlated with your metric to reduce variance and increase sensitivity
- **Groups**: Automatically compares all groups against each other (no need to specify control/treatment)

### 4. Bootstrap Test Example (`ab_test_bootstrap_example.yml`)
- **Purpose**: Non-parametric testing that doesn't assume data distribution
- **Data**: `experiment_data_ttest.csv` (same as T-test) with values for all experiment groups
- **Use case**: When data doesn't meet parametric test assumptions or you want robust results
- **Groups**: Automatically compares all groups against each other (no need to specify control/treatment)

## Running the Examples

**Note:** The actual working examples are located in `example_project/` directory. This `examples/ab_testing/` contains reference pipeline configurations.

### To run the A/B testing examples:

1. **Navigate to the example project**:
   ```bash
   cd example_project
   ```

2. **Test the A/B testing processor directly**:
   ```bash
   # Test T-test processor (without pandas)
   python3 -c "
   import sys, pyarrow as pa, pyarrow.csv as pv
   sys.path.insert(0, '..')
   from dft.processors.ab_testing import ABTestProcessor
   from dft.core.data_packet import DataPacket
   
   # Load data using PyArrow (no pandas needed)
   data = pv.read_csv('data/experiment_data_ttest.csv')
   config = {'test_type': 'ttest', 'metric_column': 'metric_value', 'group_column': 'experiment_group', 'alpha': 0.05, 'test_direction': 'relative', 'calculate_mde': True, 'power': 0.8}
   processor = ABTestProcessor(config)
   packet = DataPacket(data, {})
   result = processor.process(packet)
   result_df = result.data.to_pandas()
   print(result_df[['control_group', 'treatment_group', 'control_mean', 'treatment_mean', 'effect', 'pvalue', 'significant']])
   "
   ```

3. **Available pipeline files**:
   - `pipelines/ab_test_ttest.yml` - T-test for continuous metrics
   - `pipelines/ab_test_ztest.yml` - Z-test for binary conversion metrics  
   - `pipelines/ab_test_cuped.yml` - CUPED T-test for variance reduction
   - `pipelines/ab_test_bootstrap.yml` - Bootstrap test for robust statistics

4. **Check the results**:
   Results will be saved in `example_project/output/` as CSV files.

## Understanding the Results

Each test outputs a CSV file with the following key columns for each group comparison:

- **control_group/treatment_group**: Names of the two groups being compared
- **control_mean/treatment_mean**: Average metric values for each group in the comparison
- **effect**: The measured effect size (difference between groups)
- **pvalue**: Statistical significance (< 0.05 typically means significant)
- **significant**: Boolean indicating if the result is statistically significant
- **ci_lower/ci_upper**: Confidence interval bounds for the effect
- **method**: Which statistical test was used

**Note**: With multiple groups, you'll get multiple rows - one for each pairwise comparison (e.g., 3 groups = 3 comparisons).

## Example Data Format

### For T-test and Bootstrap (Continuous Metrics):
```csv
user_id,experiment_group,metric_value,event_date
1,control,15.50,2024-01-01
2,treatment,18.20,2024-01-01
3,variant_a,19.50,2024-01-01
4,variant_b,16.80,2024-01-01
```

### For Z-test (Binary Metrics):
```csv
user_id,experiment_group,converted,event_date
1,control,0,2024-01-01
2,treatment,1,2024-01-01
3,variant_a,1,2024-01-01
4,variant_b,0,2024-01-01
```

### For CUPED (With Pre-experiment Data):
```csv
user_id,experiment_group,metric_value,covariate_value,event_date
1,control,15.50,14.20,2024-01-01
2,treatment,18.20,16.80,2024-01-01
3,variant_a,19.50,17.50,2024-01-01
4,variant_b,16.80,15.90,2024-01-01
```

## Microbatch Processing

All examples use microbatch processing with daily windows. This simulates how you would run A/B tests on accumulating experiment data:

- Each day's data is processed cumulatively (from experiment start to current day)
- Results show how statistical significance evolves over time
- This mimics real-world experiment monitoring

## Next Steps

1. **Modify the data**: Edit the CSV files to test with your own data
2. **Adjust parameters**: Change test settings like `alpha`, `power`, or `n_samples` in the pipeline configs
3. **Add more metrics**: Extend the examples to test multiple metrics simultaneously
4. **Database integration**: Replace CSV sources with your actual database connections

For detailed documentation on A/B testing configuration and methodology, see `AB_TESTING.md` in the project root.