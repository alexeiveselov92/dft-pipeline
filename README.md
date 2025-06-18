# DFT - Data Flow Tools

Flexible ETL pipeline framework designed for data analysts and engineers. Build, orchestrate, and monitor data pipelines with YAML configurations.

## ✨ Key Features

- **🔧 Component-Based**: Modular sources, processors, and endpoints
- **📋 YAML Configuration**: Simple, readable pipeline definitions
- **🔗 Dependency Management**: Automatic pipeline ordering and validation
- **📊 Interactive Documentation**: Web-based pipeline exploration with component library
- **💾 Database Support**: PostgreSQL, MySQL, ClickHouse with upsert capabilities
- **🔄 Incremental Processing**: Smart data loading with state management
- **⚙️ Data Validation**: Built-in quality checks and constraints
- **🎯 Analyst-Friendly**: Rich CLI tools and component discovery

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd dft

# Install package with dependencies
pip install -e .
```

### 2. Create Project

```bash
# Initialize new project
dft init my_analytics_project
cd my_analytics_project
```

### 3. Explore Examples

```bash
# Try the example project
cd example_project

# View interactive documentation
dft docs --serve
# Opens at http://localhost:8080

# Discover available components
dft components list

# Run a simple pipeline
dft run --select simple_csv_example
```

## 📦 Component Library

DFT provides a rich library of pre-built components:

### 📥 Sources
- **CSV**: Read data from CSV files with configurable delimiters and encoding
- **PostgreSQL**: Extract data with SQL queries and named connections
- **MySQL**: Database source with connection pooling
- **ClickHouse**: High-performance analytics database source
- **Google Play**: Specialized financial data extraction

### ⚙️ Processors
- **Validator**: Data quality checks with custom rules and constraints
- **MAD Anomaly Detector**: Statistical anomaly detection for data monitoring

### 📤 Endpoints
- **CSV**: Write processed data to CSV files
- **PostgreSQL**: Load data with append/replace/upsert modes
- **MySQL**: Advanced upsert operations with conflict resolution
- **ClickHouse**: Optimized bulk loading for analytics workloads
- **JSON**: Export data in JSON format

## 🔧 Component Discovery

### CLI Commands

```bash
# List all components
dft components list

# Filter by type
dft components list --type endpoint

# Get detailed information
dft components describe mysql

# View configuration examples
dft components describe validator --format yaml
```

### Web Interface

Access the interactive component library at `dft docs --serve`:
- Browse components by category
- View configuration requirements
- Copy-paste ready YAML examples
- Interactive component details

## 💾 Database Features

### Named Connections

Define reusable database connections:

```yaml
# dft_project.yml
connections:
  analytics_db:
    type: postgresql
    host: analytics.company.com
    database: warehouse
    user: analyst
    password: "${POSTGRES_PASSWORD}"
  
  main_mysql:
    type: mysql
    host: mysql.company.com
    database: production
    user: readonly
    password: "${MYSQL_PASSWORD}"
```

### Upsert Operations

Intelligent insert-or-update operations:

```yaml
# MySQL upsert example
- id: upsert_users
  type: endpoint
  endpoint_type: mysql
  connection: main_mysql
  config:
    table: users
    mode: upsert
    upsert_keys: [id]  # Conflict resolution on 'id' column
    auto_create: true
    schema:
      id: "INT PRIMARY KEY"
      name: "VARCHAR(100)"
      email: "VARCHAR(100)"
      updated_at: "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
```

## 📋 Pipeline Configuration

### Basic Pipeline

```yaml
name: simple_etl
description: Extract, validate, and load user data

sources:
  - name: user_data
    type: csv
    config:
      file_path: "data/users.csv"

endpoints:
  - name: clean_users
    type: postgresql
    connection: analytics_db
    config:
      table: users_clean
      mode: replace

pipelines:
  - name: process_users
    source: user_data
    processors:
      - type: validator
        config:
          required_columns: [id, email, created_at]
          row_count_min: 1
    endpoints: [clean_users]
```

### Advanced Pipeline with Dependencies

```yaml
name: customer_analytics
tags: [analytics, daily]
depends_on: [data_ingestion]  # Run after data_ingestion pipeline

variables:
  analysis_date: "{{ yesterday() }}"
  min_transaction_amount: 10.00

pipelines:
  - name: customer_metrics
    source: transaction_data
    processors:
      - type: validator
        config:
          checks:
            - column: amount
              min_value: "{{ var('min_transaction_amount') }}"
              not_null: true
    endpoints: [metrics_warehouse]
```

## 🔄 Pipeline Execution

### Basic Execution

```bash
# Run all pipelines
dft run

# Run specific pipeline
dft run --select customer_analytics

# Run by tags
dft run --select tag:daily
```

### Dependency-Aware Execution

```bash
# Run pipeline and all dependencies
dft run --select +customer_analytics

# Run pipeline and all dependents
dft run --select customer_analytics+

# Run full dependency tree
dft run --select +customer_analytics+
```

### Pipeline Variables

```bash
# Override pipeline variables
dft run --select customer_analytics --vars analysis_date=2024-01-15,min_amount=5.00
```

## 📊 Documentation & Monitoring

### Interactive Documentation

Generate comprehensive project documentation:

```bash
dft docs --serve
```

Features:
- **Pipeline Overview**: Visual dependency graphs with filtering
- **Component Library**: Interactive component browser with examples
- **Configuration Details**: Collapsible component configurations
- **YAML Examples**: Copy-paste ready configurations

### Pipeline Validation

```bash
# Validate all pipeline configurations
dft validate

# Validate specific pipelines
dft validate --select customer_analytics

# Check dependencies
dft deps
```

## 🎯 For Data Analysts

DFT is designed with analysts in mind:

### 1. **Discover Components**
```bash
dft components list --type source
dft components describe postgresql
```

### 2. **Build Pipelines**
- Copy YAML examples from documentation
- Use named connections for database access
- Apply data validation rules

### 3. **Monitor & Debug**
- Interactive web documentation
- Pipeline dependency visualization
- Built-in configuration validation

### 4. **Scale Operations**
- Incremental data processing
- Dependency-aware execution
- Environment-specific configurations

## 🔍 Advanced Features

### Environment Configuration

```bash
# Development environment
export DFT_ENV=dev
dft run --select customer_analytics

# Production environment  
export DFT_ENV=prod
dft run --select customer_analytics
```

### State Management

DFT automatically tracks pipeline execution state for incremental processing:

```yaml
variables:
  # Start from last processed date or 7 days ago
  start_date: "{{ state.get('last_processed_date', days_ago(7)) }}"
  end_date: "{{ yesterday() }}"
```

### Custom Processors

Extend DFT with custom processing logic:

```python
from dft.core.base import DataProcessor

class CustomTransformer(DataProcessor):
    """Custom data transformation processor"""
    
    def process(self, packet, variables=None):
        # Your custom logic here
        return transformed_packet
```

## 📁 Project Structure

```
my_project/
├── dft_project.yml          # Project configuration
├── .env                     # Environment variables
├── pipelines/               # Pipeline definitions
│   ├── ingestion.yml
│   ├── analytics.yml
│   └── reporting.yml
├── data/                    # Input data files
├── output/                  # Generated outputs
└── .dft/                    # DFT metadata
    ├── docs/                # Generated documentation
    ├── state/               # Pipeline state files
    └── logs/                # Execution logs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Get started with the example project**: `cd example_project && dft docs --serve`