# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.8] - 2025-07-01

### Fixed
- **Fixed ClickHouse empty result handling**: Resolved PyArrow table creation error for empty query results
- **Enhanced empty dataset handling**: Improved schema preservation for empty ClickHouse results

## [0.3.7] - 2025-07-01

### Fixed
- **Critical Fix**: Environment variable template rendering in connections now works properly
- **Resolved ClickHouse connection issues**: Fixed "Servname not supported for ai_socktype" error
- **Enhanced ComponentFactory**: Added TemplateRenderer support for connection configurations

### Technical
- Modified ComponentFactory to process Jinja2 templates in connection strings
- Fixed template rendering timing for database connections

## [0.3.6] - 2025-07-01

### Fixed
- **Fixed microbatch datetime concatenation error**: Resolved "can only concatenate str (not "datetime.timedelta") to str" error in microbatch strategy
- **Enhanced error reporting**: Added full traceback output to console and logs for better debugging
- **Improved datetime handling**: Fixed datetime parsing and string formatting in microbatch processing

### Changed
- **Consolidated examples**: Moved all examples to `example_project/` directory for better organization
- **Better error visibility**: Step errors now show exact file and line number where the error occurred

### Technical
- Fixed `get_batch_variables()` to return ISO format strings instead of datetime objects
- Added proper datetime parsing in runner for microbatch config
- Enhanced exception handling in step execution with full tracebacks
- Cleaned up project structure by removing duplicate example directories

## [0.3.1] - 2024

### Added
- **Automatic Multi-Group Comparisons**: Automatic detection of all groups in data with pairwise comparisons
- **Pandas-Free Architecture**: Pure PyArrow + NumPy implementation for better performance

### Changed
- **BREAKING CHANGE**: Removed `control_group` and `treatment_group` parameters from A/B testing
- **Configuration Simplification**: No need to manually specify which groups to compare
- **Updated Documentation**: All examples show multi-group experiments

### Security
- **Excluded**: Development folders (`*for_developing`) from published package

---

For detailed version-specific information, see the [changelogs/](./changelogs/) directory.