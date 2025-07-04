import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import tempfile
from kea_leases_to_json import kea_leases_to_json



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