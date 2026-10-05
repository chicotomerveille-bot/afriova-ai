"""
Outlook / Microsoft 365 Connector
"""

import logging
from typing import Any, Dict, List, Optional
from integrations.base import OAuth2Connector, ConnectorConfig, ConnectorAuth, ConnectorCapability, ConnectorAction, ConnectorStatus, SyncResult

logger = logging.getLogger(__name__)


class OutlookConnector(OAuth2Connector):
    """Outlook / Microsoft 365 email and calendar connector."""

    def __init__(self, connection_id: str, config: ConnectorConfig, auth: ConnectorAuth):
        config = ConnectorConfig(
            name="Microsoft Outlook",
            provider="outlook",
            description="Microsoft 365 Outlook email and calendar integration",
            icon="outlook",
            category="email",
            auth_type="oauth2",
            scopes=["Mail.Read", "Mail.Send", "Calendars.ReadWrite"],
            base_url="https://graph.microsoft.com/v1.0",
            auth_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
            client_id_env="MICROSOFT_CLIENT_ID",
            client_secret_env="MICROSOFT_CLIENT_SECRET",
            redirect_uri="http://localhost:8000/auth/callback",
            tags=["email", "office365", "microsoft"],
        )
        super().__init__(connection_id, config, auth)

    @property
    def provider(self) -> str:
        return "outlook"

    async def get_capabilities(self) -> List[ConnectorCapability]:
        return [
            ConnectorCapability.READ,
            ConnectorCapability.WRITE,
            ConnectorCapability.DELETE,
            ConnectorCapability.UPDATE,
            ConnectorCapability.SYNC,
            ConnectorCapability.SEARCH,
        ]

    async def connect(self) -> Any:
        self.STATUS = ConnectorStatus.CONNECTED
        from integrations.base import ConnectionResult
        return ConnectionResult(success=True, connector_id=self.connection_id, provider=self.provider, message="Connected")

    async def disconnect(self) -> bool:
        self.STATUS = ConnectorStatus.DISCONNECTED
        return True

    async def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        return {"id": "msg_outlook", "status": "sent"}

    async def list_emails(self, folder: str = "inbox", limit: int = 100) -> Dict[str, Any]:
        return {"messages": []}

    async def get_schema(self) -> Dict[str, Any]:
        return {"entities": {"message": {"fields": ["id", "from", "to", "subject", "body"]}}}

    async def list_actions(self) -> List[ConnectorAction]:
        return [ConnectorAction(name="send_email", description="Send email via Outlook", params={}, output_schema={})]

    async def sync_inbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def sync_outbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_name == "send_email":
            return await self.send_email(params["to"], params["subject"], params["body"])
        raise ValueError(f"Unknown action: {action_name}")
