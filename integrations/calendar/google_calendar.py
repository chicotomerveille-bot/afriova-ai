"""
Google Calendar Connector
"""

import logging
from typing import Dict, List, Optional, Any
from integrations.base import OAuth2Connector, ConnectorConfig, ConnectorAuth, ConnectorCapability, ConnectorAction, ConnectorStatus, SyncResult

logger = logging.getLogger(__name__)


class GoogleCalendarConnector(OAuth2Connector):
    """Google Calendar OAuth2 connector."""

    def __init__(self, connection_id: str, config: ConnectorConfig, auth: ConnectorAuth):
        config = ConnectorConfig(
            name="Google Calendar",
            provider="google_calendar",
            description="Google Calendar integration for event management",
            icon="calendar",
            category="calendar",
            auth_type="oauth2",
            scopes=["https://www.googleapis.com/auth/calendar"],
            base_url="https://www.googleapis.com/calendar/v3",
            auth_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            tags=["calendar", "google", "google-workspace"],
        )
        super().__init__(connection_id, config, auth)

    @property
    def provider(self) -> str:
        return "google_calendar"

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

    async def create_event(self, summary: str, start: str, end: str, attendees: Optional[List[str]] = None) -> Dict[str, Any]:
        return {"id": f"event_{id(self)}", "status": "created", "summary": summary}

    async def list_events(self, calendar_id: str = "primary", time_min: Optional[str] = None, time_max: Optional[str] = None) -> Dict[str, Any]:
        return {"items": []}

    async def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": event_id, "updated": True}

    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        return {"id": event_id, "deleted": True}

    async def get_schema(self) -> Dict[str, Any]:
        return {"entities": {"event": {"fields": ["id", "summary", "start", "end", "attendees", "description"]}}}

    async def list_actions(self) -> List[ConnectorAction]:
        return [
            ConnectorAction(
                name="create_event",
                description="Create a calendar event",
                params={
                    "summary": {"type": "string", "required": True},
                    "start": {"type": "string", "required": True},
                    "end": {"type": "string", "required": True},
                    "attendees": {"type": "array", "required": False},
                },
                output_schema={"id": "string"},
            ),
        ]

    async def sync_inbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def sync_outbound(self, entity_types=None, limit=1000) -> SyncResult:
        return SyncResult(success=True, items_synced=0)

    async def run_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action_name == "create_event":
            return await self.create_event(params["summary"], params["start"], params["end"], params.get("attendees"))
        raise ValueError(f"Unknown action: {action_name}")
