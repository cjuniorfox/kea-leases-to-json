import os
import sys
import ctypes
import json
import tempfile
from kea_leases_to_json import kea_leases_to_json
import threading
import time



def test_kea_leases_to_json_ipv4_and_ipv6():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "lease.csv")
        with open(csv_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "host1,192.168.1.10,1234567890\n"
                "host2,2001:db8::1,1234567891\n"
            )
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name
                    

        try:
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)

            with open(tmp_json_path) as f:
                data = json.load(f)
                assert len(data) == 2
                assert data[0]["Hostname"] == "host1"
                assert data[0]["AddressType"] == "IPv4"
                assert data[0]["Address"] == ["192", "168", "1", "10"]
                assert data[1]["Hostname"] == "host2"
                assert data[1]["Address"] == ["2001", "db8", "", "1"]
                assert data[1]["AddressType"] == "IPv6"
        finally:
            os.remove(tmp_json_path)

def test_kea_leases_to_json_no_files():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name

        try:
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)

            with open(tmp_json_path) as f:
                data = json.load(f)
                assert data == []
        finally:
            os.remove(tmp_json_path)

def test_kea_leases_to_json_invalid_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "invalid_lease.csv")
        with open(csv_path, "w") as f:
            f.write("invalid,csv\ninvalid,content\n")

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name

        try:
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)
            
            with open(tmp_json_path) as f:
                data = json.load(f)
                assert len(data) == 0  # Invalid address should not be processed
        finally:
            os.remove(tmp_json_path)

def test_kea_leases_to_json_empty_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name

        try:
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)

            with open(tmp_json_path) as f:
                data = json.load(f)
                assert data == []  # No files should result in empty JSON
        finally:
            os.remove(tmp_json_path)

def test_kea_leases_with_invalid_csv_format():
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "invalid_format.csv")
        with open(csv_path, "w") as f:
            f.write("hthisisnotacsv\nsomerandomfile")  # Missing 'address' field
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name
        
        try:
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)
            
            with open(tmp_json_path) as f:
                data = json.load(f)
                assert len(data) == 0  # Invalid format should not produce any output
        finally:
            os.remove(tmp_json_path)

def test_should_watch_for_file_changes():

    def watch_for_changes(tmp_dir, tmp_json_path):
        kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", False)
        time.sleep(2)

    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "lease.csv")
        with open(csv_path, "w") as f:
            f.write("hostname,address,expire\n")
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name

        try:
            watcher_thread = threading.Thread(target=watch_for_changes, args=(tmp_dir, tmp_json_path))
            watcher_thread.start()
            time.sleep(1)  # Allow the watcher to start

            # Modify the CSV file
            with open(csv_path, "a") as f:
                f.write("host3,2001:db8::2,1234567892\n")
            time.sleep(2)  # Allow time for the watcher to process the change
            # Send KeyboardInterrupt to stop the watcher
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(watcher_thread.ident),
                ctypes.py_object(KeyboardInterrupt)
            )            
            with open(tmp_json_path) as f:
                data = json.load(f)
                assert len(data) == 1  # Only one valid entry should be processed
                assert data[0]["Hostname"] == "host3"
                assert data[0]["AddressType"] == "IPv6"
                assert data[0]["Address"] == ["2001", "db8", "", "2"]
        except Exception as e:
            print(f"Test failed with exception: {e}", file=sys.stderr)
            raise
        finally:
            os.remove(tmp_json_path)
            