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

def test_kea_leases_to_json_ipv4_only():
    """Test conversion with only IPv4 addresses"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "lease_ipv4.csv")
        with open(csv_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "server1.example.com,10.0.0.1,1234567890\n"
                "server2.example.com,172.16.0.100,1234567891\n"
                "server3.example.com,192.168.1.50,1234567892\n"
            )
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name
        
        try:
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)
            
            with open(tmp_json_path) as f:
                data = json.load(f)
                assert len(data) == 3
                
                # Verify first entry
                assert data[0]["Hostname"] == "server1"
                assert data[0]["AddressType"] == "IPv4"
                assert data[0]["Address"] == ["10", "0", "0", "1"]
                assert data[0]["Expire"] == "1234567890"
                
                # Verify second entry
                assert data[1]["Hostname"] == "server2"
                assert data[1]["AddressType"] == "IPv4"
                assert data[1]["Address"] == ["172", "16", "0", "100"]
                assert data[1]["Expire"] == "1234567891"
                
                # Verify third entry
                assert data[2]["Hostname"] == "server3"
                assert data[2]["AddressType"] == "IPv4"
                assert data[2]["Address"] == ["192", "168", "1", "50"]
                assert data[2]["Expire"] == "1234567892"
        finally:
            os.remove(tmp_json_path)

def test_kea_leases_with_custom_extension():
    """Test conversion with custom file extension"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a .txt file with CSV data
        txt_path = os.path.join(tmp_dir, "lease.txt")
        with open(txt_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "custom-host,192.168.100.50,1234567890\n"
            )
        
        # Create a .csv file that should be ignored
        csv_path = os.path.join(tmp_dir, "ignored.csv")
        with open(csv_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "should-not-appear,10.0.0.1,1234567891\n"
            )
        
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name
        
        try:
            # Process only .txt files
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".txt", True)
            
            with open(tmp_json_path) as f:
                data = json.load(f)
                assert len(data) == 1  # Only the .txt file should be processed
                assert data[0]["Hostname"] == "custom-host"
                assert data[0]["Address"] == ["192", "168", "100", "50"]
                assert data[0]["AddressType"] == "IPv4"
        finally:
            os.remove(tmp_json_path)

def test_kea_leases_csv_ignores_other_extensions():
    """Test that only .csv files are processed when extension is .csv"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a valid .csv file
        csv_path = os.path.join(tmp_dir, "valid_lease.csv")
        with open(csv_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "csv-host,192.168.1.10,1234567890\n"
            )
        
        # Create files with other extensions that should be ignored
        txt_path = os.path.join(tmp_dir, "ignore_me.txt")
        with open(txt_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "txt-host,10.0.0.1,1234567891\n"
            )
        
        log_path = os.path.join(tmp_dir, "ignore_me.log")
        with open(log_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "log-host,172.16.0.1,1234567892\n"
            )
        
        dat_path = os.path.join(tmp_dir, "ignore_me.dat")
        with open(dat_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "dat-host,192.168.2.1,1234567893\n"
            )
        
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name
        
        try:
            # Process with default .csv extension
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)
            
            with open(tmp_json_path) as f:
                data = json.load(f)
                assert len(data) == 1  # Only the .csv file should be processed
                assert data[0]["Hostname"] == "csv-host"
                assert data[0]["Address"] == ["192", "168", "1", "10"]
                assert data[0]["AddressType"] == "IPv4"
                
                # Verify that other hosts from non-csv files are NOT present
                hostnames = [item["Hostname"] for item in data]
                assert "txt-host" not in hostnames
                assert "log-host" not in hostnames
                assert "dat-host" not in hostnames
        finally:
            os.remove(tmp_json_path)

def test_kea_leases_nonexistent_directory():
    """Test that function exits with error when source directory doesn't exist"""
    import pytest
    
    nonexistent_dir = "/tmp/this_directory_should_not_exist_12345"
    
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
        tmp_json_path = tmp_json.name
    
    try:
        # Should exit with code 1 when directory doesn't exist
        with pytest.raises(SystemExit) as exc_info:
            kea_leases_to_json(nonexistent_dir, tmp_json_path, "DEBUG", ".csv", True)
        
        assert exc_info.value.code == 1
    finally:
        if os.path.exists(tmp_json_path):
            os.remove(tmp_json_path)

