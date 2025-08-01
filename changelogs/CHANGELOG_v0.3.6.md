# Changelog v0.3.6

## Fixes
- **Fixed microbatch datetime concatenation error**: Resolved "can only concatenate str (not "datetime.timedelta") to str" error in microbatch strategy
- **Enhanced error reporting**: Added full traceback output to console and logs for better debugging
- **Improved datetime handling**: Fixed datetime parsing and string formatting in microbatch processing

## Improvements  
- **Consolidated examples**: Moved all examples to `example_project/` directory for better organization
- **Better error visibility**: Step errors now show exact file and line number where the error occurred

## Technical Changes
- Fixed `get_batch_variables()` to return ISO format strings instead of datetime objects
- Added proper datetime parsing in runner for microbatch config
- Enhanced exception handling in step execution with full tracebacks
- Cleaned up project structure by removing duplicate example directories

Generated with Claude Code