import json, csv, os, sys, time, logging

def _read_file(file_name):
    logging.debug(f"Reading file {file_name}.")
    with open(file_name) as f:
        try:
            data = list(csv.DictReader(f))
        except csv.Error as e:
            logging.warning(f"Malformed CSV file {file_name}: {e}. Returning empty data.")
            return []
    
    # Check if the CSV has the required columns
    if data and not all(col in data[0] for col in ['hostname', 'address', 'expire']):
        missing_cols = [col for col in ['hostname', 'address', 'expire'] if col not in data[0]]
        logging.warning(f"Cannot read CSV file {file_name}: missing required columns {missing_cols}. Returning empty data.")
        return []
    
    mapped = []
    for row in data:
        if row['address'] is None or row['address'] == "":
            logging.warning(f"Skipping row in {file_name} due to invalid fields: 'address'")
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
                    if single_run:
                        logging.info("Single run mode enabled. Exiting after initial check.")
                        return
                    time.sleep(5)
                    continue
            # Write the new data to the target file
            logging.info(f"Writing converted data to {target_file}.")
            with open(target_file,"w") as f:
                f.writelines(converted_data)
            if single_run:
                logging.info("Single run mode enabled. Exiting after initial conversion.")
                return
        except PermissionError as e:
            logging.error(f"Permission denied writing to {target_file}: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error writing to {target_file}: {e}")
            raise
        time.sleep(5)

def kea_leases_to_json(source_dir, target_file, log_level = "INFO", extension=".csv", single_run=False):
    if not os.path.isdir(source_dir):
        print(f"Directory {source_dir} does not exist.", file=sys.stderr)
        sys.exit(1)
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(level)

    logging.info(f"Kea to JSON watcher conversion tool. Source:'{source_dir}' to '{target_file}'")
    
    run_watcher(source_dir, target_file, extension, single_run)