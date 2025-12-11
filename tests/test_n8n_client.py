"""Tests for N8nClient."""

import json

import pytest
from pytest_httpx import HTTPXMock

from n8n_client import N8nClient, N8nClientError, Workflow, WorkflowNode


@pytest.fixture
def client():
    """Create a test client with mock credentials."""
    return N8nClient(base_url="https://n8n.example.com", api_key="test-api-key")


@pytest.fixture
def sample_workflow_response():
    """Sample workflow response from API."""
    return {
        "id": "abc123",
        "name": "Test Workflow",
        "active": False,
        "nodes": [
            {
                "id": "node-1",
                "name": "Start",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [100, 100],
                "parameters": {},
            }
        ],
        "connections": {},
        "settings": {},
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z",
    }


@pytest.fixture
def sample_workflow_input():
    """Sample workflow input for creation."""
    return {
        "name": "Test Workflow",
        "nodes": [
            {
                "id": "node-1",
                "name": "Start",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [100, 100],
                "parameters": {},
            }
        ],
        "connections": {},
        "settings": {},
    }


class TestCreateWorkflow:
    """Tests for create_workflow method."""

    def test_create_workflow_success(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response, sample_workflow_input
    ):
        """Test successful workflow creation."""
        httpx_mock.add_response(
            method="POST",
            url="https://n8n.example.com/api/v1/workflows",
            json=sample_workflow_response,
            status_code=200,
        )

        result = client.create_workflow(sample_workflow_input)

        assert result["id"] == "abc123"
        assert result["name"] == "Test Workflow"

    def test_create_workflow_with_model(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response
    ):
        """Test creating workflow with Workflow model."""
        httpx_mock.add_response(
            method="POST",
            url="https://n8n.example.com/api/v1/workflows",
            json=sample_workflow_response,
            status_code=200,
        )

        workflow = Workflow(
            name="Test Workflow",
            nodes=[
                WorkflowNode(
                    id="node-1",
                    name="Start",
                    type="n8n-nodes-base.manualTrigger",
                    position=[100, 100],
                )
            ],
        )
        result = client.create_workflow(workflow)

        assert result["id"] == "abc123"

    def test_create_workflow_error(self, client: N8nClient, httpx_mock: HTTPXMock):
        """Test error handling on creation failure."""
        httpx_mock.add_response(
            method="POST",
            url="https://n8n.example.com/api/v1/workflows",
            json={"message": "Validation failed"},
            status_code=400,
        )

        with pytest.raises(N8nClientError) as exc_info:
            client.create_workflow({"name": "Invalid"})

        assert exc_info.value.status_code == 400
        assert "Validation failed" in str(exc_info.value)


class TestGetWorkflow:
    """Tests for get_workflow method."""

    def test_get_workflow_success(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response
    ):
        """Test successful workflow retrieval."""
        httpx_mock.add_response(
            method="GET",
            url="https://n8n.example.com/api/v1/workflows/abc123",
            json=sample_workflow_response,
            status_code=200,
        )

        result = client.get_workflow("abc123")

        assert result["id"] == "abc123"
        assert result["name"] == "Test Workflow"

    def test_get_workflow_not_found(self, client: N8nClient, httpx_mock: HTTPXMock):
        """Test 404 error handling."""
        httpx_mock.add_response(
            method="GET",
            url="https://n8n.example.com/api/v1/workflows/nonexistent",
            json={"message": "Workflow not found"},
            status_code=404,
        )

        with pytest.raises(N8nClientError) as exc_info:
            client.get_workflow("nonexistent")

        assert exc_info.value.status_code == 404


class TestUpdateWorkflow:
    """Tests for update_workflow method."""

    def test_update_workflow_success(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response, sample_workflow_input
    ):
        """Test successful workflow update."""
        updated_response = {**sample_workflow_response, "name": "Updated Workflow"}
        httpx_mock.add_response(
            method="PUT",
            url="https://n8n.example.com/api/v1/workflows/abc123",
            json=updated_response,
            status_code=200,
        )

        result = client.update_workflow("abc123", {**sample_workflow_input, "name": "Updated Workflow"})

        assert result["name"] == "Updated Workflow"


