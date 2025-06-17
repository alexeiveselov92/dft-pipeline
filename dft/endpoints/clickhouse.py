"""ClickHouse data endpoint"""

from typing import Any, Dict, Optional
import logging
import pyarrow as pa

from ..core.base import DataEndpoint
from ..core.data_packet import DataPacket


class ClickHouseEndpoint(DataEndpoint):
    """ClickHouse database data endpoint"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.endpoints.clickhouse.{self.name}")

    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to ClickHouse table"""

        table_name = self.get_config("table")
        if not table_name:
            raise ValueError("table is required for ClickHouse endpoint")

        try:
            from clickhouse_driver import Client
        except ImportError:
            raise ImportError("clickhouse-driver is required for ClickHouse endpoint")

        # Connection parameters
        host = self.get_config("host", "localhost")
        port = self.get_config("port", 9000)
        database = self.get_config("database", "default")
        user = self.get_config("user", "default")
        password = self.get_config("password", "")

        # Load mode
        mode = self.get_config("mode", "append")  # append, replace, upsert
        auto_create = self.get_config("auto_create", True)

        try:
            client = Client(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )

            # Check if table exists
            table_exists = self._table_exists(client, table_name)

            if not table_exists and auto_create:
                self._create_table(client, table_name, packet.data)
                self.logger.info(f"Created table {table_name}")

            # Handle different load modes
            if mode == "replace":
                # Truncate table first
                client.execute(f"TRUNCATE TABLE {table_name}")
                self.logger.info(f"Truncated table {table_name}")

            # Convert Arrow to format suitable for ClickHouse
            data_list = packet.to_dict_list()

            if data_list:
                # Get column names and prepare data
                columns = list(data_list[0].keys())
                values = [tuple(row[col] for col in columns) for row in data_list]

                insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES"
                client.execute(insert_query, values)

                self.logger.info(f"Loaded {len(values)} rows to ClickHouse table {table_name}")
            else:
                self.logger.warning("No data to load to ClickHouse")

            return True

        except Exception as e:
            self.logger.error(f"Failed to load to ClickHouse: {e}")
            raise RuntimeError(f"ClickHouse load failed: {e}")

    def _table_exists(self, client, table_name: str) -> bool:
        """Check if table exists"""
        try:
            database = self.get_config("database", "default")
            result = client.execute(
                "SELECT count() FROM system.tables WHERE database = %s AND name = %s", [database, table_name]
            )
            return result[0][0] > 0
        except Exception:
            return False

    def _create_table(self, client, table_name: str, arrow_table: pa.Table) -> None:
        """Create table from explicit schema definition"""

        # Require explicit schema definition
        user_schema = self.get_config("schema")
        if not user_schema:
            raise ValueError(f"Schema is required for ClickHouse endpoint. Please define schema for table {table_name}")

        # Build column definitions from user-defined schema only
        columns = []
        for column_name, column_type in user_schema.items():
            columns.append(f"{column_name} {column_type}")

        # Create table SQL
        engine = self.get_config("engine", "MergeTree()")
        order_by = self.get_config("order_by", "tuple()")

        create_sql = f"""
        CREATE TABLE {table_name} (
            {', '.join(columns)}
        ) ENGINE = {engine}
        ORDER BY {order_by}
        """

        client.execute(create_sql)
        self.logger.info(f"Created ClickHouse table {table_name} with schema: {columns}")

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

            client.execute("SELECT 1")
            return True

        except Exception as e:
            self.logger.error(f"ClickHouse connection test failed: {e}")
            return False
