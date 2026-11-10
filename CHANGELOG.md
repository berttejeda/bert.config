# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [7.0.0] - 2026-11-10

### Changed

- **Breaking:** TLS certificates are now verified by default when loading configs over HTTPS.
  Pass `verify_tls=False` to load from a host with a self-signed certificate.
- Accessing a missing key as an attribute now raises `AttributeError` instead of `KeyError`,
  so `hasattr()` and `getattr(config, name, default)` behave as expected.
- A web-hosted config that cannot be retrieved, or is invalid, now aborts when `failfast` is set.
- Only URIs starting with `http://` or `https://` are loaded from the web;
  a local file whose name merely starts with `http` is read from disk.
- `tox` now runs the test suite with `pytest test.py`.

### Added

- Wildcard lookups, e.g. `config.get('section1.*.item1')`, which return a list of matches.
- `properties` attribute, e.g. `config.properties.section1.key1`.
- `req_keys` accepts dot notation, e.g. `req_keys=['section1.key1']`.
- Entries in `external_configs` may be plain URI strings as well as mappings.
- A `pytest` test suite in `test.py`.

### Fixed

- Only the first entry in `external_configs` was merged, and `read()` returned `None`
  when that entry could not be used.
- Calling `read()` more than once on the same `Config` returned `None`.
- Configs referencing each other could recurse forever.
- Any non-empty `req_keys` caused every config to be treated as invalid.
- The "config not found" warning crashed on Python 3.13 (`logger.warn` was removed).
- An HTTP error response was parsed as YAML and returned as a config.
- The `templatized` flag on an external config entry, and the `is_template` options
  on `Config`, were ignored.
- `~` was not expanded in external config paths.
- Crashes on: `Config()` without a `config_file_uri`, empty YAML files,
  a null `external_configs` key, list-shaped configs, and non-string YAML keys.
- `update()` on a loaded config raised `KeyError`.
- `setup.cfg` referenced a non-existent `LICENSE.txt`.

## [6.0.0]

See the [commit history](https://github.com/berttejeda/bert.config/commits/6.0.0) for this and earlier releases.
