"""
OpenAI Connector
"""

import logging
from typing import Dict, List, Optional, Any
from integrations.base import APIKeyConnector, ConnectorConfig, ConnectorAuth, ConnectorCapability, ConnectorAction, ConnectorStatus, SyncResult

logger = logging.getLogger(__name__)


class OpenAIConnector(APIKeyConnector):
    """OpenAI API connector for LLM access."""

    def __init__(self, connection_id: str, config: ConnectorConfig, auth: ConnectorAuth):
        config = ConnectorConfig(
            name="OpenAI",
            provider="openai",
            description="OpenAI API for LLM access",
            icon="openai",
            category="ai",
            auth_type="apikey",
            config_fields={"api_key": {"type": "string", "description": "OpenAI API key"}},
            tags=["ai", "llm", "chatgpt"],
        )
        super().__init__(connection_id, config, auth)

    @property
    def provider(self) -> str:
        return "openai"

    async def get_capabilities(self) -> List[ConnectorCapability]:
        return [ConnectorCapability.READ, ConnectorCapability.RUN_ACTION]

    async def connect(self) -> Any:
        self.STATUS = ConnectorStatus.CONNECTED
        from integrations.base import ConnectionResult
        return ConnectionResult(success=True, connector_id=self.connection_id, provider=self.provider, message="Connected")

    async def disconnect(self) -> bool:
        self.STATUS = ConnectorStatus.DISCONNECTED
        return True

    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-4", temperature: float = 0.7) -> Dict[str, Any]:
        return {"choices": [{"message": {"role": "assistant", "content": "Response"}}], "usage": {}}

    async def get_schema(self) -> Dict[str, Any]:
        return {"entities": {"chat_completion": {"fields": ["model", "messages", "choices"]}}}

    async def list_actions(self) -> List[ConnectorAction]:
        return [
            ConnectorAction(name="chat_completion", description="Generate chat completion", params={}, output_schema={}),
        ]

    async def sync_inbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def sync_outbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_name == "chat_completion":
            return await self.chat_completion(params["messages"], params.get("model", "gpt-4"), params.get("temperature", 0.7))
        raise ValueError(f"Unknown action: {action_name}")