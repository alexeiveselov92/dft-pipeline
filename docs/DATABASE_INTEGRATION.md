# 🗄️ DFT Database Integration Guide

## ✅ New Features

### 🔗 Data Sources
- **PostgreSQL** - full support with automatic schema detection
- **ClickHouse** - optimized for analytics, column types support
- **MySQL** - full compatibility with charset settings
- **Google Play Console** - financial and installs data extraction
- **Custom Sources** - plugin system for adding your own data sources

### 📊 Data Endpoints  
- **PostgreSQL/ClickHouse/MySQL** - automatic table creation from data
- **Load modes**: append, replace, upsert
- **Smart type detection** from Arrow schema
- **Custom schema** via configuration
- **Custom Endpoints** - plugin system for adding your own data destinations

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

## 🔌 Custom Database Components

DFT's plugin system allows you to add custom database sources and endpoints directly to your project.

### Custom Database Source Example

```python
# dft/sources/snowflake_source.py
from typing import Any, Dict, Optional
from dft.core.base import DataSource
from dft.core.data_packet import DataPacket
import pandas as pd

class SnowflakeSource(DataSource):
    """Custom Snowflake data source"""
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        # Get connection details from config
        account = self.get_config('account')
        user = self.get_config('user') 
        password = self.get_config('password')
        warehouse = self.get_config('warehouse')
        database = self.get_config('database')
        schema = self.get_config('schema', 'PUBLIC')
        query = self.get_config('query')
        
        # Connect to Snowflake
        import snowflake.connector
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        
        # Execute query
        df = pd.read_sql(query, conn)
        conn.close()
        
        return DataPacket(
            data=df,
            metadata={
                'source': 'snowflake',
                'row_count': len(df),
                'query': query
            }
        )
    
    def test_connection(self) -> bool:
        try:
            # Test connection logic
            return True
        except Exception:
            return False
```

### Custom Database Endpoint Example

```python  
# dft/endpoints/bigquery_endpoint.py
from typing import Any, Dict, Optional
from dft.core.base import DataEndpoint
from dft.core.data_packet import DataPacket

class BigQueryEndpoint(DataEndpoint):
    """Custom BigQuery data endpoint"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        df = packet.data
        project_id = self.get_config('project_id')
        dataset_id = self.get_config('dataset_id')
        table_id = self.get_config('table_id')
        mode = self.get_config('mode', 'append')  # append/replace
        
        from google.cloud import bigquery
        import pandas_gbq
        
        # Upload to BigQuery
        destination_table = f"{project_id}.{dataset_id}.{table_id}"
        
        if_exists = 'append' if mode == 'append' else 'replace'
        
        pandas_gbq.to_gbq(
            df, 
            destination_table, 
            project_id=project_id,
            if_exists=if_exists
        )
        
        print(f"Loaded {len(df)} rows to {destination_table}")
        return True
```

### Using Custom Database Components

```yaml
# pipelines/snowflake_to_bigquery.yml
pipeline_name: snowflake_to_bigquery
description: Move data from Snowflake to BigQuery

steps:
  - id: extract_from_snowflake
    type: source
    source_type: snowflake  # Uses SnowflakeSource class
    config:
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      warehouse: "ANALYTICS_WH"
      database: "PROD_DB"
      schema: "ANALYTICS"
      query: |
        SELECT 
          customer_id,
          order_date,
          total_amount,
          status
        FROM orders 
        WHERE order_date >= CURRENT_DATE - 7
        
  - id: validate_data
    type: processor
    processor_type: validator
    depends_on: [extract_from_snowflake]
    config:
      required_columns: [customer_id, order_date, total_amount]
      row_count_min: 1
      
  - id: load_to_bigquery
    type: endpoint
    endpoint_type: big_query  # Uses BigQueryEndpoint class
    depends_on: [validate_data]
    config:
      project_id: "{{ env_var('GCP_PROJECT_ID') }}"
      dataset_id: "analytics"
      table_id: "recent_orders"
      mode: "replace"
```

### Plugin Features for Databases

- **Auto-Discovery**: Database components are automatically loaded from `dft/sources/` and `dft/endpoints/`
- **Connection Reuse**: Use project-level connection configurations
- **Error Handling**: Built-in connection testing and error management
- **Type Safety**: Leverage pandas and Arrow for consistent data types
- **Performance**: Optimize for specific database characteristics
- **Security**: Environment variable support for credentials

### Environment Variables for Custom Components

```bash
# .env
# Snowflake
SNOWFLAKE_ACCOUNT=abc12345.snowflakecomputing.com
SNOWFLAKE_USER=analyst
SNOWFLAKE_PASSWORD=secure_password

# BigQuery  
GCP_PROJECT_ID=my-analytics-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Other databases
MONGODB_CONNECTION_STRING=mongodb://user:pass@host:port/db
REDIS_URL=redis://localhost:6379/0
```