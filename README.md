# DFT - Data Flow Tools

ETL pipeline framework for data analysts and engineers.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd dft

# Install package (dependencies will be installed automatically)
pip install .
```

### 2. Create Project

```bash
# Create new project
dft init my_analytics_project
cd my_analytics_project
```

### 3. Configure Connections

Create `dft_project.yml` file:

```yaml
# dft_project.yml
project_name: my_analytics

# State management configuration
state:
  ignore_in_git: true  # Recommended for development

# Database and service connections (can be used as sources and endpoints)
connections:
  my_postgres:
    type: postgresql
    host: "{{ env_var('POSTGRES_HOST') }}"
    port: 5432
    database: "{{ env_var('POSTGRES_DB') }}"
    user: "{{ env_var('POSTGRES_USER') }}"
    password: "{{ env_var('POSTGRES_PASSWORD') }}"
    
  my_clickhouse:
    type: clickhouse
    host: "{{ env_var('CH_HOST') }}"
    port: 9000
    database: "{{ env_var('CH_DATABASE') }}"
    user: "{{ env_var('CH_USER') }}"
    password: "{{ env_var('CH_PASSWORD') }}"

variables:
  default_start_date: "2024-01-01"
```

Create `.env` file:

```bash
# .env
POSTGRES_HOST=localhost
POSTGRES_DB=analytics
POSTGRES_USER=analyst
POSTGRES_PASSWORD=password123

CH_HOST=clickhouse.company.com  
CH_DATABASE=analytics
CH_USER=default
CH_PASSWORD=
```

### 4. Create Pipeline

Create `pipelines/daily_metrics.yml` file:

```yaml
pipeline_name: daily_metrics
tags: [daily, metrics]

variables:
  start_date: "{{ state.get('last_processed_date', var('default_start_date')) }}"
  end_date: "{{ yesterday() }}"

steps:
  # Extract data from source
  - id: extract_events
    type: source
    source_type: postgresql
    connection: my_postgres
    config:
      query: |
        SELECT 
          user_id,
          event_date,
          event_type,
          revenue
        FROM events 
        WHERE event_date BETWEEN '{{ var("start_date") }}' AND '{{ var("end_date") }}'
  
  # Validate data
  - id: validate_data
    type: processor
    processor_type: validator
    depends_on: [extract_events]
    config:
      required_columns: [user_id, event_date, event_type]
      row_count_min: 1
  
  # Save to ClickHouse
  - id: save_to_warehouse
    type: endpoint
    endpoint_type: clickhouse
    connection: my_clickhouse
    depends_on: [validate_data]
    config:
      table: "daily_events"
      auto_create: true
      mode: "append"
      schema:
        user_id: "String"
        event_date: "Date"
        event_type: "String"
        revenue: "Float64"
        processed_at: "DateTime DEFAULT now()"
      engine: "MergeTree()"
      order_by: "(event_date, user_id)"
```

### 5. Run Pipeline

```bash
# Run specific pipeline
dft run --select daily_metrics

# Run all pipelines with tag
dft run --select tag:daily

# Full refresh (ignore state)
dft run --select daily_metrics --full-refresh

# Run with variables
dft run --select daily_metrics --vars start_date=2024-01-01,end_date=2024-01-31
```

## 📋 Core Commands

```bash
# Project initialization
dft init my_project

# Running pipelines
dft run                           # Run all pipelines in dependency order
dft run --select pipeline_name    # Run specific pipeline
dft run --select tag:daily        # Run pipelines with tag
dft run --exclude tag:slow        # Exclude pipelines with tag

# Dependency selectors (dbt-style)
dft run --select +pipeline_name   # Run upstream dependencies
dft run --select pipeline_name+   # Run downstream dependencies  
dft run --select +pipeline_name+  # Run all related pipelines

# Pipeline validation
dft validate                      # Validate all pipeline configurations
dft validate --select my_pipeline # Validate specific pipeline

# Dependency analysis
dft deps                          # Show all dependencies
dft deps --select my_pipeline     # Dependencies for pipeline

# Documentation and utilities
dft docs                          # Generate documentation
dft docs --serve                  # Start web server with documentation
dft update-gitignore              # Update .gitignore based on project config
```

## 🔌 Supported Components

### Data Sources
- **CSV** - read CSV files
- **JSON** - read JSON files  
- **PostgreSQL** - SQL queries to PostgreSQL
- **ClickHouse** - SQL queries to ClickHouse
- **MySQL** - SQL queries to MySQL
- **Google Play** - data loading from Google Play Console

### Processors  
- **validator** - schema and data quality validation
- **mad_anomaly_detector** - MAD method anomaly detector

### Data Endpoints
- **CSV** - save to CSV files
- **JSON** - save to JSON files
- **PostgreSQL** - load to PostgreSQL tables
- **ClickHouse** - load to ClickHouse tables  
- **MySQL** - load to MySQL tables

## 🔗 Pipeline Dependencies

DFT supports inter-pipeline dependencies similar to dbt. This allows building complex data flows where one pipeline depends on the results of another.

### Defining Dependencies

```yaml
# pipelines/base_data.yml
pipeline_name: base_data
tags: [base, etl]

steps:
  - id: extract_raw_data
    type: source
    source_type: postgresql
    config:
      query: "SELECT * FROM raw_events"
  
  - id: save_base_data
    type: endpoint
    endpoint_type: csv
    depends_on: [extract_raw_data]
    config:
      file_path: "output/base_data.csv"
