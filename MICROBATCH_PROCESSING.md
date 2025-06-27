# Microbatch Processing Guide

DFT supports microbatch processing for efficient handling of time-series data. This strategy automatically splits your pipeline execution into time-based windows, enabling incremental processing with lookback support for late-arriving data.

## Overview

Microbatch processing transforms your pipeline into a cycle that processes data in time windows:

```
FOR each time window:
  1. Extract data for this window
  2. Process the data
  3. Delete old data for this window
  4. Load new processed data
  5. Move to next window
```

## Configuration

Add microbatch configuration to your pipeline's `variables` section:

```yaml
variables:
  microbatch:
    event_time_column: "created_at"    # Column containing timestamps
    batch_size: "day"                  # Time window size
    lookback: 2                        # Number of previous windows to reprocess
    begin: "2024-01-01T00:00:00"      # Start time (required for first run)
    end: "2024-12-31T23:59:59"        # End time (optional, defaults to now)
```

### Supported Batch Sizes

- `10min` - 10-minute windows
- `hour` - Hourly windows  
- `day` - Daily windows
- `week` - Weekly windows
- `month` - Monthly windows (approximated as 30 days)
- `year` - Yearly windows (approximated as 365 days)

### Lookback Strategy

- **lookback: 0** - Process only new data (no reprocessing)
- **lookback: 1** - Reprocess the previous window (default)
- **lookback: N** - Reprocess the last N windows

Lookback is essential for handling late-arriving data in ETL scenarios.

## Pipeline Variables

During microbatch execution, your pipeline steps automatically receive these variables:

- `batch_start` - Start of current batch window (datetime object)
- `batch_end` - End of current batch window (datetime object)  
- `batch_period` - Batch size (e.g., "day")
- `event_time_column` - Column name for time filtering

## Sources

Sources must filter data using the batch variables:

```yaml
- id: "extract_events"
  type: "source"
  source_type: "postgresql"
  config:
    query: |
      SELECT *
      FROM events
      WHERE created_at >= '{{ batch_start.strftime('%Y-%m-%d %H:%M:%S') }}'
        AND created_at < '{{ batch_end.strftime('%Y-%m-%d %H:%M:%S') }}'
```

### Date Formatting Examples

```yaml
# PostgreSQL/MySQL
WHERE date_col >= '{{ batch_start.strftime('%Y-%m-%d %H:%M:%S') }}'

# For date-only columns
WHERE date_col >= '{{ batch_start.strftime('%Y-%m-%d') }}'::date

# ClickHouse
WHERE date_col >= '{{ batch_start.strftime('%Y-%m-%d %H:%M:%S') }}'

# API calls
url: "https://api.example.com/data?start={{ batch_start.isoformat() }}&end={{ batch_end.isoformat() }}"
```

## Processors

Processors work transparently with microbatch - they receive filtered data for each window and process it normally:

```yaml
- id: "validate_events"
  type: "processor"
  processor_type: "validator"
  config:
    checks:
      - check: "row_count"
        min_rows: 1
      - check: "required_columns"
        columns: ["user_id", "event_type", "created_at"]
```

## Endpoints

Endpoints automatically handle data replacement for microbatch:

```yaml
- id: "load_results"
  type: "endpoint"
  endpoint_type: "postgresql"
  config:
    table: "daily_stats"
    event_time_column: "event_date"  # Required for automatic cleanup
    schema:
      event_date: "DATE"
      event_count: "INTEGER"
```

### How Endpoint Cleanup Works

1. **Before loading new data**: Automatically deletes existing data where `event_time_column` falls within the current batch window
2. **Load new data**: Inserts the processed data for this window
3. **No conflicts**: Each window is completely replaced

## Complete Example

```yaml
name: "daily_analytics"

variables:
  microbatch:
    event_time_column: "created_at"
    batch_size: "day"
    lookback: 1
    begin: "2024-01-01T00:00:00"

steps:
  - id: "extract_events"
    type: "source" 
    source_type: "postgresql"
    config:
      query: |
        SELECT user_id, event_type, created_at
        FROM events
        WHERE created_at >= '{{ batch_start.strftime('%Y-%m-%d %H:%M:%S') }}'
          AND created_at < '{{ batch_end.strftime('%Y-%m-%d %H:%M:%S') }}'
      connection: "events_db"

  - id: "validate_events"
    type: "processor"
    processor_type: "validator"
    depends_on: ["extract_events"]
    config:
      checks:
        - check: "row_count"
          min_rows: 1
        - check: "required_columns"
          columns: ["user_id", "event_type", "created_at"]

  - id: "load_events"
    type: "endpoint"
    endpoint_type: "postgresql"
    depends_on: ["validate_events"]
    config:
      table: "processed_events"
      event_time_column: "created_at"
      connection: "analytics_db"
      schema:
        user_id: "VARCHAR(100)"
        event_type: "VARCHAR(100)"
        created_at: "TIMESTAMP"
```

## Execution Output

Microbatch execution provides clear progress logging:

```
Running pipeline daily_analytics with microbatch strategy
Processing 5 batch windows for pipeline daily_analytics

Running 3 steps for batch day [2024-01-01 00:00 - 2024-01-02 00:00]

 1 of 3 START extract_events.................................. [RUN] OK 1,234 rows, 2.3MB
 2 of 3 START validate_events................................. [RUN] OK 1,234 rows, 2.3MB  
 3 of 3 START load_events..................................... [RUN] OK 1,234 rows

Completed successfully
Successfully processed batch 1/5: day[2024-01-01T00:00:00-2024-01-02T00:00:00]

Running 3 steps for batch day [2024-01-02 00:00 - 2024-01-03 00:00]
...
```

## Error Handling

- If any batch fails, subsequent batches are skipped
- The next run will resume from the failed batch
- Use `dft run --full-refresh` to reset state and start from the beginning

## State Management

Microbatch state is automatically tracked:
- Last processed timestamp is stored in `.dft/state/`
- Each run determines windows to process based on last successful batch
- Lookback configuration ensures late data is handled properly

## Performance Tips

1. **Optimize batch size** for your data volume and processing time
2. **Use appropriate lookback** - higher values process more data but ensure completeness
3. **Index your event_time_column** in source databases for efficient filtering
4. **Consider data retention** in target tables when using large lookback values

## API Sources

For API sources, use the datetime objects directly:

```yaml
- id: "api_extract"
  type: "source"
  source_type: "http"
  config:
    url: "https://api.example.com/events"
    params:
      start_date: "{{ batch_start.isoformat() }}"
      end_date: "{{ batch_end.isoformat() }}"
```

## Troubleshooting

### No data in batch windows
- Check your source query time filtering
- Verify `begin` date is correct
- Check if data exists in the source for the time range

### Slow processing
- Reduce batch size (e.g., from `day` to `hour`)
- Optimize source queries with proper indexes
- Check if lookback value is too high

### Data missing after runs
- Ensure `event_time_column` is correctly configured in endpoints
- Check that source filtering matches endpoint cleanup column
- Verify time zone consistency across your data

### Failed batches
- Check logs for specific error messages
- Run individual batch manually by setting `begin` and `end` times
- Use `--full-refresh` to reset state if needed