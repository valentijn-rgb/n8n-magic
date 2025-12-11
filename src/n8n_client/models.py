"""Pydantic models for n8n workflow API."""

from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class N8nSettings(BaseSettings):
    """Settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    n8n_host: str = Field(alias="N8N_host")
    n8n_api_key: str = Field(alias="N8N_API_KEY")

    @property
    def base_url(self) -> str:
        """Return the base URL with trailing slash removed."""
        return self.n8n_host.rstrip("/")


class NodeConnection(BaseModel):
    """A connection to another node."""

    node: str
    type: str = "main"
    index: int = 0


class WorkflowNode(BaseModel):
    """A node in an n8n workflow."""

    id: str
    name: str
    type: str
    type_version: float = Field(alias="typeVersion", default=1)
    position: list[float]
    parameters: dict[str, Any] = Field(default_factory=dict)
    credentials: dict[str, Any] | None = None

    model_config = {"populate_by_name": True}


class WorkflowSettings(BaseModel):
    """Workflow settings."""

    timeout_hours: int | None = Field(alias="timeoutHours", default=None)
    error_workflow: str | None = Field(alias="errorWorkflow", default=None)
    save_manual_executions: bool | None = Field(alias="saveManualExecutions", default=None)

    model_config = {"populate_by_name": True}


class Workflow(BaseModel):
    """An n8n workflow."""

    name: str
    nodes: list[WorkflowNode] = Field(default_factory=list)
    connections: dict[str, dict[str, list[list[NodeConnection]]]] = Field(default_factory=dict)
    settings: WorkflowSettings = Field(default_factory=WorkflowSettings)

    # Read-only fields (returned by API, not sent on create/update)
    id: str | None = None
    active: bool | None = None
    created_at: str | None = Field(alias="createdAt", default=None)
    updated_at: str | None = Field(alias="updatedAt", default=None)
    version_id: str | None = Field(alias="versionId", default=None)

    model_config = {"populate_by_name": True}

    def to_create_payload(self) -> dict[str, Any]:
        """Return payload suitable for workflow creation (excludes read-only fields)."""
        return {
            "name": self.name,
            "nodes": [node.model_dump(by_alias=True, exclude_none=True) for node in self.nodes],
            "connections": self.connections,
            "settings": self.settings.model_dump(by_alias=True, exclude_none=True),
        }


class WorkflowListResponse(BaseModel):
    """Response from listing workflows."""

    data: list[Workflow]
    next_cursor: str | None = Field(alias="nextCursor", default=None)

    model_config = {"populate_by_name": True}