```

```yaml
# pipelines/analytics.yml
pipeline_name: analytics
tags: [analytics, daily]
depends_on: [base_data]  # Depends on base_data pipeline

steps:
  - id: read_base_data
    type: source
    source_type: csv
    config:
      file_path: "output/base_data.csv"
  
  - id: process_analytics
    type: processor
    processor_type: validator
    depends_on: [read_base_data]
    config:
      required_columns: [user_id, event_date]
```

### Automatic Ordering

When running `dft run`, pipelines are automatically executed in the correct order:

```bash
# Run all pipelines - they will execute in dependency order
dft run

# Result:
# 1. base_data (runs first)
# 2. analytics (runs after base_data)
```

### Dependency Selectors (dbt-style)

Use `+` syntax to select pipelines by dependencies:

```bash
# Run all pipelines that analytics depends on
dft run --select +analytics

# Run all pipelines that depend on base_data
dft run --select base_data+

# Run base_data and all its upstream/downstream dependencies
dft run --select +base_data+
```

### Connection Reuse Example

The same connection can be used as both source and endpoint:

```yaml
# Example: Data transformation within same database
steps:
  # Read from table A
  - id: extract_raw_data
    type: source
    source_type: postgresql
    connection: my_postgres  # Same connection
    config:
      query: "SELECT * FROM raw_table"
  
  # Transform data
  - id: validate_data
    type: processor
    processor_type: validator
    depends_on: [extract_raw_data]
    config:
      required_columns: [id, name]
  
  # Write to table B in same database
  - id: save_processed_data
    type: endpoint
    endpoint_type: postgresql
    connection: my_postgres  # Same connection reused
    depends_on: [validate_data]
    config:
      table: "processed_table"
      auto_create: true
      mode: "append"
      schema:
        id: "INTEGER"
        name: "TEXT"
        processed_at: "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
```

### Dependency Validation

DFT automatically validates dependency correctness on any run:

- ✅ All dependent pipelines exist
- ✅ No circular dependencies
- ✅ If a dependency pipeline fails, dependent pipelines are skipped

```bash
# If there are dependency errors, you get an error even when running another pipeline
dft run --select independent_pipeline
# Error: Pipeline 'analytics' depends on 'nonexistent_pipeline' which does not exist
```

## ⚡ Incremental Processing

DFT automatically tracks pipeline state and supports incremental updates:

```yaml
variables:
  # On first run start_date = days_ago(7)
  # On subsequent runs start_date = last processed date + 1 day
  start_date: "{{ state.get('last_processed_date', days_ago(7)) }}"
  end_date: "{{ yesterday() }}"
```

After successful pipeline execution, DFT automatically updates `last_processed_date`.

## ⚙️ State Management

DFT tracks pipeline execution state to enable incremental processing. State files store information like `last_processed_date` to avoid reprocessing the same data.

### What is State?
State files contain metadata about pipeline execution:
- `last_processed_date` - for incremental data processing
- Execution history and status
- Custom state variables

State is stored in `.dft/state/` directory as JSON files.

### Configuration Options

DFT supports configurable state management for different deployment scenarios:

#### Development Setup (Default)
```yaml
# dft_project.yml
state:
  ignore_in_git: true  # State files ignored in git (recommended for dev)
```

**Use case**: Local development, each developer has their own state
- ✅ No state conflicts between developers
- ✅ Clean git history without state changes
- ❌ State not preserved on fresh git clone

#### Production/GitOps Setup
```yaml
# dft_project.yml  
state:
  ignore_in_git: false  # State files versioned in git (for GitOps)
```

**Use case**: Production deployments, GitOps workflows
- ✅ State preserved across deployments
- ✅ Consistent incremental processing
- ✅ State history tracked in git
- ❌ Potential merge conflicts on state files

### Update Git Configuration
```bash
# After changing state config, update .gitignore
dft update-gitignore
```

### State in Action
```yaml
# Pipeline uses state for incremental processing
variables:
  # First run: processes last 7 days
  # Subsequent runs: processes from last_processed_date
  start_date: "{{ state.get('last_processed_date', days_ago(7)) }}"
  end_date: "{{ yesterday() }}"
```

## 📁 Project Structure

```
my_analytics_project/
├── dft_project.yml              # Project configuration and connections
├── .env                         # Secret variables
├── pipelines/                   # Pipeline YAML files
│   ├── daily_metrics.yml
│   ├── user_analysis.yml
│   └── ab_tests.yml
├── output/                      # Generated output files (ignored in git)
├── .dft/
│   ├── state/                   # Pipeline state (configurable)
│   └── logs/                    # Execution logs
└── docs/                        # Generated documentation
```

## 🔧 Development

```bash
# Install for development
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy dft/

# Code formatting
black dft/
isort dft/
```

## 📖 Additional Documentation

- [PIPELINE_DEPENDENCIES.md](PIPELINE_DEPENDENCIES.md) - Detailed guide on inter-pipeline dependencies
- [DATABASE_INTEGRATION.md](DATABASE_INTEGRATION.md) - Detailed guide on database integration
- [examples/](examples/) - Pipeline examples

## 🆘 Support

When encountering issues:

1. Check logs in `.dft/logs/`
2. Run `dft validate` to verify configuration
3. Ensure all environment variables are set
4. Create an issue in the project repository