"""Example custom data processor"""

from typing import Any, Dict, Optional
from datetime import datetime
from dft.core.base import DataProcessor
from dft.core.data_packet import DataPacket


class MyCustomProcessor(DataProcessor):
    """Example custom processor that doubles values"""
    
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Process data by doubling the 'value' column"""
        try:
            import pandas as pd
            df = packet.data.copy()
            
            # Example processing: double the value column if it exists
            if 'value' in df.columns:
                df['value'] = df['value'] * 2
                df['processed'] = True
            
            timestamp = pd.Timestamp.now()
        except ImportError:
            # Fallback for non-pandas data
            if isinstance(packet.data, list):
                df = []
                for row in packet.data:
                    new_row = row.copy()
                    if 'value' in new_row:
                        new_row['value'] = new_row['value'] * 2
                        new_row['processed'] = True
                    df.append(new_row)
            else:
                df = packet.data
            timestamp = datetime.now()
        
        return DataPacket(
            data=df,
            metadata={
                **packet.metadata,
                'processor': 'MyCustomProcessor',
                'processed_at': timestamp
            }
        )