def test_kea_leases_no_write_permission():
    """Test that PermissionError is logged and raised when target file has no write permission"""
    import pytest
    import logging
    from unittest.mock import patch
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "lease.csv")
        with open(csv_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "test-host,192.168.1.1,1234567890\n"
            )
        
        # Create a read-only directory for the output file
        readonly_dir = os.path.join(tmp_dir, "readonly")
        os.makedirs(readonly_dir, mode=0o444)
        target_file = os.path.join(readonly_dir, "output.json")
        
        try:
            with patch('logging.error') as mock_error:
                # Run in single mode and expect PermissionError to be raised
                with pytest.raises(PermissionError):
                    kea_leases_to_json(tmp_dir, target_file, "DEBUG", ".csv", True)
                
                # Verify that logging.error was called before exception was raised
                assert mock_error.called, "logging.error should have been called"
                error_call = str(mock_error.call_args)
                assert "Permission denied writing to" in error_call
                assert target_file in error_call
        finally:
            # Restore write permissions for cleanup
            os.chmod(readonly_dir, 0o755)
            if os.path.exists(readonly_dir):
                os.rmdir(readonly_dir)

def test_csv_error_handling_logs_and_continues():
    """Test that csv.Error is caught, logged, and doesn't raise an exception"""
    import logging
    from unittest.mock import patch, mock_open
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "malformed.csv")
        # Create a file that will trigger csv.Error when read
        with open(csv_path, "w") as f:
            f.write("hostname,address,expire\n")
            f.write('"unclosed quote field\n')
        
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name
        
        try:
            # Capture log output
            with patch('logging.warning') as mock_warning:
                # This should not raise an exception, just log the error
                kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)
                
                # Verify that logging.warning was called with the csv.Error message
                assert mock_warning.called, "logging.warning should have been called"
                warning_call = str(mock_warning.call_args)
                assert "Skipping row" in warning_call
                assert "due to invalid fields: 'address'" in warning_call
            
            # Verify the JSON file was still created (even if empty or partial)
            with open(tmp_json_path) as f:
                data = json.load(f)
                # The function should continue and return empty list for the bad file
                assert isinstance(data, list)
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
            time.sleep(7)  # Allow time for the watcher to process the change
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

def test_single_run_no_changes_exits():
    """Test that single-run mode exits when no changes are detected"""
    from unittest.mock import patch
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "lease.csv")
        with open(csv_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "test-host,192.168.1.1,1234567890\n"
            )
        
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name
        
        try:
            # First run: create the initial JSON file
            kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)
            
            # Verify file was created
            assert os.path.exists(tmp_json_path)
            
            # Second run: with same data, should detect no changes and exit
            with patch('logging.info') as mock_info, patch('logging.debug') as mock_debug:
                kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", True)
                
                # Verify that debug log was called with "No changes detected"
                debug_calls = [str(call) for call in mock_debug.call_args_list]
                no_changes_logged = any("No changes detected" in call for call in debug_calls)
                assert no_changes_logged, "logging.debug should have been called with 'No changes detected'"
                
                # Verify that info log was called with single run exit message
                info_calls = [str(call) for call in mock_info.call_args_list]
                single_run_exit = any("Single run mode enabled. Exiting after initial check." in call for call in info_calls)
                assert single_run_exit, "logging.info should have been called with single run exit message"
        finally:
            if os.path.exists(tmp_json_path):
                os.remove(tmp_json_path)

def test_no_changes_detected_debug_log():
    """Test that 'No changes detected' debug message is logged when file hasn't changed"""
    from unittest.mock import patch
    
    def watch_for_no_changes(tmp_dir, tmp_json_path):
        kea_leases_to_json(tmp_dir, tmp_json_path, "DEBUG", ".csv", False)
        time.sleep(2)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "lease.csv")
        with open(csv_path, "w") as f:
            f.write(
                "hostname,address,expire\n"
                "test-host,192.168.1.1,1234567890\n"
            )
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_json:
            tmp_json_path = tmp_json.name
        
        try:
            with patch('logging.debug') as mock_debug:
                watcher_thread = threading.Thread(target=watch_for_no_changes, args=(tmp_dir, tmp_json_path))
                watcher_thread.start()
                time.sleep(8)  # Wait 8 seconds to allow multiple checks without changes
                
                # Send KeyboardInterrupt to stop the watcher
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(watcher_thread.ident),
                    ctypes.py_object(KeyboardInterrupt)
                )
                watcher_thread.join(timeout=2)
                
                # Verify that logging.debug was called with "No changes detected"
                debug_calls = [str(call) for call in mock_debug.call_args_list]
                no_changes_logged = any("No changes detected" in call for call in debug_calls)
                assert no_changes_logged, "logging.debug should have been called with 'No changes detected'"
        finally:
            if os.path.exists(tmp_json_path):
                os.remove(tmp_json_path)
            