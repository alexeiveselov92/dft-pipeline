"""CSV data source"""

import pyarrow as pa
import pyarrow.csv as pa_csv
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.base import DataSource
from ..core.data_packet import DataPacket


class CSVSource(DataSource):
    """CSV file data source"""
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from CSV file"""
        
        file_path = self.get_config("file_path")
        if not file_path:
            raise ValueError("file_path is required for CSV source")
        
        # Read CSV file directly with Arrow (faster than pandas)
        table = pa_csv.read_csv(file_path)
        
        # Create data packet
        packet = DataPacket(
            data=table,
            source=f"csv:{file_path}",
            metadata={
                "file_path": file_path,
                "file_size": Path(file_path).stat().st_size if Path(file_path).exists() else 0,
            }
        )
        
        return packet
    
    def test_connection(self) -> bool:
        """Test if CSV file exists and is readable"""
        file_path = self.get_config("file_path")
        if not file_path:
            return False
        
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and path.suffix.lower() == '.csv'
        except Exception:
            return False