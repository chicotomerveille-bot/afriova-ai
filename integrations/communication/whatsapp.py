"""
WhatsApp Business Connector
"""

import logging
from typing import Dict, List, Optional, Any
from integrations.base import APIKeyConnector, ConnectorConfig, ConnectorAuth, ConnectorCapability, ConnectorAction, ConnectorStatus, SyncResult

logger = logging.getLogger(__name__)


class WhatsAppConnector(APIKeyConnector):
    """WhatsApp Business API connector (Twilio or Meta API)."""

    def __init__(self, connection_id: str, config: ConnectorConfig, auth: ConnectorAuth):
        config = ConnectorConfig(
            name="WhatsApp Business",
            provider="whatsapp",
            description="WhatsApp Business messaging via Twilio or Meta API",
            icon="whatsapp",
            category="communication",
            auth_type="apikey",
            config_fields={
                "account_sid": {"type": "string", "description": "Twilio Account SID"},
                "auth_token": {"type": "string", "description": "Twilio Auth Token"},
                "from_number": {"type": "string", "description": "WhatsApp phone number"},
            },
            tags=["communication", "chat", "messaging", "africa"],
        )
        super().__init__(connection_id, config, auth)

    @property
    def provider(self) -> str:
        return "whatsapp"

    async def get_capabilities(self) -> List[ConnectorCapability]:
        return [ConnectorCapability.READ, ConnectorCapability.WRITE, ConnectorCapability.SYNC]

    async def connect(self) -> Any:
        self.STATUS = ConnectorStatus.CONNECTED
        from integrations.base import ConnectionResult
        return ConnectionResult(success=True, connector_id=self.connection_id, provider=self.provider, message="Connected")

    async def disconnect(self) -> bool:
        self.STATUS = ConnectorStatus.DISCONNECTED
        return True

    async def send_message(self, to: str, body: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        return {"sid": f"WA{id(self) % 10000}", "status": "sent"}

    async def send_template(self, to: str, template_name: str, components: List[Dict] = None) -> Dict[str, Any]:
        return {"id": f"tpl_{id(self) % 10000}", "status": "sent"}

    async def get_schema(self) -> Dict[str, Any]:
        return {"entities": {"message": {"fields": ["id", "from", "to", "body", "timestamp"]}}}

    async def list_actions(self) -> List[ConnectorAction]:
        return [
            ConnectorAction(name="send_message", description="Send WhatsApp message", params={}, output_schema={}),
            ConnectorAction(name="send_template", description="Send template message", params={}, output_schema={}),
        ]

    async def sync_inbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def sync_outbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_name == "send_message":
            return await self.send_message(params["to"], params["body"], params.get("media_url"))
        elif action_name == "send_template":
            return await self.send_template(params["to"], params["template_name"], params.get("components"))
        raise ValueError(f"Unknown action: {action_name}")