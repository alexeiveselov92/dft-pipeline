# Pipeline Dependencies Guide

DFT supports inter-pipeline dependencies similar to dbt, allowing you to build complex data workflows where pipelines depend on each other.

## Table of Contents

- [Basic Concepts](#basic-concepts)
- [Project Structure](#project-structure)
- [Defining Dependencies](#defining-dependencies)
- [Execution Order](#execution-order)
- [Selection Syntax](#selection-syntax)
- [Dependency Validation](#dependency-validation)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Basic Concepts

### Pipeline Dependencies vs Step Dependencies

DFT supports two levels of dependencies:

1. **Step Dependencies** (within a pipeline): Steps depend on other steps in the same pipeline
2. **Pipeline Dependencies** (between pipelines): Pipelines depend on other pipelines

```yaml
# Step dependencies (within pipeline)
steps:
  - id: step_a
    type: source
    # ... config
  
  - id: step_b
    type: processor
    depends_on: [step_a]  # Step dependency
    # ... config

# Pipeline dependencies (between pipelines)
pipeline_name: my_pipeline
depends_on: [other_pipeline]  # Pipeline dependency
```

## Project Structure

When you create a new DFT project with `dft init`, you get a complete structure that supports both built-in and custom components:

```
my_project/
├── dft_project.yml              # Project configuration
├── .env                         # Environment variables
├── pipelines/                   # Pipeline definitions
│   ├── base_data_pipeline.yml   # Base data extraction
│   ├── analytics_pipeline.yml   # Analytics processing
│   ├── reporting_pipeline.yml   # Final reporting
│   └── custom_example_pipeline.yml  # Example using custom components
├── dft/                         # Custom components (plugin system)
│   ├── sources/                # Custom data sources
│   │   ├── __init__.py
│   │   └── my_custom_source.py # Example: API source, Snowflake, etc.
│   ├── processors/             # Custom data processors
│   │   ├── __init__.py
│   │   └── my_custom_processor.py  # Example: ML models, transformations
│   └── endpoints/              # Custom data endpoints
│       ├── __init__.py
│       └── my_custom_endpoint.py   # Example: webhooks, external APIs
├── data/                        # Input data files
├── output/                      # Generated outputs
└── .dft/                        # DFT metadata
    ├── docs/                    # Generated documentation
    ├── state/                   # Pipeline state files
    └── logs/                    # Execution logs
```

### Plugin System Integration

Custom components in the `dft/` directory are automatically discovered and can be used in dependency chains:

```yaml
# pipelines/custom_data_flow.yml
pipeline_name: custom_data_flow
depends_on: [base_data_pipeline]  # Standard dependency

steps:
  - id: fetch_external_data
    type: source
    source_type: my_api  # Custom source from dft/sources/my_api_source.py
    config:
      api_url: "https://api.example.com/data"
      
  - id: custom_processing
    type: processor  
    processor_type: my_transformer  # Custom processor from dft/processors/
    depends_on: [fetch_external_data]
    
  - id: send_to_webhook
    type: endpoint
    endpoint_type: my_webhook  # Custom endpoint from dft/endpoints/
    depends_on: [custom_processing]
    config:
      webhook_url: "https://hooks.slack.com/services/..."

# This pipeline can also be a dependency for other pipelines
```

```yaml
# pipelines/final_report.yml  
pipeline_name: final_report
depends_on: [custom_data_flow, analytics_pipeline]  # Depends on custom pipeline

steps:
  - id: combine_results
    type: processor
    processor_type: validator
    # ... config
```

## Defining Dependencies

### Simple Dependencies

```yaml
# pipelines/base_data.yml
pipeline_name: base_data
tags: [base, etl]

steps:
  - id: extract_data
    type: source
    source_type: postgresql
    config:
      query: "SELECT * FROM raw_events"
```

```yaml
# pipelines/analytics.yml
pipeline_name: analytics
depends_on: [base_data]  # This pipeline depends on base_data
tags: [analytics, daily]

steps:
  - id: process_data
    type: source
    source_type: csv
    config:
      file_path: "output/base_data.csv"
```

### Multiple Dependencies

```yaml
# pipelines/reporting.yml
pipeline_name: reporting
depends_on: [base_data, user_data, product_data]  # Multiple dependencies
tags: [reporting, final]

steps:
  - id: combine_data
    type: source
    source_type: csv
    config:
      file_path: "output/combined_data.csv"
```

### Complex Dependency Chains

```
raw_data_pipeline
├── cleaned_data_pipeline
│   ├── analytics_pipeline
│   └── reporting_pipeline
└── validation_pipeline
```

```yaml
# 1. Raw data (no dependencies)
pipeline_name: raw_data_pipeline

# 2. Cleaned data (depends on raw)
pipeline_name: cleaned_data_pipeline  
depends_on: [raw_data_pipeline]

# 3. Validation (depends on raw)
pipeline_name: validation_pipeline
depends_on: [raw_data_pipeline]

# 4. Analytics (depends on cleaned)
pipeline_name: analytics_pipeline
depends_on: [cleaned_data_pipeline]

# 5. Reporting (depends on analytics)
pipeline_name: reporting_pipeline
depends_on: [analytics_pipeline]
```

## Execution Order

### Automatic Topological Sorting

DFT automatically determines the correct execution order using topological sorting:

```bash
dft run  # Executes in dependency order
```

**Execution order for the above example:**
1. `raw_data_pipeline` (no dependencies)
2. `cleaned_data_pipeline` and `validation_pipeline` (parallel, both depend on raw_data)
3. `analytics_pipeline` (depends on cleaned_data)
4. `reporting_pipeline` (depends on analytics)

### Parallel Execution

Pipelines without interdependencies can run in parallel:

```
Pipeline A (independent) ─── runs in parallel ──── Pipeline C (independent)
Pipeline B (depends on A) ── waits for A ────────── runs after A completes
```

## Selection Syntax

### dbt-style Selectors

DFT uses the same dependency selection syntax as dbt:

| Syntax | Description | Example |
|--------|-------------|---------|
| `pipeline_name` | Run specific pipeline | `dft run --select analytics` |
| `+pipeline_name` | Run upstream dependencies | `dft run --select +analytics` |
| `pipeline_name+` | Run downstream dependencies | `dft run --select base_data+` |
| `+pipeline_name+` | Run all related pipelines | `dft run --select +analytics+` |
| `tag:tagname` | Run pipelines with tag | `dft run --select tag:daily` |

### Examples

```bash
# Run all pipelines (automatic dependency order)
dft run

# Run specific pipeline only
dft run --select analytics_pipeline

# Run analytics and all its dependencies
dft run --select +analytics_pipeline

# Run base_data and everything that depends on it
dft run --select base_data_pipeline+

# Run the entire dependency graph around analytics
dft run --select +analytics_pipeline+

# Run all daily pipelines in dependency order
dft run --select tag:daily

# Exclude slow pipelines but maintain dependencies
dft run --exclude tag:slow
```

### Complex Selections

```bash
# Multiple selectors (union)
dft run --select +analytics_pipeline,+reporting_pipeline

# Tag-based selection with dependencies
dft run --select +tag:critical

# Exclusion with dependencies
dft run --select +reporting_pipeline --exclude tag:expensive
```

## Dependency Validation

### Automatic Validation

DFT validates dependencies before any pipeline execution:

```bash
# Even when running a single pipeline, all dependencies are validated
dft run --select independent_pipeline
# Error: Pipeline 'analytics' depends on 'nonexistent_pipeline' which does not exist
```

### Validation Rules

1. **Existence Check**: All referenced pipelines must exist
2. **Circular Dependency Detection**: No circular dependencies allowed
3. **Consistency Check**: Dependencies are checked across the entire project

### Common Validation Errors

```bash
# Missing dependency
Error: Pipeline 'analytics' depends on 'nonexistent_pipeline' which does not exist

# Circular dependency
Error: Circular dependency detected in pipeline dependency graph involving 'pipeline_a'

# Invalid dependency reference
Error: Pipeline 'my_pipeline' depends on '' which is invalid
```

## Error Handling

### Failed Dependencies

When a pipeline fails, dependent pipelines are automatically skipped:

```
✅ base_data_pipeline (success)
❌ analytics_pipeline (failed)
⏭️ reporting_pipeline (skipped - dependency failed)
✅ independent_pipeline (success - no dependencies)
```

### Error Propagation

```bash
# Example output when dependencies fail
[INFO] Running 3 pipeline(s) in dependency order
[SUCCESS] base_data_pipeline completed
[ERROR] analytics_pipeline failed: Database connection error
[WARNING] Skipping reporting_pipeline due to failed dependencies
[SUCCESS] independent_pipeline completed
```

### Partial Success

DFT continues executing independent pipelines even when some dependency chains fail:

- ✅ Independent pipelines still execute
- ✅ Unaffected dependency chains continue
- ❌ Only dependent pipelines are skipped

## Best Practices

### 1. Logical Grouping

Group related transformations into dependency chains:

```
Raw Data → Cleaned Data → Business Logic → Reporting
```

### 2. Minimize Dependencies

Only create dependencies when data actually flows between pipelines:

```yaml
# Good: Real data dependency
pipeline_name: analytics
depends_on: [raw_data]  # analytics actually uses raw_data output

# Avoid: Artificial ordering
pipeline_name: reporting  
depends_on: [unrelated_pipeline]  # reporting doesn't use unrelated_pipeline data
```

### 3. Use Tags for Logical Grouping

```yaml
# Raw data pipelines
tags: [raw, daily, tier1]

# Analytics pipelines  
tags: [analytics, daily, tier2]

# Reporting pipelines
tags: [reporting, daily, tier3]
```

### 4. Document Dependencies

```yaml
pipeline_name: user_analytics
depends_on: [user_raw_data, event_raw_data]
description: "Combines user and event data for analytics. Requires both raw data pipelines to complete first."
```

### 5. Fail Fast

Structure dependencies so critical failures are detected early:

```
Data Validation → Data Processing → Business Logic → Reporting
     ↑ Fail here rather than later
```

## Examples

### Example 1: Linear Dependency Chain

```yaml
# Stage 1: Raw data extraction
pipeline_name: extract_raw_data
tags: [raw, extract]

# Stage 2: Data cleaning (depends on raw)
pipeline_name: clean_data
depends_on: [extract_raw_data]
tags: [clean, transform]

# Stage 3: Business metrics (depends on clean)
pipeline_name: calculate_metrics
depends_on: [clean_data]
tags: [metrics, business]

# Stage 4: Reporting (depends on metrics)
pipeline_name: generate_reports
depends_on: [calculate_metrics]
tags: [reports, final]
```

### Example 2: Fan-out Pattern

```yaml
# Base data (one input)
pipeline_name: base_events
tags: [base]

# Multiple analytics (fan out from base)
pipeline_name: user_analytics
depends_on: [base_events]
tags: [analytics, users]

pipeline_name: product_analytics
depends_on: [base_events] 
tags: [analytics, products]

pipeline_name: revenue_analytics
depends_on: [base_events]
tags: [analytics, revenue]
```

### Example 3: Fan-in Pattern

```yaml
# Multiple sources
pipeline_name: user_data
tags: [source, users]

pipeline_name: event_data
tags: [source, events]

pipeline_name: product_data
tags: [source, products]

# Combined reporting (fan in)
pipeline_name: comprehensive_report
depends_on: [user_data, event_data, product_data]
tags: [report, comprehensive]
```

### Example 4: Diamond Pattern

```yaml
# Common base
pipeline_name: raw_data
tags: [raw]

# Two processing branches
pipeline_name: process_users
depends_on: [raw_data]
tags: [users]

pipeline_name: process_events  
depends_on: [raw_data]
tags: [events]

# Combine both branches
pipeline_name: user_event_analysis
depends_on: [process_users, process_events]
tags: [analysis, final]
```

## Command Reference

### Basic Commands

```bash
# Show all dependencies
dft deps

# Run with dependencies
dft run --select +my_pipeline

# Validate without running
dft validate
```

### Advanced Usage

```bash
# Complex selection
dft run --select +tag:critical,independent_pipeline --exclude tag:slow

# Debug dependency issues
dft deps --select +problematic_pipeline

# Run specific dependency chains
dft run --select base_data+
```

## Troubleshooting

### Common Issues

1. **Circular Dependencies**: Check for cycles in your dependency graph
2. **Missing Pipelines**: Ensure all referenced pipelines exist
3. **Incorrect Execution Order**: Verify your `depends_on` declarations
4. **Skipped Pipelines**: Check if dependencies failed

### Debug Commands

```bash
# Show dependency graph
dft deps

# Validate configuration
dft validate

# Run with verbose logging
dft run --log-level DEBUG
```

For more examples and advanced patterns, see the [examples/](examples/) directory.