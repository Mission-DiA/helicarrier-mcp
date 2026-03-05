import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from helicarrier_mcp.auth import fetch_api_key
from helicarrier_mcp.client import HelicarrierClient
from helicarrier_mcp.config import config

mcp = FastMCP("helicarrier")

# Fetch API key once at startup (fails fast if unavailable)
api_key = fetch_api_key(config.gcp_project, config.secret_name)
client = HelicarrierClient(config.api_url, api_key)


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


@mcp.tool()
async def fleet_list_apps(
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """List all apps in the Helicarrier fleet.

    Returns app names, statuses, owners, and usage stats.
    Use search to filter by name, status to filter by 'active' or 'inactive'.
    """
    try:
        result = await client.get(
            "/admin/apps",
            params={
                "page": page,
                "page_size": page_size,
                "search": search,
                "status": status,
            },
        )
        return _json(result)
    except Exception as e:
        return f"Error listing apps: {e}"


@mcp.tool()
async def fleet_health_summary() -> str:
    """Get fleet-wide endpoint health summary across UAT and Production.

    Returns healthy/unhealthy/unreachable counts per environment
    and last sweep timestamp.
    """
    try:
        result = await client.get("/admin/endpoint-health/summary")
        return _json(result)
    except Exception as e:
        return f"Error fetching health summary: {e}"


@mcp.tool()
async def fleet_app_detail(app_id: str) -> str:
    """Get detailed intelligence profile for a specific app.

    Returns infrastructure details (framework, language, SDK version,
    auth method, deployment model) and metadata coverage.
    """
    try:
        result = await client.get(f"/admin/intel/profile/{app_id}")
        return _json(result)
    except Exception as e:
        return f"Error fetching app detail for '{app_id}': {e}"


@mcp.tool()
async def build_status(
    app_id: Optional[str] = None,
    repo_name: Optional[str] = None,
    status: Optional[str] = None,
    branch: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Get Cloud Build history for the fleet.

    Filter by app_id, repo_name, status ('success'/'failure'/'in_progress'),
    or branch. Returns build ID, repo, branch, status, duration, and timestamps.
    """
    try:
        result = await client.get(
            "/admin/builds",
            params={
                "app_id": app_id,
                "repo_name": repo_name,
                "status": status,
                "branch": branch,
                "page": page,
                "page_size": page_size,
            },
        )
        return _json(result)
    except Exception as e:
        return f"Error fetching builds: {e}"


@mcp.tool()
async def cost_summary(days: int = 30) -> str:
    """Get fleet cost summary from GCP billing.

    Returns total fleet cost, per-app breakdown with percentages,
    and shared infrastructure costs. Days parameter controls the lookback
    period (1-365, default 30).
    """
    try:
        result = await client.get(
            "/admin/costs/summary",
            params={"days": days},
        )
        return _json(result)
    except Exception as e:
        return f"Error fetching cost summary: {e}"
