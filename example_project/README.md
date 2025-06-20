# DFT Example Project

This example project demonstrates DFT (Data Flow Tools) capabilities with sample pipelines and configurations.

## 📁 Project Structure

```
example_project/
├── dft_project.yml          # Project configuration and database connections
├── data/                    # Sample data files
│   └── sample_data.csv
├── dft/                     # Custom components (plugin system)
│   ├── sources/            # Custom data sources
│   │   └── my_custom_source.py     # Example custom source
│   ├── processors/         # Custom data processors
│   │   └── my_custom_processor.py  # Example custom processor
│   └── endpoints/          # Custom data endpoints
│       └── my_custom_endpoint.py   # Example custom endpoint
├── pipelines/               # Pipeline YAML definitions
│   ├── analytics_pipeline.yml
│   ├── base_data_pipeline.yml
│   ├── custom_example_pipeline.yml # Uses custom components
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
# Install from PyPI
pip install dft-pipeline

# Or from source (development)
# cd .. && pip install -e . && cd example_project
```

### 2. Run a Simple Example

```bash
# Run a basic CSV processing pipeline
dft run --select simple_csv_example

# Try the custom components example
dft run --select custom_example_pipeline
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

### custom_example_pipeline.yml
**NEW**: Demonstrates the plugin system with custom sources, processors, and endpoints.

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
- **Custom Components** - plugin system for extending DFT with your own sources, processors, and endpoints

## 🔍 Pipeline Features Demonstrated

- **Dependencies**: Pipeline execution order based on `depends_on`
- **Tags**: Grouping pipelines by purpose (`analytics`, `daily`, etc.)
- **Variables**: Template variables for flexible configurations
- **Validation**: Data quality checks with custom rules
- **Named Connections**: Reusable database connection definitions
- **Upsert Operations**: Insert or update operations for incremental loads
- **Plugin System**: Custom components that are automatically discovered and available in pipelines

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
4. **Create Custom Components**: Add your own sources/processors/endpoints to the `dft/` directory
5. **Validate Work**: Use built-in validation to catch configuration errors
6. **Monitor Dependencies**: Understand pipeline relationships and execution order

## 🔗 Next Steps

- Explore the interactive documentation at `dft docs --serve`
- Try the custom components example: `dft run --select custom_example_pipeline`
- Create your own custom components in the `dft/sources/`, `dft/processors/`, or `dft/endpoints/` directories
- Try modifying pipeline configurations
- Add your own database connections in `dft_project.yml`
- Create new pipelines using the component examples