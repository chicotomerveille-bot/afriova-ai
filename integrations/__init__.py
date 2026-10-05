"""
Afriova AI - Connectors Framework (MCP-like)

Unified interface for connecting to all enterprise tools.
Supports OAuth2, API keys, and various authentication methods.
"""

from integrations.base import (
    BaseConnector,
    OAuth2Connector,
    APIKeyConnector,
    ConnectorConfig,
    ConnectorAuth,
    ConnectorAction,
    ConnectorCapability,
    ConnectorStatus,
    OAuth2Token,
    ConnectionResult,
    SyncResult,
)
from integrations.registry import (
    ConnectorRegistry,
    get_registry,
    register_connector,
    list_available_connectors,
)

__all__ = [
    "BaseConnector",
    "OAuth2Connector",
    "APIKeyConnector",
    "ConnectorConfig",
    "ConnectorAuth",
    "ConnectorAction",
    "ConnectorCapability",
    "ConnectorStatus",
    "OAuth2Token",
    "ConnectionResult",
    "SyncResult",
    "ConnectorRegistry",
    "get_registry",
    "register_connector",
    "list_available_connectors",
]