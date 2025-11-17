import argparse
import kea_leases_to_json

def main():
    parser = argparse.ArgumentParser(description="Convert kea leases to JSON")
    parser.add_argument("source_dir", help="Directory path containing kea files")
    parser.add_argument("target_file", help="Target file")
    parser.add_argument(
        "--extension",
        default=".csv",
        help="File extension to look for (default: .csv)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)"
    )
    parser.add_argument(
        "--single-run",
        action="store_true",
        default=False,
        help="Run once and exit, useful for testing"
    )
    parser.add_argument(
        "--daemonize",
        action="store_true",
        default=False,
        help="Run the process as a daemon in the background, only if not in single-run mode"
    )
    parser.add_argument(
        "--pid",
        help="PID file path for the daemon process",
        default="/var/run/kea_leases_to_json.pid"
    )
    parser.add_argument(
        "--version", 
        "-v",
        action='version', 
        version=f'kea_leases_to_json {kea_leases_to_json.get_version()}', 
        help="Show version and exit"
    )
    
    args = parser.parse_args()
    if args.daemonize and not args.single_run:
        from daemonize import Daemonize
        cmd = lambda: kea_leases_to_json(
                source_dir= args.source_dir,
                target_file= args.target_file,
                log_level= args.log_level.upper(),
                extension= args.extension,
                single_run= args.single_run
            )
        daemon = Daemonize(
            app="kea_leases_to_json",
            pid=args.pid,
            action=cmd
        )
        daemon.start()
    else:
        kea_leases_to_json.kea_leases_to_json(
            source_dir= args.source_dir,
            target_file= args.target_file,
            log_level= args.log_level.upper(),
            extension= args.extension,
            single_run= args.single_run
        )