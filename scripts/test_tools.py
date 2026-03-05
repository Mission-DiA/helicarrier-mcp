"""Manual smoke test — run each tool and print results."""

import asyncio

from helicarrier_mcp.server import (
    build_status,
    cost_summary,
    fleet_app_detail,
    fleet_health_summary,
    fleet_list_apps,
)


async def main() -> None:
    print("=== fleet_list_apps ===")
    print(await fleet_list_apps(page_size=3))

    print("\n=== fleet_health_summary ===")
    print(await fleet_health_summary())

    print("\n=== fleet_app_detail (nexus-okr) ===")
    print(await fleet_app_detail("nexus-okr"))

    print("\n=== build_status (last 3) ===")
    print(await build_status(page_size=3))

    print("\n=== cost_summary (7 days) ===")
    print(await cost_summary(days=7))


if __name__ == "__main__":
    asyncio.run(main())
