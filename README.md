# DFT - Data Flow Tools

[![PyPI version](https://badge.fury.io/py/dft-pipeline.svg)](https://badge.fury.io/py/dft-pipeline)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Flexible ETL pipeline framework designed for data analysts and engineers. Build, orchestrate, and monitor data pipelines with YAML configurations.

## ✨ Key Features

- **🔧 Component-Based**: Modular sources, processors, and endpoints
- **🔌 Plugin System**: Add custom components directly to your project
- **📋 YAML Configuration**: Simple, readable pipeline definitions
- **🔗 Dependency Management**: Automatic pipeline ordering and validation
- **📊 Interactive Documentation**: Web-based pipeline exploration with component library
- **💾 Database Support**: PostgreSQL, MySQL, ClickHouse with upsert capabilities
- **🔄 Incremental Processing**: Smart data loading with state management
- **⚙️ Data Validation**: Built-in quality checks and constraints
- **🎯 Analyst-Friendly**: Rich CLI tools and component discovery

## 🚀 Quick Start

### 1. Installation

#### Option A: Install from PyPI (Recommended)

```bash
# Install directly from PyPI
pip install dft-pipeline
```

#### Option B: Install from Source (For Development)

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
# Initialize a new project with examples
dft init my_analytics_project
cd my_analytics_project

# View interactive documentation
dft docs --serve
# Opens at http://localhost:8080

# Discover available components
dft components list

# Run a simple pipeline (uses sample data)
dft run --select simple_csv_example

# Try the custom components example  
dft run --select custom_example_pipeline
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
pipeline_name: simple_etl
description: Extract, validate, and load user data

connections:
  analytics_db:
    type: postgresql
    host: analytics.company.com
    database: warehouse
    user: analyst
    password: "${POSTGRES_PASSWORD}"

steps:
  - id: load_user_data
    type: source
    source_type: csv
    config:
      file_path: "data/users.csv"

  - id: validate_users
    type: processor
    processor_type: validator
    depends_on: [load_user_data]
    config:
      required_columns: [id, email, created_at]
      row_count_min: 1

  - id: save_clean_users
    type: endpoint
    endpoint_type: postgresql
    connection: analytics_db
    depends_on: [validate_users]
    config:
      table: users_clean
      mode: replace
```

### Advanced Pipeline with Dependencies

```yaml
pipeline_name: customer_analytics
tags: [analytics, daily]
depends_on: [data_ingestion]  # Run after data_ingestion pipeline

variables:
  analysis_date: "{{ yesterday() }}"
  min_transaction_amount: 10.00

connections:
  transaction_db:
    type: postgresql
    host: transactions.company.com
    database: sales
    user: analyst
    password: "${POSTGRES_PASSWORD}"
    
  warehouse_db:
    type: postgresql
    host: warehouse.company.com
    database: analytics
    user: writer
    password: "${WAREHOUSE_PASSWORD}"

steps:
  - id: extract_transaction_data
    type: source
    source_type: postgresql
    connection: transaction_db
    config:
      query: |
        SELECT * FROM transactions 
        WHERE date = '{{ var("analysis_date") }}'

  - id: validate_metrics
    type: processor
    processor_type: validator
    depends_on: [extract_transaction_data]
    config:
      checks:
        - column: amount
          min_value: "{{ var('min_transaction_amount') }}"
          not_null: true

  - id: save_to_warehouse
    type: endpoint
    endpoint_type: postgresql
    connection: warehouse_db
    depends_on: [validate_metrics]
    config:
      table: metrics_warehouse
      mode: append
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

### Custom Components Plugin System

DFT supports adding custom components directly to your project, similar to dbt macros. When you run `dft init`, a complete plugin structure is created:

```
my_project/
├── dft/                    # Custom components directory
│   ├── sources/           # Custom data sources
│   ├── processors/        # Custom data processors  
│   └── endpoints/         # Custom data endpoints
└── pipelines/
    └── custom_example_pipeline.yml  # Example using custom components
```

#### Creating Custom Components

**1. Custom Source Example:**

```python
# dft/sources/api_source.py
from typing import Any, Dict, Optional
from dft.core.base import DataSource
from dft.core.data_packet import DataPacket

class ApiSource(DataSource):
    """Custom API data source"""
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        api_url = self.get_config('api_url')
        # Your API extraction logic
        return DataPacket(data=data, metadata={})
    
    def test_connection(self) -> bool:
        return True
```

**2. Custom Processor Example:**

```python
# dft/processors/data_cleaner.py
from dft.core.base import DataProcessor

class DataCleaner(DataProcessor):
    """Custom data cleaning processor"""
    
    def process(self, packet, variables=None):
        # Your cleaning logic
        cleaned_data = self.clean_data(packet.data)
        return DataPacket(data=cleaned_data, metadata=packet.metadata)
```

**3. Custom Endpoint Example:**

```python  
# dft/endpoints/webhook.py
from dft.core.base import DataEndpoint

class WebhookEndpoint(DataEndpoint):
    """Custom webhook endpoint"""
    
    def load(self, packet, variables=None) -> bool:
        webhook_url = self.get_config('webhook_url')
        # Your webhook logic
        return True
```

#### Using Custom Components

Components are automatically discovered and can be used by their snake_case name:

```yaml
# pipelines/my_pipeline.yml
steps:
  - id: fetch_data
    type: source
    source_type: api  # Uses ApiSource class
    config:
      api_url: "https://api.example.com/data"
  
  - id: clean_data  
    type: processor
    processor_type: data_cleaner  # Uses DataCleaner class
    depends_on: [fetch_data]
    
  - id: send_webhook
    type: endpoint  
    endpoint_type: webhook  # Uses WebhookEndpoint class
    depends_on: [clean_data]
    config:
      webhook_url: "https://hooks.slack.com/..."
```

#### Plugin Features

- **Auto-Discovery**: Components are automatically loaded from `dft/` directories
- **Snake Case Naming**: `MyCustomSource` → `my_custom` in pipelines
- **No Registration**: Just add `.py` files and they become available
- **Examples Included**: Working examples created with every `dft init`
- **Flexible**: Supports both pandas and plain Python data structures

## 📁 Project Structure

```
my_project/
├── dft_project.yml          # Project configuration
├── .env                     # Environment variables
├── pipelines/               # Pipeline definitions
│   ├── ingestion.yml
│   ├── analytics.yml
│   ├── reporting.yml
│   └── custom_example_pipeline.yml  # Example with custom components
├── dft/                     # Custom components (auto-created)
│   ├── sources/            # Custom data sources
│   │   ├── __init__.py
│   │   └── my_custom_source.py     # Example custom source
│   ├── processors/         # Custom data processors
│   │   ├── __init__.py
│   │   └── my_custom_processor.py  # Example custom processor
│   └── endpoints/          # Custom data endpoints
│       ├── __init__.py
│       └── my_custom_endpoint.py   # Example custom endpoint
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

**Get started in 30 seconds**: 
```bash
pip install dft-pipeline
dft init my_project && cd my_project
dft docs --serve  # Interactive documentation
```

**Try the plugin system**: `dft run --select custom_example_pipeline`