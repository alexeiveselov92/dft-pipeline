"""ClickHouse data source"""

import pyarrow as pa
from typing import Any, Dict, Optional
import logging

from ..core.base import DataSource
from ..core.data_packet import DataPacket


class ClickHouseSource(DataSource):
    """ClickHouse database data source"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.sources.clickhouse.{self.name}")
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from ClickHouse"""
        
        query = self.get_config("query")
        if not query:
            raise ValueError("query is required for ClickHouse source")
        
        try:
            from clickhouse_driver import Client
        except ImportError:
            raise ImportError("clickhouse-driver is required for ClickHouse source. Install with: pip install clickhouse-driver")
        
        # Connection parameters
        host = self.get_config("host", "localhost")
        port = self.get_config("port", 9000)
        database = self.get_config("database", "default")
        user = self.get_config("user", "default")
        password = self.get_config("password", "")
        
        try:
            # Connect to ClickHouse
            client = Client(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
            
            # Execute query and get results with column info
            result = client.execute(query, with_column_types=True)
            data, columns = result
            
            # Convert to list of dicts
            if data and columns:
                column_names = [col[0] for col in columns]
                data_list = []
                for row in data:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[column_names[i]] = value
                    data_list.append(row_dict)
                
                # Convert to Arrow table
                table = pa.table(data_list)
            else:
                # Empty result
                table = pa.table({})
            
            # Create data packet
            packet = DataPacket(
                data=table,
                source=f"clickhouse:{host}:{database}",
                metadata={
                    "query": query,
                    "host": host,
                    "database": database,
                    "variables": variables or {},
                    "column_types": {col[0]: col[1] for col in columns} if columns else {},
                }
            )
            
            self.logger.info(f"Extracted {packet.row_count} rows from ClickHouse")
            return packet
            
        except Exception as e:
            self.logger.error(f"Failed to extract from ClickHouse: {e}")
            raise RuntimeError(f"ClickHouse extraction failed: {e}")
    
    def test_connection(self) -> bool:
        """Test ClickHouse connection"""
        try:
            from clickhouse_driver import Client
            
            client = Client(
                host=self.get_config("host", "localhost"),
                port=self.get_config("port", 9000),
                database=self.get_config("database", "default"),
                user=self.get_config("user", "default"),
                password=self.get_config("password", ""),
            )
            
            # Simple test query
            client.execute("SELECT 1")
            return True
            
        except Exception as e:
            self.logger.error(f"ClickHouse connection test failed: {e}")
            return False