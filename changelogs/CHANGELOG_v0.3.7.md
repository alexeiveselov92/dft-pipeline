# Changelog v0.3.7

## Critical Fixes
- **Fixed environment variable template rendering in connections**: Environment variables in connection configurations (like `{{ env_var('CH_HOST') }}`) are now properly rendered
- **Enhanced ComponentFactory with template support**: Added TemplateRenderer to ComponentFactory to process Jinja2 templates in connection strings
- **Resolved ClickHouse connection issues**: Fixed "Servname not supported for ai_socktype" error caused by unrendered template variables

## Technical Changes
- Modified `ComponentFactory.__init__()` to accept `TemplateRenderer` parameter
- Added template rendering in `_get_source_config()` method for connection configurations
- Updated `PipelineRunner` to pass `TemplateRenderer` to `ComponentFactory`

## Impact
This fix resolves connection issues with all database sources (PostgreSQL, MySQL, ClickHouse) when using environment variables in connection configurations. Users can now properly use `.env` files with template variables like:

```yaml
connections:
  clickhouse_prod:
    type: clickhouse
    host: "{{ env_var('CH_HOST', 'localhost') }}"
    port: "{{ env_var('CH_PORT', '9000') }}"
```

Generated with Claude Code