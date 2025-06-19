"""Example custom data processor"""

from typing import Any, Dict, Optional
from dft.core.base import DataProcessor
from dft.core.data_packet import DataPacket


class MyCustomProcessor(DataProcessor):
    """Example custom processor that doubles values"""
    
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Process data by doubling the 'value' column"""
        data = packet.data
        
        try:
            import pandas as pd
            df = data.copy()
            # Example processing: double the value column if it exists
            if 'value' in df.columns:
                df['value'] = df['value'] * 2
                df['processed'] = True
            processed_data = df
            timestamp = pd.Timestamp.now()
        except (ImportError, AttributeError):
            # Fallback for list of dicts
            if isinstance(data, list):
                processed_data = []
                for item in data:
                    new_item = item.copy()
                    if 'value' in new_item:
                        new_item['value'] = new_item['value'] * 2
                    new_item['processed'] = True
                    processed_data.append(new_item)
            else:
                processed_data = data
            from datetime import datetime
            timestamp = datetime.now()
        
        return DataPacket(
            data=processed_data,
            metadata={
                **packet.metadata,
                'processor': 'MyCustomProcessor',
                'processed_at': timestamp
            }
        )