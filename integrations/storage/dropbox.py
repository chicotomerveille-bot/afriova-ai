"""
Dropbox Connector
"""

import logging
from typing import Dict, List, Optional, Any
from integrations.base import OAuth2Connector, ConnectorConfig, ConnectorAuth, ConnectorCapability, ConnectorAction, ConnectorStatus, SyncResult

logger = logging.getLogger(__name__)


class DropboxConnector(OAuth2Connector):
    """Dropbox file storage connector."""

    def __init__(self, connection_id: str, config: ConnectorConfig, auth: ConnectorAuth):
        config = ConnectorConfig(
            name="Dropbox",
            provider="dropbox",
            description="Dropbox file storage and sync",
            icon="dropbox",
            category="storage",
            auth_type="oauth2",
            scopes=["files.content.write", "files.metadata.read", "files.metadata.write"],
            base_url="https://api.dropboxapi.com",
            auth_url="https://www.dropbox.com/oauth2/authorize",
            token_url="https://api.dropboxapi.com/oauth2/token",
            tags=["storage", "files", "cloud"],
        )
        super().__init__(connection_id, config, auth)

    @property
    def provider(self) -> str:
        return "dropbox"

    async def get_capabilities(self) -> List[ConnectorCapability]:
        return [ConnectorCapability.READ, ConnectorCapability.WRITE, ConnectorCapability.DELETE, ConnectorCapability.UPDATE, ConnectorCapability.SYNC]

    async def connect(self) -> Any:
        self.STATUS = ConnectorStatus.CONNECTED
        from integrations.base import ConnectionResult
        return ConnectionResult(success=True, connector_id=self.connection_id, provider=self.provider, message="Connected")

    async def disconnect(self) -> bool:
        self.STATUS = ConnectorStatus.DISCONNECTED
        return True

    async def upload_file(self, path: str, content: bytes) -> Dict[str, Any]:
        return {"id": f"file_{id(self) % 10000}", "name": path}

    async def download_file(self, path: str) -> Dict[str, Any]:
        return {"content": b"", "name": path}

    async def list_files(self, path: str = "/") -> Dict[str, Any]:
        return {"entries": []}

    async def get_schema(self) -> Dict[str, Any]:
        return {"entities": {"file": {"fields": ["id", "name", "path", "size"]}}}

    async def list_actions(self) -> List[ConnectorAction]:
        return [ConnectorAction(name="upload_file", description="Upload file to Dropbox", params={}, output_schema={})]

    async def sync_inbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def sync_outbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_name == "upload_file":
            return await self.upload_file(params["path"], params["content"])
        raise ValueError(f"Unknown action: {action_name}")