"""
Base Connector Framework for Afriova AI
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import logging
import asyncio

logger = logging.getLogger(__name__)


class ConnectorStatus(Enum):
    """Status of a connector connection."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"
    EXPIRED = "expired"


class ConnectorCapability(Enum):
    """Capabilities a connector may support."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    UPDATE = "update"
    SYNC = "sync"
    WEBHOOK = "webhook"
    LISTEN = "listen"
    INBOUND_SYNC = "inbound_sync"
    OUTBOUND_SYNC = "outbound_sync"
    RUN_ACTION = "run_action"
    GET_SCHEMA = "get_schema"
    SEARCH = "search"
    BATCH = "batch"


@dataclass(frozen=True)
class ConnectorAuth:
    """Base authentication data for a connector."""
    provider: str
    user_id: Optional[str] = None
    organization_id: Optional[UUID] = None
    authenticated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self, leeway_seconds: int = 60) -> bool:
        if self.expires_at is None:
            return False
        from datetime import timedelta
        return datetime.now(timezone.utc) > (self.expires_at - timedelta(seconds=leeway_seconds))


@dataclass
class OAuth2Token:
    """OAuth2 access token and metadata."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    scope: Optional[str] = None

    @property
    def expires_at(self) -> Optional[datetime]:
        if self.expires_in is None:
            return None
        from datetime import timedelta
        return datetime.now(timezone.utc) + timedelta(seconds=self.expires_in)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "scope": self.scope,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuth2Token":
        expires_at = data.get("expires_at")
        if expires_at and isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except Exception:
                expires_at = None
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in"),
            scope=data.get("scope"),
        )


@dataclass
class ConnectionResult:
    """Result of a connection attempt."""
    success: bool
    connector_id: str
    provider: str
    user_id: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    connector_config: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    items_synced: int = 0
    items_failed: int = 0
    errors: List[str] = field(default_factory=list)
    sync_direction: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ConnectorAction:
    """Defines an executable action provided by a connector."""
    name: str
    description: str
    params: Dict[str, Dict[str, Any]]
    output_schema: Dict[str, Any]


@dataclass
class ConnectorConfig:
    """Configuration for a connector."""
    name: str
    provider: str
    description: str
    icon: str
    category: str
    auth_type: str
    config_fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    scopes: List[str] = field(default_factory=list)
    base_url: Optional[str] = None
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    client_id_env: Optional[str] = None
    client_secret_env: Optional[str] = None
    redirect_uri: Optional[str] = None
    documentation_url: Optional[str] = None
    is_local: bool = False
    is_african: bool = False
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    priority: int = 100


@dataclass
class ConnectorMetadata:
    """Metadata about a connector implementation."""
    provider: str
    class_ref: str
    config: ConnectorConfig
    capabilities: List[ConnectorCapability]
    default_sync_interval: Optional[int] = None
    max_batch_size: int = 1000
    rate_limit: Optional[int] = None


class BaseConnector(ABC):
    """Abstract base class for all enterprise connectors."""

    STATUS: ConnectorStatus = ConnectorStatus.DISCONNECTED

    def __init__(self, connection_id: UUID | str, config: ConnectorConfig, auth: ConnectorAuth):
        self.connection_id = str(connection_id)
        self.config = config
        self.auth = auth
        self._client: Optional[Any] = None
        self._lock = asyncio.Lock()
        self._last_sync: Optional[datetime] = None
        self._connection_details: Dict[str, Any] = {}

    @property
    @abstractmethod
    def provider(self) -> str:
        pass

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def category(self) -> str:
        return self.config.category

    @abstractmethod
    async def get_capabilities(self) -> List[ConnectorCapability]:
        pass

    async def connect(self) -> ConnectionResult:
        self.STATUS = ConnectorStatus.CONNECTING
        try:
            # Default implementation - override in subclass
            self.STATUS = ConnectorStatus.CONNECTED
            return ConnectionResult(
                success=True,
                connector_id=self.connection_id,
                provider=self.provider,
                message="Connected successfully",
            )
        except Exception as e:
            self.STATUS = ConnectorStatus.ERROR
            return ConnectionResult(
                success=False,
                connector_id=self.connection_id,
                provider=self.provider,
                message="Connection failed",
                error=str(e),
            )

    async def disconnect(self) -> bool:
        try:
            if hasattr(self, '_client') and self._client:
                try:
                    await self._client.aclose()
                except:
                    pass
                self._client = None
            self.STATUS = ConnectorStatus.DISCONNECTED
            return True
        except Exception as e:
            logger.error(f"Error disconnecting {self.provider}: {e}")
            return False

    async def sync_inbound(self, entity_types: Optional[List[str]] = None, limit: int = 1000) -> SyncResult:
        raise NotImplementedError

    async def sync_outbound(self, entity_types: Optional[List[str]] = None, limit: int = 1000) -> SyncResult:
        raise NotImplementedError

    async def sync(self, entity_types: Optional[List[str]] = None, direction: str = "both", limit: int = 1000) -> SyncResult:
        results = []
        if direction in ("inbound", "both"):
            results.append(await self.sync_inbound(entity_types, limit))
        if direction in ("outbound", "both"):
            results.append(await self.sync_outbound(entity_types, limit))
        total_items = sum(r.items_synced for r in results)
        total_failed = sum(r.items_failed for r in results)
        all_errors = []
        for r in results:
            all_errors.extend(r.errors)
        return SyncResult(
            success=total_failed == 0,
            items_synced=total_items,
            items_failed=total_failed,
            errors=all_errors,
        )

    async def list_actions(self) -> List[ConnectorAction]:
        return []

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        pass

    async def list_entities(self) -> List[str]:
        schema = await self.get_schema()
        return list(schema.get("entities", {}).keys())

    async def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "connection_id": self.connection_id,
            "status": self.STATUS.value,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
        }

    async def test_connection(self) -> bool:
        try:
            await self.health_check()
            return self.STATUS == ConnectorStatus.CONNECTED
        except Exception:
            return False


class OAuth2Connector(BaseConnector):
    """Base for OAuth2-based connectors."""

    def __init__(self, connection_id: UUID | str, config: ConnectorConfig, auth: ConnectorAuth):
        super().__init__(connection_id, config, auth)

    async def get_oauth_authorization_url(self, redirect_uri: Optional[str] = None, state: Optional[str] = None) -> str:
        raise NotImplementedError

    async def exchange_code(self, code: str, redirect_uri: Optional[str] = None) -> OAuth2Token:
        raise NotImplementedError

    async def refresh_tokens(self) -> OAuth2Token:
        raise NotImplementedError


class APIKeyConnector(BaseConnector):
    """Base for API key / token-based connectors."""

    def __init__(self, connection_id: UUID | str, config: ConnectorConfig, auth: ConnectorAuth):
        super().__init__(connection_id, config, auth)

    async def _get_auth_headers(self) -> Dict[str, str]:
        api_key = self.auth.metadata.get("api_key")
        if api_key:
            return {"Authorization": f"Bearer {api_key}"}
        return {}