class TestDeleteWorkflow:
    """Tests for delete_workflow method."""

    def test_delete_workflow_success(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response
    ):
        """Test successful workflow deletion."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://n8n.example.com/api/v1/workflows/abc123",
            json=sample_workflow_response,
            status_code=200,
        )

        result = client.delete_workflow("abc123")

        assert result["id"] == "abc123"


class TestListWorkflows:
    """Tests for list_workflows method."""

    def test_list_workflows_success(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response
    ):
        """Test successful workflow listing."""
        httpx_mock.add_response(
            method="GET",
            url="https://n8n.example.com/api/v1/workflows?limit=100",
            json={"data": [sample_workflow_response], "nextCursor": None},
            status_code=200,
        )

        result = client.list_workflows()

        assert len(result.data) == 1
        assert result.data[0].name == "Test Workflow"
        assert result.next_cursor is None

    def test_list_workflows_with_filters(self, client: N8nClient, httpx_mock: HTTPXMock):
        """Test listing with filters."""
        httpx_mock.add_response(
            method="GET",
            url="https://n8n.example.com/api/v1/workflows?limit=50&active=true&name=test",
            json={"data": [], "nextCursor": None},
            status_code=200,
        )

        result = client.list_workflows(active=True, name="test", limit=50)

        assert len(result.data) == 0


class TestActivateDeactivate:
    """Tests for activate/deactivate methods."""

    def test_activate_workflow(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response
    ):
        """Test workflow activation."""
        activated = {**sample_workflow_response, "active": True}
        httpx_mock.add_response(
            method="POST",
            url="https://n8n.example.com/api/v1/workflows/abc123/activate",
            json=activated,
            status_code=200,
        )

        result = client.activate_workflow("abc123")

        assert result["active"] is True

    def test_deactivate_workflow(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response
    ):
        """Test workflow deactivation."""
        httpx_mock.add_response(
            method="POST",
            url="https://n8n.example.com/api/v1/workflows/abc123/deactivate",
            json=sample_workflow_response,
            status_code=200,
        )

        result = client.deactivate_workflow("abc123")

        assert result["active"] is False


class TestFileOperations:
    """Tests for import/export file operations."""

    def test_import_from_file(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response, tmp_path
    ):
        """Test importing workflow from JSON file."""
        httpx_mock.add_response(
            method="POST",
            url="https://n8n.example.com/api/v1/workflows",
            json=sample_workflow_response,
            status_code=200,
        )

        # Create a temp workflow file
        workflow_file = tmp_path / "workflow.json"
        workflow_file.write_text(
            json.dumps(
                {
                    "name": "Test Workflow",
                    "nodes": [],
                    "connections": {},
                    "settings": {},
                }
            )
        )

        result = client.import_from_file(workflow_file)

        assert result["id"] == "abc123"

    def test_export_to_file(
        self, client: N8nClient, httpx_mock: HTTPXMock, sample_workflow_response, tmp_path
    ):
        """Test exporting workflow to JSON file."""
        httpx_mock.add_response(
            method="GET",
            url="https://n8n.example.com/api/v1/workflows/abc123",
            json=sample_workflow_response,
            status_code=200,
        )

        output_file = tmp_path / "exported.json"
        client.export_to_file("abc123", output_file)

        assert output_file.exists()
        exported = json.loads(output_file.read_text())
        assert exported["name"] == "Test Workflow"


class TestCleanWorkflow:
    """Tests for clean_workflow_for_import method."""

    def test_removes_readonly_fields(self):
        """Test that readonly fields are removed."""
        workflow = {
            "id": "abc123",
            "name": "Test",
            "nodes": [],
            "connections": {},
            "settings": {},
            "active": True,
            "createdAt": "2024-01-01",
            "updatedAt": "2024-01-01",
            "versionId": "v1",
        }

        cleaned = N8nClient.clean_workflow_for_import(workflow)

        assert "id" not in cleaned
        assert "active" not in cleaned
        assert "createdAt" not in cleaned
        assert "updatedAt" not in cleaned
        assert "versionId" not in cleaned
        assert cleaned["name"] == "Test"
        assert "nodes" in cleaned


class TestContextManager:
    """Tests for context manager support."""

    def test_context_manager(self):
        """Test using client as context manager."""
        with N8nClient(base_url="https://n8n.example.com", api_key="test") as client:
            assert client is not None
        # Client should be closed after exiting context
