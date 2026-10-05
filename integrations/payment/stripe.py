"""
Stripe Payment Connector
"""

import logging
from typing import Dict, List, Optional, Any
from integrations.base import APIKeyConnector, ConnectorConfig, ConnectorAuth, ConnectorCapability, ConnectorAction, ConnectorStatus, SyncResult

logger = logging.getLogger(__name__)


class StripeConnector(APIKeyConnector):
    """Stripe payment processing connector."""

    def __init__(self, connection_id: str, config: ConnectorConfig, auth: ConnectorAuth):
        config = ConnectorConfig(
            name="Stripe",
            provider="stripe",
            description="Stripe payment processing",
            icon="stripe",
            category="payment",
            auth_type="apikey",
            config_fields={
                "api_key": {"type": "string", "description": "Stripe secret key"},
                "publishable_key": {"type": "string", "description": "Stripe publishable key"},
            },
            tags=["payment", "finance"],
        )
        super().__init__(connection_id, config, auth)

    @property
    def provider(self) -> str:
        return "stripe"

    async def get_capabilities(self) -> List[ConnectorCapability]:
        return [ConnectorCapability.READ, ConnectorCapability.WRITE, ConnectorCapability.SYNC]

    async def connect(self) -> Any:
        self.STATUS = ConnectorStatus.CONNECTED
        from integrations.base import ConnectionResult
        return ConnectionResult(success=True, connector_id=self.connection_id, provider=self.provider, message="Connected")

    async def disconnect(self) -> bool:
        self.STATUS = ConnectorStatus.DISCONNECTED
        return True

    async def create_payment_intent(self, amount: int, currency: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        return {"id": f"pi_{id(self) % 10000}", "amount": amount, "currency": currency, "status": "requires_payment_method"}

    async def create_invoice(self, customer_id: str, amount: float, description: str) -> Dict[str, Any]:
        return {"id": f"inv_{id(self) % 10000}", "amount": amount}

    async def get_schema(self) -> Dict[str, Any]:
        return {"entities": {"payment_intent": {"fields": ["id", "amount", "currency", "status"]}, "invoice": {"fields": ["id", "amount", "customer"]}}}

    async def list_actions(self) -> List[ConnectorAction]:
        return [
            ConnectorAction(name="create_payment_intent", description="Create payment intent", params={}, output_schema={}),
            ConnectorAction(name="create_invoice", description="Create invoice", params={}, output_schema={}),
        ]

    async def sync_inbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def sync_outbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_name == "create_payment_intent":
            return await self.create_payment_intent(params["amount"], params["currency"], params.get("customer_id"))
        elif action_name == "create_invoice":
            return await self.create_invoice(params["customer_id"], params["amount"], params["description"])
        raise ValueError(f"Unknown action: {action_name}")