"""Data validation processor"""

from typing import Any, Dict, List, Optional
import pyarrow as pa

from ..core.base import DataProcessor
from ..core.data_packet import DataPacket


class DataValidator(DataProcessor):
    """Data validation processor"""
    
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Validate data packet"""
        
        errors = []
        
        # Check row count constraints
        row_count_min = self.get_config("row_count_min")
        row_count_max = self.get_config("row_count_max")
        
        if row_count_min is not None and packet.row_count < row_count_min:
            errors.append(f"Row count {packet.row_count} is below minimum {row_count_min}")
        
        if row_count_max is not None and packet.row_count > row_count_max:
            errors.append(f"Row count {packet.row_count} exceeds maximum {row_count_max}")
        
        # Check required columns
        required_columns = self.get_config("required_columns", [])
        if required_columns:
            missing_columns = set(required_columns) - set(packet.column_names)
            if missing_columns:
                errors.append(f"Missing required columns: {list(missing_columns)}")
        
        # Check schema if enabled
        schema_check = self.get_config("schema_check", False)
        if schema_check and packet.data is not None:
            # Basic schema validation - check for null values in required columns
            for col_name in required_columns:
                if col_name in packet.column_names:
                    column = packet.data.column(col_name)
                    null_count = column.null_count
                    if null_count > 0:
                        errors.append(f"Column {col_name} contains {null_count} null values")
        
        # If there are validation errors, raise exception
        if errors:
            error_message = "; ".join(errors)
            raise ValueError(f"Data validation failed: {error_message}")
        
        # Add validation metadata
        packet.add_metadata("validation_passed", True)
        packet.add_metadata("validation_checks", {
            "row_count_min": row_count_min,
            "row_count_max": row_count_max,
            "required_columns": required_columns,
            "schema_check": schema_check,
        })
        
        return packet