"""
Connector Registry for Afriova AI
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type
from uuid import UUID, uuid4
import logging
from threading import RLock

from integrations.base import BaseConnector, ConnectorConfig, ConnectorAuth, ConnectorMetadata

logger = logging.getLogger(__name__)


@dataclass
class ConnectorRegistration:
    """Registration entry for a connector in the registry."""
    metadata: ConnectorMetadata
    connector_class: Type[BaseConnector]
    loaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConnectorRegistry:
    """Singleton registry for all available connectors."""

    _instance: Optional["ConnectorRegistry"] = None
    _lock = RLock()

    def __new__(cls) -> "ConnectorRegistry":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._registrations: Dict[str, ConnectorRegistration] = {}
        self._connections: Dict[str, BaseConnector] = {}
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "ConnectorRegistry":
        return cls()

    def register(self, connector_class: Type[BaseConnector]) -> None:
        provider = connector_class.__name__.replace("Connector", "").lower()
        dummy_config = ConnectorConfig(
            name=provider,
            provider=provider,
            description="",
            icon="",
            category="",
            auth_type="",
        )
        dummy_auth = ConnectorAuth(provider=provider)
        try:
            instance = connector_class("dummy", dummy_config, dummy_auth)
            metadata = ConnectorMetadata(
                provider=provider,
                class_ref=f"{connector_class.__module__}:{connector_class.__name__}",
                config=instance.config,
                capabilities=instance.get_capabilities() if asyncio.iscoroutinefunction(instance.get_capabilities) else [],
            )
        except Exception:
            metadata = ConnectorMetadata(
                provider=provider,
                class_ref=f"{connector_class.__module__}:{connector_class.__name__}",
                config=dummy_config,
                capabilities=[],
            )
        self._registrations[provider] = ConnectorRegistration(
            metadata=metadata,
            connector_class=connector_class,
        )
        logger.info(f"Registered connector: {provider}")

    def get(self, provider: str) -> Optional[ConnectorRegistration]:
        return self._registrations.get(provider.lower())

    def list_all(self) -> List[ConnectorRegistration]:
        return list(self._registrations.values())

    def list_by_category(self, category: str) -> List[ConnectorRegistration]:
        return [r for r in self._registrations.values() if r.metadata.config.category == category]

    def list_by_tags(self, tags: List[str]) -> List[ConnectorRegistration]:
        return [r for r in self._registrations.values()
                if any(t in r.metadata.config.tags for t in tags)]

    def create_connection(self, provider: str, config: Dict[str, Any]) -> BaseConnector:
        reg = self.get(provider)
        if not reg:
            raise ValueError(f"Unknown connector provider: {provider}")
        connection_id = uuid4()
        auth = ConnectorAuth(
            provider=provider,
            user_id=config.get("user_id"),
            organization_id=config.get("organization_id"),
            scopes=config.get("scopes", []),
            metadata=config.get("auth_metadata", {}),
        )
        connector = reg.connector_class(connection_id, reg.metadata.config, auth)
        self._connections[str(connection_id)] = connector
        return connector

    def get_connection(self, connection_id: str) -> Optional[BaseConnector]:
        return self._connections.get(connection_id)

    def remove_connection(self, connection_id: str) -> bool:
        conn = self._connections.pop(connection_id, None)
        if conn:
            import asyncio
            asyncio.create_task(conn.disconnect())
            return True
        return False

    def get_active_connections(self) -> Dict[str, BaseConnector]:
        return self._connections.copy()

    def clear(self) -> None:
        self._registrations.clear()
        self._connections.clear()


_registry: Optional[ConnectorRegistry] = None


def get_registry() -> ConnectorRegistry:
    global _registry
    if _registry is None:
        _registry = ConnectorRegistry.get_instance()
    return _registry


def register_connector(connector_class: Type[BaseConnector]) -> None:
    get_registry().register(connector_class)


def list_available_connectors(category: Optional[str] = None,
                               tags: Optional[List[str]] = None) -> List[ConnectorRegistration]:
    reg = get_registry()
    if category:
        return reg.list_by_category(category)
    if tags:
        return reg.list_by_tags(tags)
    return reg.list_all()
