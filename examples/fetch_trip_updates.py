"""Fetch live trip updates from the NTA GTFS-RT feed and print a summary.

Usage:
    export NTA_API_KEY=your-key   # from https://developer.nationaltransport.ie/
    uv run python examples/fetch_trip_updates.py

Environment variables:
    NTA_API_KEY: Required. NTA developer API key (sent only as a header).
    NTA_FEED_URL: Optional. Overrides the default TripUpdates feed URL.
"""

import asyncio
import os
import sys
from datetime import UTC, datetime

import aiohttp

from nta_gtfs import GtfsRtClient, TripUpdate

DEFAULT_FEED_URL = "https://api.nationaltransport.ie/gtfsr/v2/TripUpdates"
MAX_TRIPS_SHOWN = 5
MAX_STOPS_PER_TRIP = 3


def _format_timestamp(posix_time: int | None) -> str:
    """Format a POSIX timestamp as a local HH:MM string.

    Args:
        posix_time: POSIX timestamp from the feed, or ``None``.

    Returns:
        Local ``HH:MM`` string, or ``"--:--"`` when the timestamp is absent.
    """
    if posix_time is None:
        return "--:--"
    return datetime.fromtimestamp(posix_time, tz=UTC).astimezone().strftime("%H:%M")


def _print_trip(trip: TripUpdate) -> None:
    """Print a one-trip summary with its first few stop-level updates.

    Args:
        trip: Parsed trip update to summarise.
    """
    direction = trip.direction_id if trip.direction_id is not None else "?"
    print(
        f"Trip {trip.trip_id} | route {trip.route_id} | direction {direction}"
        f" | {len(trip.stop_time_updates)} stop update(s)"
    )
    for stu in trip.stop_time_updates[:MAX_STOPS_PER_TRIP]:
        delay = f"{stu.arrival_delay:+d}s" if stu.arrival_delay is not None else "n/a"
        print(
            f"  stop {stu.stop_id}: arrival {_format_timestamp(stu.arrival_time)}"
            f" (delay {delay})"
        )
    remaining = len(trip.stop_time_updates) - MAX_STOPS_PER_TRIP
    if remaining > 0:
        print(f"  ... and {remaining} more stop(s)")


async def main() -> int:
    """Fetch trip updates from the live feed and print a readable summary.

    Returns:
        Process exit code: ``0`` on success, ``1`` on configuration error.
    """
    api_key = os.environ.get("NTA_API_KEY")
    if not api_key:
        print(
            "Error: the NTA_API_KEY environment variable is not set.\n"
            "Get a key from https://developer.nationaltransport.ie/ and run:\n"
            "  export NTA_API_KEY=your-key",
            file=sys.stderr,
        )
        return 1

    feed_url = os.environ.get("NTA_FEED_URL", DEFAULT_FEED_URL)

    async with aiohttp.ClientSession() as session:
        client = GtfsRtClient(feed_url=feed_url, api_key=api_key, session=session)
        updates = await client.async_fetch_trip_updates()

    print(f"Fetched {len(updates)} trip update(s) from {feed_url}\n")
    for trip in updates[:MAX_TRIPS_SHOWN]:
        _print_trip(trip)
    if len(updates) > MAX_TRIPS_SHOWN:
        print(f"\n... and {len(updates) - MAX_TRIPS_SHOWN} more trip(s) not shown")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
