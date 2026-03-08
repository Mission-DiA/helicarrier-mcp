import json

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
    search: str | None = None,
    status: str | None = None,
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
    app_id: str | None = None,
    repo_name: str | None = None,
    status: str | None = None,
    branch: str | None = None,
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


# ─── AEGIS: Platform Governance Engine ────────────────────────


@mcp.tool()
async def aegis_summary() -> str:
    """Get AEGIS fleet-wide governance snapshot.

    Returns active/mitigating incident counts, pending T2 actions,
    24h scan and test counts, top severity, and affected apps.
    """
    try:
        result = await client.get("/admin/aegis/summary")
        return _json(result)
    except Exception as e:
        return f"Error fetching AEGIS summary: {e}"


@mcp.tool()
async def aegis_list_incidents(
    status: str | None = None,
    app_id: str | None = None,
    env: str | None = None,
    severity: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """List AEGIS incidents (correlated platform issues).

    Filter by status ('active'/'mitigating'/'resolved'), app_id,
    env ('uat'/'production'), or severity ('critical'/'high'/'medium'/'low').
    """
    try:
        result = await client.get(
            "/admin/aegis/incidents",
            params={
                "status": status,
                "app_id": app_id,
                "env": env,
                "severity": severity,
                "page": page,
                "page_size": page_size,
            },
        )
        return _json(result)
    except Exception as e:
        return f"Error listing AEGIS incidents: {e}"


@mcp.tool()
async def aegis_incident_detail(incident_id: str) -> str:
    """Get full detail for an AEGIS incident including related actions.

    Returns incident metadata, signals, activity log, and all actions
    taken for this incident.
    """
    try:
        result = await client.get(f"/admin/aegis/incidents/{incident_id}")
        return _json(result)
    except Exception as e:
        return f"Error fetching incident {incident_id}: {e}"


@mcp.tool()
async def aegis_list_actions(
    status: str | None = None,
    tier: str | None = None,
    app_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """List AEGIS actions (automated responses to incidents).

    Filter by status ('pending'/'approved'/'completed'/'rejected'),
    tier ('T0'/'T1'/'T2'), or app_id. T2 actions require Director approval.
    """
    try:
        result = await client.get(
            "/admin/aegis/actions",
            params={
                "status": status,
                "tier": tier,
                "app_id": app_id,
                "page": page,
                "page_size": page_size,
            },
        )
        return _json(result)
    except Exception as e:
        return f"Error listing AEGIS actions: {e}"


@mcp.tool()
async def aegis_approve_action(action_id: str, reason: str | None = None) -> str:
    """Approve a pending T2 AEGIS action (Director approval).

    T2 actions are high-risk operations like rollback, promote, or escalate.
    Only pending actions can be approved.
    """
    try:
        result = await client.post(
            f"/admin/aegis/actions/{action_id}/approve",
            data={"reason": reason},
        )
        return _json(result)
    except Exception as e:
        return f"Error approving action {action_id}: {e}"


@mcp.tool()
async def aegis_reject_action(action_id: str, reason: str | None = None) -> str:
    """Reject a pending T2 AEGIS action.

    Provide a reason for the rejection. Only pending actions can be rejected.
    """
    try:
        result = await client.post(
            f"/admin/aegis/actions/{action_id}/reject",
            data={"reason": reason},
        )
        return _json(result)
    except Exception as e:
        return f"Error rejecting action {action_id}: {e}"


@mcp.tool()
async def aegis_list_scans(
    app_id: str | None = None,
    limit: int = 20,
) -> str:
    """List AEGIS source code scan results.

    Returns scan metadata, findings summary (critical/high/medium/low counts),
    and commit info. Filter by app_id.
    """
    try:
        result = await client.get(
            "/admin/aegis/scans",
            params={"app_id": app_id, "limit": limit},
        )
        return _json(result)
    except Exception as e:
        return f"Error listing AEGIS scans: {e}"


@mcp.tool()
async def aegis_list_tests(
    app_id: str | None = None,
    test_type: str | None = None,
    limit: int = 20,
) -> str:
    """List AEGIS test results (smoke, contract, integration, walkthrough).

    Filter by app_id or test_type ('api'/'integration'/'walkthrough').
    Returns pass/fail status, duration, and failure details.
    """
    try:
        result = await client.get(
            "/admin/aegis/tests",
            params={"app_id": app_id, "test_type": test_type, "limit": limit},
        )
        return _json(result)
    except Exception as e:
        return f"Error listing AEGIS tests: {e}"


@mcp.tool()
async def aegis_list_fixes(
    app_id: str | None = None,
    limit: int = 20,
) -> str:
    """List AEGIS fix reports (documented fixes applied by the engine).

    Returns what was found, what was fixed, why it matters,
    files changed, and developer acknowledgment status.
    """
    try:
        result = await client.get(
            "/admin/aegis/fixes",
            params={"app_id": app_id, "limit": limit},
        )
        return _json(result)
    except Exception as e:
        return f"Error listing AEGIS fixes: {e}"


@mcp.tool()
async def aegis_app_intel(app_id: str) -> str:
    """Get AEGIS deep intelligence profile for an app.

    Returns identity, features, API endpoints, UI pages, data model,
    connections, deployment info, and user journeys.
    """
    try:
        result = await client.get(f"/admin/aegis/app-intel/{app_id}")
        return _json(result)
    except Exception as e:
        return f"Error fetching AEGIS intel for {app_id}: {e}"


@mcp.tool()
async def aegis_resolve_incident(incident_id: str, resolution: str) -> str:
    """Resolve an AEGIS incident with a resolution note.

    Marks the incident as resolved and records the resolution in the
    activity log.
    """
    try:
        result = await client.post(
            f"/admin/aegis/incidents/{incident_id}/resolve",
            data={"resolution": resolution},
        )
        return _json(result)
    except Exception as e:
        return f"Error resolving incident {incident_id}: {e}"
