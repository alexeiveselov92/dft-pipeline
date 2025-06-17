"""PostgreSQL data endpoint"""

from typing import Any, Dict, Optional
import logging
import pyarrow as pa

from ..core.base import DataEndpoint
from ..core.data_packet import DataPacket


class PostgreSQLEndpoint(DataEndpoint):
    """PostgreSQL database data endpoint"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.endpoints.postgresql.{self.name}")
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to PostgreSQL table"""
        
        table_name = self.get_config("table")
        if not table_name:
            raise ValueError("table is required for PostgreSQL endpoint")
        
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL endpoint")
        
        # Connection parameters
        conn_params = {
            "host": self.get_config("host", "localhost"),
            "port": self.get_config("port", 5432),
            "database": self.get_config("database"),
            "user": self.get_config("user"),
            "password": self.get_config("password"),
        }
        
        conn_params = {k: v for k, v in conn_params.items() if v is not None}
        
        # Load mode
        mode = self.get_config("mode", "append")  # append, replace, upsert
        auto_create = self.get_config("auto_create", True)
        
        try:
            conn = psycopg2.connect(**conn_params)
            cur = conn.cursor()
            
            # Check if table exists
            table_exists = self._table_exists(cur, table_name)
            
            if not table_exists and auto_create:
                self._create_table(cur, table_name, packet.data)
                conn.commit()
                self.logger.info(f"Created table {table_name}")
            
            # Handle different load modes
            if mode == "replace":
                cur.execute(f"TRUNCATE TABLE {table_name}")
                conn.commit()
                self.logger.info(f"Truncated table {table_name}")
            
            # Convert Arrow to list of dicts for bulk insert
            data_list = packet.to_dict_list()
            
            if data_list:
                # Get column names
                columns = list(data_list[0].keys())
                column_placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f'"{col}"' for col in columns])
                
                # Prepare bulk insert SQL
                insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({column_placeholders})'
                
                # Convert data to tuples for bulk insert
                data_tuples = [tuple(row[col] for col in columns) for row in data_list]
                
                # Execute bulk insert
                psycopg2.extras.execute_batch(cur, insert_sql, data_tuples)
                conn.commit()
                
                self.logger.info(f"Loaded {len(data_list)} rows to PostgreSQL table {table_name}")
            else:
                self.logger.warning("No data to load to PostgreSQL")
            
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load to PostgreSQL: {e}")
            raise RuntimeError(f"PostgreSQL load failed: {e}")
    
    def _table_exists(self, cursor, table_name: str) -> bool:
        """Check if table exists"""
        try:
            cursor.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
                (table_name,)
            )
            return cursor.fetchone()[0]
        except Exception:
            return False
    
    def _create_table(self, cursor, table_name: str, arrow_table: pa.Table) -> None:
        """Create table from Arrow schema"""
        
        # Get user-defined schema if provided
        user_schema = self.get_config("schema", {})
        
        # Map Arrow types to PostgreSQL types
        type_mapping = {
            pa.string(): "TEXT",
            pa.int8(): "SMALLINT",
            pa.int16(): "SMALLINT", 
            pa.int32(): "INTEGER",
            pa.int64(): "BIGINT",
            pa.uint8(): "SMALLINT",
            pa.uint16(): "INTEGER",
            pa.uint32(): "BIGINT", 
            pa.uint64(): "BIGINT",
            pa.float32(): "REAL",
            pa.float64(): "DOUBLE PRECISION",
            pa.bool_(): "BOOLEAN",
            pa.date32(): "DATE",
            pa.date64(): "DATE",
            pa.timestamp('s'): "TIMESTAMP",
            pa.timestamp('ms'): "TIMESTAMP",
            pa.timestamp('us'): "TIMESTAMP",
            pa.timestamp('ns'): "TIMESTAMP",
        }
        
        # Build column definitions
        columns = []
        for field in arrow_table.schema:
            column_name = field.name
            
            # Use user-defined type if provided
            if column_name in user_schema:
                column_type = user_schema[column_name]
            else:
                # Auto-detect type
                arrow_type = field.type
                column_type = type_mapping.get(arrow_type, "TEXT")
            
            columns.append(f'"{column_name}" {column_type}')
        
        # Create table SQL
        create_sql = f'''
        CREATE TABLE "{table_name}" (
            {', '.join(columns)}
        )
        '''
        
        cursor.execute(create_sql)
        self.logger.info(f"Created PostgreSQL table {table_name} with schema: {columns}")
    
    def test_connection(self) -> bool:
        """Test PostgreSQL connection"""
        try:
            import psycopg2
            
            conn_params = {
                "host": self.get_config("host", "localhost"),
                "port": self.get_config("port", 5432),
                "database": self.get_config("database"),
                "user": self.get_config("user"),
                "password": self.get_config("password"),
            }
            
            conn_params = {k: v for k, v in conn_params.items() if v is not None}
            
            conn = psycopg2.connect(**conn_params)
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL connection test failed: {e}")
            return False