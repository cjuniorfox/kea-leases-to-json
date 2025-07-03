import os
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
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG")
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