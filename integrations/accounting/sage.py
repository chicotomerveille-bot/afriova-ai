"""
Sage Accounting Connector
"""

import logging
from typing import Dict, List, Optional, Any
from integrations.base import OAuth2Connector, ConnectorConfig, ConnectorAuth, ConnectorCapability, ConnectorAction, ConnectorStatus, SyncResult

logger = logging.getLogger(__name__)


class SageConnector(OAuth2Connector):
    """Sage accounting connector."""

    def __init__(self, connection_id: str, config: ConnectorConfig, auth: ConnectorAuth):
        config = ConnectorConfig(
            name="Sage Accounting",
            provider="sage",
            description="Sage accounting integration",
            icon="sage",
            category="accounting",
            auth_type="oauth2",
            scopes=["invoice", "contact"],
            base_url="https://api.sage.com",
            tags=["accounting", "finance"],
        )
        super().__init__(connection_id, config, auth)

    @property
    def provider(self) -> str:
        return "sage"

    async def get_capabilities(self) -> List[ConnectorCapability]:
        return [ConnectorCapability.READ, ConnectorCapability.WRITE, ConnectorCapability.UPDATE, ConnectorCapability.SYNC]

    async def connect(self) -> Any:
        self.STATUS = ConnectorStatus.CONNECTED
        from integrations.base import ConnectionResult
        return ConnectionResult(success=True, connector_id=self.connection_id, provider=self.provider, message="Connected")

    async def disconnect(self) -> bool:
        self.STATUS = ConnectorStatus.DISCONNECTED
        return True

    async def create_invoice(self, contact_id: str, amount: float, description: str) -> Dict[str, Any]:
        return {"id": f"sage_inv_{id(self)}", "amount": amount}

    async def get_schema(self) -> Dict[str, Any]:
        return {"entities": {"invoice": {"fields": ["id", "contactId", "amount", "description"]}}}

    async def list_actions(self) -> List[ConnectorAction]:
        return [ConnectorAction(name="create_invoice", description="Create invoice", params={}, output_schema={})]

    async def sync_inbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def sync_outbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_name == "create_invoice":
            return await self.create_invoice(params["contact_id"], params["amount"], params["description"])
        raise ValueError(f"Unknown action: {action_name}")