# Kea Leases to JSON

A Python tool to convert [ISC Kea](https://kea.readthedocs.io/) DHCP leases files to JSON format.  
Supports both IPv4 and IPv6 leases. Includes a directory watcher for real-time conversion.

## Features

- Converts Kea leases CSV files to JSON
- Handles both IPv4 and IPv6 addresses
- Watches a directory for changes and updates the JSON output automatically
- Command-line interface

## Installation

You can install the latest release from [PyPI](https://pypi.org/project/kea-leases-to-json/):

```bash
pip install kea-leases-to-json
```

Or, to install from source:

```bash
git clone https://github.com/yourusername/kea-leases-to-json.git
cd kea-leases-to-json
pip install .
```

## Usage

After installation, you can use the command-line tool:

```bash
kea-leases-to-json /path/to/kea/leases/dir /path/to/output.json
```

### Options

- `source_dir` (required): Directory containing Kea lease CSV files
- `target_file` (required): Output JSON file path
- `--extension`: File extension to look for (default: `.csv`)
- `--log-level`: Logging level - choices: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `--single-run`: Run once and exit, useful for testing. By default, the script starts a watcher for any file changes
- `--daemonize`: Run the process as a daemon in the background (only works when not in single-run mode)
- `--pid`: PID file path for the daemon process (default: `/var/run/kea_leases_to_json.pid`)

## Example

```bash
kea-leases-to-json \
  ./leases \
  ./leases.json \
  --extension .csv \
  --log-level DEBUG \
  --single-run
```

## CI & Test Coverage

![Test Status](https://github.com/cjuniorfox/kea-leases-to-json/actions/workflows/python-package.yml/badge.svg)
[![codecov](https://codecov.io/gh/cjuniorfox/kea-leases-to-json/graph/badge.svg?token=SC5CRMC3YW)](https://codecov.io/gh/cjuniorfox/kea-leases-to-json)

The test suite is run automatically on every push and pull request using GitHub Actions. Coverage results are uploaded to Codecov and displayed above.

To run tests and check coverage locally:

```sh
pytest --cov=kea_leases_to_json --cov-report=term
```

## License

This project is licensed under the [GNU GPL v3](LICENSE).

## Contributing

Pull requests
 