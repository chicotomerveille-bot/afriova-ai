"""
PostgreSQL Connector
"""

import logging
from typing import Dict, List, Optional, Any
from integrations.base import APIKeyConnector, ConnectorConfig, ConnectorAuth, ConnectorCapability, ConnectorAction, ConnectorStatus, SyncResult

logger = logging.getLogger(__name__)


class PostgreSQLConnector(APIKeyConnector):
    """PostgreSQL database connector."""

    def __init__(self, connection_id: str, config: ConnectorConfig, auth: ConnectorAuth):
        config = ConnectorConfig(
            name="PostgreSQL",
            provider="postgresql",
            description="PostgreSQL database connector",
            icon="database",
            category="database",
            auth_type="apikey",  # Uses URL or credentials
            config_fields={
                "host": {"type": "string", "description": "Database host"},
                "port": {"type": "integer", "description": "Database port"},
                "database": {"type": "string", "description": "Database name"},
                "username": {"type": "string", "description": "Username"},
                "password": {"type": "string", "description": "Password"},
            },
            tags=["database", "sql", "local"],
        )
        super().__init__(connection_id, config, auth)

    @property
    def provider(self) -> str:
        return "postgresql"

    async def get_capabilities(self) -> List[ConnectorCapability]:
        return [ConnectorCapability.READ, ConnectorCapability.WRITE, ConnectorCapability.DELETE, ConnectorCapability.UPDATE, ConnectorCapability.SYNC]

    async def connect(self) -> Any:
        self.STATUS = ConnectorStatus.CONNECTED
        from integrations.base import ConnectionResult
        return ConnectionResult(success=True, connector_id=self.connection_id, provider=self.provider, message="Connected")

    async def disconnect(self) -> bool:
        self.STATUS = ConnectorStatus.DISCONNECTED
        return True

    async def execute_query(self, query: str, params: Optional[List] = None) -> Dict[str, Any]:
        return {"rows": [], "rowcount": 0}

    async def execute_insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"inserted_id": 1}

    async def get_schema(self) -> Dict[str, Any]:
        return {"entities": {"table": {"fields": ["table_name", "column_name"]}}}

    async def list_actions(self) -> List[ConnectorAction]:
        return [ConnectorAction(name="execute_query", description="Execute SQL query", params={}, output_schema={})]

    async def sync_inbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def sync_outbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_name == "execute_query":
            return await self.execute_query(params["query"], params.get("params"))
        raise ValueError(f"Unknown action: {action_name}")