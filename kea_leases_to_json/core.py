import json, csv, os, sys, time, logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DirChangeHandler(FileSystemEventHandler):
    def __init__(self, source_dir, target_file, extension=".csv"):
        self.source_dir = source_dir
        self.target_file = target_file
        self.extension = extension
        logging.debug(f"DirChangeHandler initialized with source: {source_dir}, target: {target_file}, extension: {extension}")

    def on_any_event(self, event):
        if event.event_type  in ("created", "modified", "deleted"):
            logging.debug(f"Event {event.event_type} trigged.")
            # Only act on file changes, not directory events
            if not event.is_directory:
                converted_data = _convert_directory(self.source_dir, self.extension)
                try:
                    logging.info(f"Writing converted data to {self.target_file}.")
                    with open(self.target_file,"w") as f:
                        f.writelines(converted_data)
                except Exception as e:
                    logging.error(f"Error writing to {self.target_file}: {e}")

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

def kea_leases_to_json(source_dir, target_file, log_level = "INFO", extension=".csv", single_run=False):
    if not os.path.isdir(source_dir):
        print(f"Directory {source_dir} does not exist.", file=sys.stderr)
        sys.exit(1)
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(level)

    logging.info(f"Kea to JSON watcher conversion tool. Source:'{source_dir}' to '{target_file}'")
    # Initial run: write output
    converted_data = _convert_directory(source_dir,extension)
    with open(target_file, "w") as f:
        f.write(converted_data)
    # Set up watchdog
    if single_run:
        logging.info("Single run mode enabled. Exiting after initial conversion.")
        return
    logging.info(f"Watching directory '{source_dir}' for changes.")
    event_handler = DirChangeHandler(source_dir, target_file, extension)
    observer = Observer()
    observer.schedule(event_handler, source_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()