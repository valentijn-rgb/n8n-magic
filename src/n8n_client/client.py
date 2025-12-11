"""n8n API client for workflow management."""

import json
from pathlib import Path
from typing import Any

import httpx

from .models import N8nSettings, Workflow, WorkflowListResponse


class N8nClientError(Exception):
    """Base exception for N8nClient errors."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class N8nClient:
    """Client for interacting with the n8n REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize the n8n client.

        Args:
            base_url: n8n instance URL. If not provided, reads from N8N_host env var.
            api_key: API key for authentication. If not provided, reads from N8N_API_KEY env var.
            timeout: Request timeout in seconds.
        """
        if base_url is None or api_key is None:
            settings = N8nSettings()
            base_url = base_url or settings.base_url
            api_key = api_key or settings.n8n_api_key

        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
        self._client = httpx.Client(
            headers={
                "X-N8N-API-KEY": api_key,
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise on errors."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"raw": response.text}

        if response.status_code >= 400:
            message = data.get("message", f"HTTP {response.status_code}")
            raise N8nClientError(message, response.status_code, data)

        return data

    # --- Workflow CRUD ---

    def create_workflow(self, workflow: dict[str, Any] | Workflow) -> dict[str, Any]:
        """Create a new workflow.

        Args:
            workflow: Workflow definition as dict or Workflow model.
                      Must include: name, nodes, connections.
                      Should NOT include: id, active, createdAt, updatedAt.

        Returns:
            Created workflow including assigned id.
        """
        if isinstance(workflow, Workflow):
            payload = workflow.to_create_payload()
        else:
            payload = self.clean_workflow_for_import(workflow)

        response = self._client.post(f"{self.api_url}/workflows", json=payload)
        return self._handle_response(response)

    def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Get a workflow by ID.

        Args:
            workflow_id: The workflow ID.

        Returns:
            Complete workflow definition.
        """
        response = self._client.get(f"{self.api_url}/workflows/{workflow_id}")
        return self._handle_response(response)

    def update_workflow(self, workflow_id: str, workflow: dict[str, Any] | Workflow) -> dict[str, Any]:
        """Update an existing workflow.

        Args:
            workflow_id: The workflow ID to update.
            workflow: New workflow definition.

        Returns:
            Updated workflow.
        """
        if isinstance(workflow, Workflow):
            payload = workflow.to_create_payload()
        else:
            payload = self.clean_workflow_for_import(workflow)

        response = self._client.put(f"{self.api_url}/workflows/{workflow_id}", json=payload)
        return self._handle_response(response)

    def delete_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Delete a workflow.

        Args:
            workflow_id: The workflow ID to delete.

        Returns:
            Deleted workflow data.
        """
        response = self._client.delete(f"{self.api_url}/workflows/{workflow_id}")
        return self._handle_response(response)

    def list_workflows(
        self,
        active: bool | None = None,
        tags: list[str] | None = None,
        name: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> WorkflowListResponse:
        """List workflows with optional filters.

        Args:
            active: Filter by active status.
            tags: Filter by tags.
            name: Filter by name (partial match).
            limit: Max results per page (max 250).
            cursor: Pagination cursor.

        Returns:
            WorkflowListResponse with data and nextCursor.
        """
        params: dict[str, Any] = {"limit": min(limit, 250)}
        if active is not None:
            params["active"] = str(active).lower()
        if tags:
            params["tags"] = ",".join(tags)
        if name:
            params["name"] = name
        if cursor:
            params["cursor"] = cursor

        response = self._client.get(f"{self.api_url}/workflows", params=params)
        data = self._handle_response(response)
        return WorkflowListResponse(**data)

    # --- Workflow State ---

    def activate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Activate a workflow.

        Args:
            workflow_id: The workflow ID.

        Returns:
            Updated workflow.
        """
        response = self._client.post(f"{self.api_url}/workflows/{workflow_id}/activate")
        return self._handle_response(response)

    def deactivate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Deactivate a workflow.

        Args:
            workflow_id: The workflow ID.

        Returns:
            Updated workflow.
        """
        response = self._client.post(f"{self.api_url}/workflows/{workflow_id}/deactivate")
        return self._handle_response(response)

    # --- Convenience Methods ---

    def import_from_file(self, filepath: str | Path) -> dict[str, Any]:
        """Import a workflow from a JSON file.

        Args:
            filepath: Path to the JSON file.

        Returns:
            Created workflow.
        """
        filepath = Path(filepath)
        with open(filepath) as f:
            workflow = json.load(f)
        return self.create_workflow(workflow)

    def export_to_file(self, workflow_id: str, filepath: str | Path) -> None:
        """Export a workflow to a JSON file.

        Args:
            workflow_id: The workflow ID.
            filepath: Destination path for the JSON file.
        """
        workflow = self.get_workflow(workflow_id)
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(workflow, f, indent=2)

    @staticmethod
    def clean_workflow_for_import(workflow: dict[str, Any]) -> dict[str, Any]:
        """Remove read-only fields from a workflow dict before import.

        The n8n API rejects workflows with id, active, createdAt, etc.
        This method strips those fields.

        Args:
            workflow: Raw workflow dict (e.g., from export).

        Returns:
            Cleaned workflow ready for create/update.
        """
        readonly_fields = {"id", "active", "createdAt", "updatedAt", "versionId", "state"}
        return {k: v for k, v in workflow.items() if k not in readonly_fields}
