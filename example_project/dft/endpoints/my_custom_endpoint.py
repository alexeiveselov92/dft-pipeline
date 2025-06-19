"""Example custom data endpoint"""

from typing import Any, Dict, Optional
from dft.core.base import DataEndpoint
from dft.core.data_packet import DataPacket


class MyCustomEndpoint(DataEndpoint):
    """Example custom endpoint that prints data info"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data by printing information about it"""
        data = packet.data
        
        try:
            import pandas as pd
            df = data
            print(f"Custom endpoint received data:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Sample data:")
            print(df.head().to_string(index=False))
            data_str = df.to_string(index=False)
            shape_info = f"Shape: {df.shape}"
            columns_info = f"Columns: {list(df.columns)}"
            timestamp = pd.Timestamp.now()
        except (ImportError, AttributeError):
            # Fallback for list of dicts
            print(f"Custom endpoint received data:")
            if isinstance(data, list):
                print(f"  Records: {len(data)}")
                if data:
                    print(f"  Keys: {list(data[0].keys())}")
                    print(f"  Sample data:")
                    for item in data[:3]:  # Show first 3 items
                        print(f"    {item}")
                data_str = str(data)
                shape_info = f"Records: {len(data)}"
                columns_info = f"Keys: {list(data[0].keys()) if data else []}"
            else:
                print(f"  Data: {data}")
                data_str = str(data)
                shape_info = f"Type: {type(data)}"
                columns_info = "N/A"
            from datetime import datetime
            timestamp = datetime.now()
        
        # You could save to file, send to API, etc.
        output_path = self.get_config('output_path', 'output/custom_data.txt')
        with open(output_path, 'w') as f:
            f.write(f"Data processed at {timestamp}\n")
            f.write(f"{shape_info}\n")
            f.write(f"{columns_info}\n")
            f.write("\nData:\n")
            f.write(data_str)
        
        return True