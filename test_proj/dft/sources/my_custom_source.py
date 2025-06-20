"""Example custom data source"""

from typing import Any, Dict, Optional
from dft.core.base import DataSource
from dft.core.data_packet import DataPacket


class MyCustomSource(DataSource):
    """Example custom data source that generates sample data"""
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract sample data"""
        # Example: generate sample data with pandas fallback
        try:
            import pandas as pd
            data = {
                'id': [1, 2, 3, 4, 5],
                'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                'value': [10, 20, 30, 40, 50]
            }
            df = pd.DataFrame(data)
            timestamp = pd.Timestamp.now()
        except ImportError:
            # Fallback if pandas not available
            data = [
                {'id': 1, 'name': 'Alice', 'value': 10},
                {'id': 2, 'name': 'Bob', 'value': 20},
                {'id': 3, 'name': 'Charlie', 'value': 30},
                {'id': 4, 'name': 'David', 'value': 40},
                {'id': 5, 'name': 'Eve', 'value': 50}
            ]
            df = data  # Use list of dicts as fallback
            from datetime import datetime
            timestamp = datetime.now()
        
        return DataPacket(
            data=df,
            metadata={
                'source': 'MyCustomSource',
                'row_count': len(df) if hasattr(df, '__len__') else 5,
                'generated_at': timestamp
            }
        )
    
    def test_connection(self) -> bool:
        """Test connection (always returns True for this example)"""
        return True
