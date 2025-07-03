import json, csv, os, sys, time, logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DirChangeHandler(FileSystemEventHandler):
    def __init__(self, source_dir, target_file):
        self.source_dir = source_dir
        self.target_file = target_file

    def on_any_event(self, event):
        if event.event_type  in ("created", "modified", "deleted"):
            logging.debug(f"Event {event.event_type} trigged.")
            # Only act on file changes, not directory events
            if not event.is_directory:
                converted_data = _convert_directory(self.source_dir)
                with open(self.target_file,"w") as f:
                    f.writelines(converted_data)


logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s %(levelname)s %(message)s'
)

def _read_file(file_name):
    logging.debug(f"Reading file {file_name}.")
    with open(file_name) as f:
        data = list(csv.DictReader(f))
    mapped = []
    for row in data:
        address = row['address']
        if ':' in address:
            address_type = "IPv6"
            address_parts = address.split(':')
        else:
            address_type = "IPv4"
            address_parts = address.split('.')
        mapped.append({
            "Hostname": row['hostname'].split(".")[0],
            "Address": address_parts,
            "AddressType": address_type,
            "Expire": row['expire']
        })
    logging.debug(f"File {file_name} was read.")
    return mapped

def _convert_directory(path):
    logging.debug(f"Scanning directory: '{path}'.")
    results = []
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for f in files:
        results.extend(_read_file(os.path.join(path, f)))
    logging.debug(f"Directory scanned: '{path}'")
    return json.dumps(results)

def kea_leases_to_json(source_dir, target_file, log_level = "INFO"):
    if not os.path.isdir(source_dir):
        print(f"Directory {source_dir} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    logging.getLogger().setLevel(log_level)
    logging.info(f"Kea to JSON watcher conversion tool. Source:'{source_dir}' to '{target_file}'")
    # Initial run: write output
    converted_data = _convert_directory(source_dir)
    with open(target_file, "w") as f:
        f.write(converted_data)
    # Set up watchdog
    event_handler = DirChangeHandler(source_dir, target_file)
    observer = Observer()
    observer.schedule(event_handler, source_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()