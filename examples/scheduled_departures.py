"""Load the NTA static GTFS schedule and print departures for a stop.

Usage:
    uv run python examples/scheduled_departures.py 8250DB001234 46A --direction 0

The static GTFS zip is large (tens of MB); the first load takes a while.

Environment variables:
    NTA_STATIC_GTFS_URL: Optional. Overrides the default static GTFS zip URL.
"""

import argparse
import asyncio
import os
import sys
from datetime import date

import aiohttp

from nta_gtfs import StaticGtfsClient

DEFAULT_STATIC_URL = "https://www.transportforireland.ie/transitData/Data/GTFS_All.zip"


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the scheduled departures query.

    Returns:
        Parsed arguments namespace with ``stop_id``, ``route_id``,
        ``direction``, ``operator`` and ``date`` attributes.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Download the NTA static GTFS schedule and print scheduled "
            "departures for a stop and route."
        ),
        epilog=(
            "Example: uv run python examples/scheduled_departures.py "
            "8250DB001234 46A --direction 0"
        ),
    )
    parser.add_argument("stop_id", help="GTFS stop ID, e.g. 8250DB001234")
    parser.add_argument("route_id", help="route short name, e.g. 46A")
    parser.add_argument(
        "--direction",
        type=int,
        choices=(0, 1),
        default=None,
        help="GTFS direction_id filter (0 or 1); omit for both directions",
    )
    parser.add_argument(
        "--operator",
        default=None,
        help="GTFS agency ID filter; omit for all operators",
    )
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="date to query (default: today)",
    )
    return parser.parse_args()


async def main() -> int:
    """Load the static GTFS feed and print departures for the requested stop.

    Returns:
        Process exit code: ``0`` on success (including no matches found).
    """
    args = _parse_args()
    static_url = os.environ.get("NTA_STATIC_GTFS_URL", DEFAULT_STATIC_URL)
    target_date = args.date if args.date is not None else date.today()

    print(f"Downloading and parsing static GTFS from {static_url} ...")
    async with aiohttp.ClientSession() as session:
        client = StaticGtfsClient(static_gtfs_url=static_url, session=session)
        await client.async_load()

    departures = client.get_scheduled_departures(
        stop_id=args.stop_id,
        route_id=args.route_id,
        direction_id=args.direction,
        operator_id=args.operator,
        target_date=target_date,
    )

    if not departures:
        print(
            f"No departures found for stop {args.stop_id}, route {args.route_id} "
            f"on {target_date.isoformat()}."
        )
        return 0

    print(
        f"\n{len(departures)} departure(s) for stop {args.stop_id}, "
        f"route {args.route_id} on {target_date.isoformat()}:\n"
    )
    for dep in departures:
        print(f"  {dep.departure_time}  route {dep.route_name}  trip {dep.trip_id}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
