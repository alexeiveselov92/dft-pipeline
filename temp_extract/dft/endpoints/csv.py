"""CSV data endpoint"""

from pathlib import Path
from typing import Any, Dict, Optional
import pyarrow.csv as pa_csv

from ..core.base import DataEndpoint
from ..core.data_packet import DataPacket


class CSVEndpoint(DataEndpoint):
    """CSV file data endpoint"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to CSV file"""
        
        file_path = self.get_config("file_path")
        if not file_path:
            raise ValueError("file_path is required for CSV endpoint")
        
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Use Arrow CSV writer (faster than pandas)
            pa_csv.write_csv(packet.data, file_path)
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to save CSV file {file_path}: {e}")