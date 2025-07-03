import argparse
from kea_leases_to_json.core import kea_leases_to_json

def main():
    parser = argparse.ArgumentParser(description="Convert kea leases to JSON")
    parser.add_argument("source_dir", help="Directory path containing kea files")
    parser.add_argument("target_file", help="Target file")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    kea_leases_to_json(args.source_dir,args.target_file,args.log_level.upper())
