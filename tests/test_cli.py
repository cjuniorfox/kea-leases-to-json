import os
import sys
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from kea_leases_to_json.cli import main


def test_cli_basic_execution(tmp_path):
    """Test basic CLI execution with required arguments"""
    csv_file = tmp_path / "lease.csv"
    csv_file.write_text(
        "hostname,address,expire\n"
        "test-host,192.168.1.100,1234567890\n"
    )
    
    output_file = tmp_path / "output.json"
    
    test_args = [
        "kea-leases-to-json",
        str(tmp_path),
        str(output_file),
        "--single-run"
    ]
    
    with patch.object(sys, 'argv', test_args):
        main()
    
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["Hostname"] == "test-host"


def test_cli_with_extension_argument(tmp_path):
    """Test CLI with custom file extension"""
    lease_file = tmp_path / "lease.txt"
    lease_file.write_text(
        "hostname,address,expire\n"
        "host1,10.0.0.1,1234567890\n"
    )
    
    output_file = tmp_path / "output.json"
    
    test_args = [
        "kea-leases-to-json",
        str(tmp_path),
        str(output_file),
        "--extension", ".txt",
        "--single-run"
    ]
    
    with patch.object(sys, 'argv', test_args):
        main()
    
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
        assert len(data) == 1


def test_cli_with_log_level(tmp_path):
    """Test CLI with different log levels"""
    csv_file = tmp_path / "lease.csv"
    csv_file.write_text("hostname,address,expire\n")
    
    output_file = tmp_path / "output.json"
    
    for log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        test_args = [
            "kea-leases-to-json",
            str(tmp_path),
            str(output_file),
            "--log-level", log_level,
            "--single-run"
        ]
        
        with patch.object(sys, 'argv', test_args):
            main()
        
        assert output_file.exists()


def test_cli_version_flag():
    """Test --version flag"""
    test_args = ["kea-leases-to-json", "--version"]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_cli_version_short_flag():
    """Test -v flag for version"""
    test_args = ["kea-leases-to-json", "-v"]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_cli_missing_required_arguments():
    """Test CLI with missing required arguments"""
    test_args = ["kea-leases-to-json"]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0


def test_cli_invalid_log_level(tmp_path):
    """Test CLI with invalid log level"""
    output_file = tmp_path / "output.json"
    
    test_args = [
        "kea-leases-to-json",
        str(tmp_path),
        str(output_file),
        "--log-level", "INVALID",
        "--single-run"
    ]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0


def test_cli_help_flag():
    """Test --help flag"""
    test_args = ["kea-leases-to-json", "--help"]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


@patch('daemonize.Daemonize')
def test_cli_daemonize_mode(mock_daemonize, tmp_path):
    """Test CLI with daemonize flag"""
    csv_file = tmp_path / "lease.csv"
    csv_file.write_text("hostname,address,expire\n")
    
    output_file = tmp_path / "output.json"
    pid_file = tmp_path / "test.pid"
    
    test_args = [
        "kea-leases-to-json",
        str(tmp_path),
        str(output_file),
        "--daemonize",
        "--pid", str(pid_file)
    ]
    
    mock_daemon_instance = MagicMock()
    mock_daemonize.return_value = mock_daemon_instance
    
    with patch.object(sys, 'argv', test_args):
        main()
    
    mock_daemonize.assert_called_once()
    mock_daemon_instance.start.assert_called_once()


def test_cli_daemonize_ignored_with_single_run(tmp_path):
    """Test that daemonize is ignored when single-run is specified"""
    csv_file = tmp_path / "lease.csv"
    csv_file.write_text(
        "hostname,address,expire\n"
        "host1,192.168.1.1,1234567890\n"
    )
    
    output_file = tmp_path / "output.json"
    
    test_args = [
        "kea-leases-to-json",
        str(tmp_path),
        str(output_file),
        "--daemonize",
        "--single-run"
    ]
    
    # Should not attempt to import Daemonize when single-run is set
    with patch.object(sys, 'argv', test_args):
        main()
    
    assert output_file.exists()


def test_cli_with_ipv6_addresses(tmp_path):
    """Test CLI with IPv6 addresses"""
    csv_file = tmp_path / "lease.csv"
    csv_file.write_text(
        "hostname,address,expire\n"
        "ipv6-host,2001:db8::1,1234567890\n"
    )
    
    output_file = tmp_path / "output.json"
    
    test_args = [
        "kea-leases-to-json",
        str(tmp_path),
        str(output_file),
        "--single-run"
    ]
    
    with patch.object(sys, 'argv', test_args):
        main()
    
    with open(output_file) as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["AddressType"] == "IPv6"
        assert data[0]["Hostname"] == "ipv6-host"


def test_cli_with_multiple_lease_files(tmp_path):
    """Test CLI with multiple CSV files in directory"""
    csv_file1 = tmp_path / "lease1.csv"
    csv_file1.write_text(
        "hostname,address,expire\n"
        "host1,192.168.1.1,1234567890\n"
    )
    
    csv_file2 = tmp_path / "lease2.csv"
    csv_file2.write_text(
        "hostname,address,expire\n"
        "host2,192.168.1.2,1234567891\n"
    )
    
    output_file = tmp_path / "output.json"
    
    test_args = [
        "kea-leases-to-json",
        str(tmp_path),
        str(output_file),
        "--single-run"
    ]
    
    with patch.object(sys, 'argv', test_args):
        main()
    
    with open(output_file) as f:
        data = json.load(f)
        assert len(data) == 2
        hostnames = {item["Hostname"] for item in data}
        assert hostnames == {"host1", "host2"}


def test_cli_custom_pid_file(tmp_path):
    """Test CLI with custom PID file path"""
    csv_file = tmp_path / "lease.csv"
    csv_file.write_text("hostname,address,expire\n")
    
    output_file = tmp_path / "output.json"
    custom_pid = tmp_path / "custom.pid"
    
    test_args = [
        "kea-leases-to-json",
        str(tmp_path),
        str(output_file),
        "--pid", str(custom_pid),
        "--single-run"
    ]
    
    with patch.object(sys, 'argv', test_args):
        main()
    
    assert output_file.exists()
