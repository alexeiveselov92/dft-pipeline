# Changelog v0.3.8

## Fixes
- **Fixed ClickHouse empty result handling**: Resolved "Must pass names or schema when constructing Table or RecordBatch" error when ClickHouse queries return empty results
- **Enhanced PyArrow table creation**: Improved handling of empty datasets with proper schema preservation

## Technical Changes
- Modified ClickHouse source to properly handle empty query results while preserving column schema
- Added proper empty table creation with column names when data is empty but schema is available
- Improved error handling for PyArrow table construction

## Impact
This fix resolves crashes when ClickHouse queries return no rows (e.g., when filtering by date ranges with no data). The pipeline will now correctly handle empty results and continue processing.

Generated with Claude Code