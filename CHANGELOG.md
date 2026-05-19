# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2024-01-01

### Added

- Initial release
- `GtfsRtClient` for fetching real-time GTFS-RT trip updates from NTA feeds
- `StaticGtfsClient` for downloading and querying static GTFS schedule data
- Exception hierarchy: `NtaGtfsError`, `GtfsRtAuthError`, `GtfsRtFetchError`, `GtfsRtParseError`, `StaticGtfsLoadError`
