# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - 2026-07-12

### Added

- `StaticGtfsClient` accepts an optional `stop_ids` collection; when given, only
  `stop_times.txt` rows for those stops are indexed, cutting peak memory roughly
  17x on a large feed (#20)

### Changed

- `StaticGtfsClient.async_load` now streams the zip download to an anonymous
  temporary file in 1 MiB chunks and parses each CSV row-by-row instead of
  holding the archive and all parsed rows in memory; peak RSS on a large feed
  drops ~2.3x even without a stop filter (#20)
- After parsing, only trips referenced by the departure index are retained

## [0.1.0] - 2026-07-11

### Added

- Initial release
- `GtfsRtClient` for fetching real-time GTFS-RT trip updates from NTA feeds
- `StaticGtfsClient` for downloading and querying static GTFS schedule data
- Exception hierarchy: `NtaGtfsError`, `GtfsRtAuthError`, `GtfsRtFetchError`, `GtfsRtParseError`, `StaticGtfsLoadError`
