# DFT Example Project

This example project demonstrates DFT (Data Flow Tools) capabilities with sample pipelines and configurations.

## 📁 Project Structure

```
example_project/
├── dft_project.yml          # Project configuration and database connections
├── data/                    # Sample data files
│   └── sample_data.csv
├── pipelines/               # Pipeline YAML definitions
│   ├── analytics_pipeline.yml
│   ├── base_data_pipeline.yml
│   ├── customer_analysis.yml
│   ├── daily_transactions.yml
│   ├── independent_pipeline.yml
│   ├── reporting_pipeline.yml
│   └── simple_csv_example.yml
└── output/                  # Output files (auto-generated)
```

## 🚀 Quick Start

### 1. Install DFT

```bash
# From the main DFT directory
cd ..
pip install -e .
cd example_project
```

### 2. Run a Simple Example

```bash
# Run a basic CSV processing pipeline
dft run --select simple_csv_example
```

### 3. View Documentation

```bash
# Generate and serve interactive documentation
dft docs --serve
# Opens at http://localhost:8080
```

### 4. Explore Components

```bash
# List all available components
dft components list

# Get details about a specific component
dft components describe mysql

# View YAML examples
dft components describe validator --format yaml
```

## 🔧 Example Pipelines

### simple_csv_example.yml
Basic CSV processing pipeline for testing without database dependencies.

### analytics_pipeline.yml
Demonstrates pipeline dependencies (depends on `base_data_pipeline`).

### customer_analysis.yml
Shows complex data processing with multiple sources and validation steps.

### daily_transactions.yml
Example of daily batch processing with data validation.

## 💾 Database Examples

The project includes examples for:
- **PostgreSQL** sources and endpoints with named connections
- **ClickHouse** endpoints with advanced configurations
- **MySQL** endpoints with upsert functionality
- **CSV** file processing

## 🔍 Pipeline Features Demonstrated

- **Dependencies**: Pipeline execution order based on `depends_on`
- **Tags**: Grouping pipelines by purpose (`analytics`, `daily`, etc.)
- **Variables**: Template variables for flexible configurations
- **Validation**: Data quality checks with custom rules
- **Named Connections**: Reusable database connection definitions
- **Upsert Operations**: Insert or update operations for incremental loads

## 📊 Documentation & Monitoring

### Interactive Documentation
- View all pipelines with dependencies
- Explore available components with configuration examples
- Interactive dependency graphs

### CLI Tools
```bash
dft validate          # Validate pipeline configurations
dft deps              # Show pipeline dependencies
dft components list   # List available components
```

## 🎯 For Analysts

This example project shows how analysts can:

1. **Discover Components**: Use `dft components` to find sources, processors, and endpoints
2. **Copy Configurations**: Get ready-to-use YAML examples from documentation
3. **Build Pipelines**: Combine components with clear configuration patterns
4. **Validate Work**: Use built-in validation to catch configuration errors
5. **Monitor Dependencies**: Understand pipeline relationships and execution order

## 🔗 Next Steps

- Explore the interactive documentation at `dft docs --serve`
- Try modifying pipeline configurations
- Add your own database connections in `dft_project.yml`
- Create new pipelines using the component examples