"""Example custom data endpoint"""

from typing import Any, Dict, Optional
from datetime import datetime
from dft.core.base import DataEndpoint
from dft.core.data_packet import DataPacket


class MyCustomEndpoint(DataEndpoint):
    """Example custom endpoint that prints data info"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data by printing information about it"""
        data = packet.data
        
        try:
            import pandas as pd
            print(f"Custom endpoint received data:")
            print(f"  Shape: {data.shape}")
            print(f"  Columns: {list(data.columns)}")
            print(f"  Sample data:")
            print(data.head().to_string(index=False))
            
            # Save to file
            output_path = self.get_config('output_path', 'output/custom_data.txt')
            with open(output_path, 'w') as f:
                f.write(f"Data processed at {pd.Timestamp.now()}\n")
                f.write(f"Shape: {data.shape}\n")
                f.write(f"Columns: {list(data.columns)}\n")
                f.write("\nData:\n")
                f.write(data.to_string(index=False))
            
        except ImportError:
            # Fallback for non-pandas data
            print(f"Custom endpoint received data:")
            if isinstance(data, list):
                print(f"  Rows: {len(data)}")
                if data:
                    print(f"  Columns: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                    print(f"  Sample data: {data[:3]}")
            else:
                print(f"  Data type: {type(data)}")
                print(f"  Data: {data}")
            
            # Save to file
            output_path = self.get_config('output_path', 'output/custom_data.txt')
            with open(output_path, 'w') as f:
                f.write(f"Data processed at {datetime.now()}\n")
                if isinstance(data, list):
                    f.write(f"Rows: {len(data)}\n")
                    f.write(f"Sample data: {data[:5]}\n")
                else:
                    f.write(f"Data: {data}\n")
        
        return True
