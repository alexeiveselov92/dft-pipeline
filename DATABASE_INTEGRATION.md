# 🗄️ DFT Database Integration Guide

## ✅ New Features

### 🔗 Data Sources
- **PostgreSQL** - full support with automatic schema detection
- **ClickHouse** - optimized for analytics, column types support
- **MySQL** - full compatibility with charset settings
- **Google Play Console** - financial and installs data extraction

### 📊 Data Endpoints  
- **PostgreSQL/ClickHouse/MySQL** - automatic table creation from data
- **Load modes**: append, replace, upsert
- **Smart type detection** from Arrow schema
- **Custom schema** via configuration

### ⚡ Incremental Processing
- **State management** - tracking last processed dates
- **Automatic date ranges** - automatic date range determination
- **Execution history** - logging successful/failed executions
- **Simple configuration** - works through variables and state

## 📝 Table Configuration

### Automatic Creation (Recommended)
```yaml
- id: save_to_clickhouse
  type: endpoint
  endpoint_type: clickhouse
  config:
    table: "user_events"
    auto_create: true      # create table automatically
    mode: "append"         # append/replace/upsert
```

### Custom Schema
```yaml
- id: save_with_schema
  type: endpoint
  endpoint_type: clickhouse
  config:
    table: "ab_test_results"
    auto_create: true
    schema:
      experiment_id: "String"
      date: "Date"
      p_value: "Float64"
      effect_size: "Float64"
      created_at: "DateTime DEFAULT now()"
    engine: "MergeTree()"
    order_by: "(experiment_id, date)"
```

### Database-Specific Settings

**ClickHouse:**
```yaml
config:
  table: "events"
  engine: "MergeTree()"           # table engine
  order_by: "(date, user_id)"     # ORDER BY
  partition_by: "toYYYYMM(date)"  # PARTITION BY (optional)
```

**PostgreSQL:**
```yaml
config:
  table: "events"
  schema:
    user_id: "BIGINT NOT NULL"
    event_name: "VARCHAR(255)"
    created_at: "TIMESTAMP DEFAULT NOW()"
```

## 🔄 Incremental Pipeline Processing

### Pipeline Example with Incremental Processing
```yaml
pipeline_name: daily_analytics
variables:
  # Automatic date range determination based on state
  start_date: "{{ state.get('last_processed_date', days_ago(7)) }}"
  end_date: "{{ yesterday() }}"

steps:
  # 1. Get data for period
  - id: get_daily_data
    type: source
    source_type: clickhouse
    connection: clickhouse_prod
    config:
      query: |
        SELECT 
          user_id,
          event_date,
          revenue,
          country
        FROM events 
        WHERE event_date BETWEEN '{{ var("start_date") }}' AND '{{ var("end_date") }}'
        
  # 2. Process data
  - id: process_data
    type: processor
    processor_type: validator
    depends_on: [get_daily_data]
    config:
      required_columns: [user_id, event_date, revenue]
    
  # 3. Save results
  - id: save_results
    type: endpoint
    endpoint_type: clickhouse
    connection: clickhouse_prod
    depends_on: [process_data]
    config:
      table: "daily_analytics"
      auto_create: true
      mode: "append"
      schema:
        user_id: "String"
        event_date: "Date"
        revenue: "Float64"
        country: "String"
        processed_at: "DateTime DEFAULT now()"
      engine: "MergeTree()"
      order_by: "(event_date, user_id)"
```

### Transaction Processing Example with Incremental Processing
```yaml
pipeline_name: transaction_processing
variables:
  start_date: "{{ state.get('last_processed_date', days_ago(7)) }}"
  end_date: "{{ yesterday() }}"

steps:
  - id: extract_transactions
    type: source
    source_type: postgresql
    connection: postgres_prod
    config:
      query: |
        SELECT 
          transaction_id,
          customer_id,
          transaction_date,
          amount,
          status
        FROM transactions 
        WHERE transaction_date BETWEEN '{{ var("start_date") }}' AND '{{ var("end_date") }}'
        AND status = 'completed'
        
  - id: save_processed_data
    type: endpoint
    endpoint_type: clickhouse
    connection: clickhouse_prod
    depends_on: [extract_transactions]
    config:
      table: "processed_transactions"
      auto_create: true
      mode: "append"
      schema:
        transaction_id: "String"
        customer_id: "String"
        transaction_date: "Date"
        amount: "Float64"
        status: "String"
        processed_at: "DateTime DEFAULT now()"
      engine: "MergeTree()"
      order_by: "(transaction_date, customer_id)"
```

### How Incremental Processing Works

1. **State tracking** - system remembers `last_processed_date` for each pipeline
2. **Automatic date ranges** - `start_date`/`end_date` variables are automatically determined
3. **Simple configuration** - just use `state.get()` in variables
4. **State update** - after successful pipeline execution, state is updated
5. **Fallback dates** - if state is empty, fallback is used (e.g., `days_ago(7)`)


## 🔑 Secret Management

### Environment Variables (Recommended)
```yaml
# dft_project.yml
connections:
  clickhouse_prod:
    type: clickhouse
    host: "{{ env_var('CH_HOST') }}"
    user: "{{ env_var('CH_USER') }}"
    password: "{{ env_var('CH_PASSWORD') }}"
    database: "analytics"
```

### .env File
```bash
# .env
CH_HOST=clickhouse.company.com
CH_USER=dft_user
CH_PASSWORD=secure_password
GOOGLE_PLAY_PACKAGE_NAME=com.company.app
GOOGLE_PLAY_SERVICE_ACCOUNT_FILE=/path/to/service-account.json
```

## 📊 Usage Examples

### 1. Daily Data Processing
```bash
dft run --select daily_data_pipeline
```

### 2. Scheduled Data Monitoring
```bash
# Via cron every hour
0 * * * * cd /analytics && dft run --select data_quality_check
```

### 3. Incremental Data Processing
```bash
dft run --select incremental_processing
```

### 4. Processing Specific Period
```bash
dft run --select transaction_processing --vars start_date=2024-01-01,end_date=2024-01-31
```

## 🚀 Performance

### ClickHouse Optimizations
- Use `MergeTree` engine with proper `ORDER BY`
- Date partitioning for large tables
- Batch insert instead of row-by-row

### Incremental Processing
- Process only new data
- Use `state.get('last_processed_date')` 
- Regularly clean up old state files

### Monitoring
- Performance metrics logging
- Track processed data size
- Alerts for execution time thresholds

## ❓ FAQ

**Q: Do I need to describe the table schema completely?**
A: No, DFT automatically determines types from Arrow data. Custom schema is only needed for specific requirements.

**Q: What if the table already exists?**
A: With `auto_create: true`, DFT will check for existence. If the table exists, it will be used without changes.

**Q: How to handle large data volumes?**
A: Use incremental processing, database partitioning, and batch loading modes.

**Q: Do I need a generic "database" source?**
A: No, it's better to use specific sources (postgresql, clickhouse, mysql) for optimal performance with each database.