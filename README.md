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
kea-leases-to-json --source /path/to/kea/leases/dir --target /path/to/output.json
```

### Options

- `--source` (required): Directory containing Kea lease CSV files
- `--target` (required): Output JSON file path
- `--log-level`: Logging level (default: INFO)
- `--extension`: The extension for the file. Defaults to `.csv` 
- `--single-run`: As defaults, this script starts a watcher for any file change. With this parameter, runs once and exits out.

## Example

```bash
kea-leases-to-json \
  --source ./leases \
  --target ./leases.json \
  --log-level DEBUG \
  --extension .csv \
  --single-run
```

## License

This project is licensed under the [GNU GPL v3](LICENSE).

## Contributing

Pull requests