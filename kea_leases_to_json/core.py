import json, csv, os, sys, time, logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s %(levelname)s %(message)s'
)

def _read_file(file_name):
    logging.debug(f"Reading file {file_name}.")
    with open(file_name) as f:
        try:
            data = list(csv.DictReader(f))
        except csv.Error as e:
            logging.error(f"Error reading CSV file {file_name}: {e}")
            return []
    mapped = []
    for row in data:
        try:
            if 'hostname' not in row or 'address' not in row or 'expire' not in row:
                logging.warning(f"Skipping row in {file_name} due to missing fields: {row}")
                continue
        except KeyError as e:
            logging.error(f"Missing expected key in row: {e}")
            continue
        address = row['address']
        if ':' in address:
            address_type = "IPv6"
            address_parts = address.split(':')
        else:
            address_type = "IPv4"
            address_parts = address.split('.')
        if len(address_parts) > 0 and len(row["hostname"]) > 0:
            mapped.append({
                "Hostname": row['hostname'].split(".")[0],
                "Address": address_parts,
                "AddressType": address_type,
                "Expire": row['expire']
            })
    logging.debug(f"File {file_name} was read.")
    return mapped

def _convert_directory(path, extension=".csv"):
    logging.debug(f"Scanning directory: '{path}'.")
    results = []
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for f in files:
        if f.endswith(extension):
            logging.debug(f"Processing file: '{f}'.")
            results.extend(_read_file(os.path.join(path, f)))
        else:
            logging.debug(f"Skipping file: '{f}' (not a {extension} file).")
    logging.debug(f"Directory scanned: '{path}'")
    return json.dumps(results)

def run_watcher(source_path, target_file, extension=".csv", single_run=False):
    logging.info(f"Watching directory '{source_path}' for changes.")
    while True:
        converted_data = _convert_directory(source_path, extension)
        try:
            # Check if the converted data is different from the existing file content
            if os.path.exists(target_file):
                with open(target_file, "r") as f:
                    existing_data = f.read()
                if existing_data == converted_data:
                    logging.debug("No changes detected. Skipping write.")
                    time.sleep(5)
                    continue
            # Write the new data to the target file
            logging.info(f"Writing converted data to {target_file}.")
            with open(target_file,"w") as f:
                f.writelines(converted_data)
                if single_run:
                    logging.info("Single run mode enabled. Exiting after initial conversion.")
                    return
        except Exception as e:
            logging.error(f"Error writing to {target_file}: {e}")
        time.sleep(5)

def kea_leases_to_json(source_dir, target_file, log_level = "INFO", extension=".csv", single_run=False):
    if not os.path.isdir(source_dir):
        print(f"Directory {source_dir} does not exist.", file=sys.stderr)
        sys.exit(1)
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(level)

    logging.info(f"Kea to JSON watcher conversion tool. Source:'{source_dir}' to '{target_file}'")
    
    run_watcher(source_dir, target_file, extension, single_run)