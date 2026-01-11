"""
Tests for ping functionality.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import socket
from netwhy import ping


class TestPing(unittest.TestCase):
    """Test ping functions."""
    
    @patch('netwhy.ping.socket.socket')
    def test_tcp_ping_success(self, mock_socket_class):
        """Test successful TCP ping."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        # Mock connect to succeed (no exception)
        mock_socket.connect.return_value = None
        
        # Mock successful connections
        result = ping.tcp_ping("example.com", 80, 5, 3)
        
        self.assertEqual(result["method"], "tcp")
        self.assertEqual(result["host"], "example.com")
        self.assertEqual(result["port"], 80)
        self.assertEqual(result["packet_loss"], 0.0)
        self.assertIsNotNone(result["avg"])
        self.assertGreater(len(result["latencies"]), 0)
        self.assertEqual(len([l for l in result["latencies"] if l is not None]), 3)
    
    @patch('netwhy.ping.socket.socket')
    def test_tcp_ping_timeout(self, mock_socket_class):
        """Test TCP ping with timeouts."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = socket.timeout()
        
        result = ping.tcp_ping("example.com", 80, 5, 3)
        
        self.assertEqual(result["packet_loss"], 100.0)
        self.assertIsNone(result["avg"])
        self.assertEqual(len([l for l in result["latencies"] if l is None]), 3)
    
    @patch('netwhy.ping.socket.socket')
    def test_tcp_ping_partial_failure(self, mock_socket_class):
        """Test TCP ping with partial failures."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        call_count = [0]
        
        def side_effect(*args):
            call_count[0] += 1
            if call_count[0] == 2:
                raise socket.error("Connection failed")
        
        mock_socket.connect.side_effect = side_effect
        
        result = ping.tcp_ping("example.com", 80, 5, 3)
        
        # Should have some packet loss
        self.assertGreater(result["packet_loss"], 0)
        self.assertLess(result["packet_loss"], 100)
    
    @patch('subprocess.run')
    def test_icmp_ping_success(self, mock_run):
        """Test successful ICMP ping."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
PING example.com (93.184.216.34) 56(84) bytes of data.
64 bytes from example.com (93.184.216.34): icmp_seq=1 ttl=54 time=12.345 ms
64 bytes from example.com (93.184.216.34): icmp_seq=2 ttl=54 time=13.456 ms
64 bytes from example.com (93.184.216.34): icmp_seq=3 ttl=54 time=14.567 ms
        """
        mock_run.return_value = mock_result
        
        result = ping.icmp_ping("example.com", 3, 5)
        
        self.assertEqual(result["method"], "icmp")
        self.assertEqual(result["host"], "example.com")
        self.assertLess(result["packet_loss"], 100)
        self.assertGreater(len([l for l in result["latencies"] if l is not None]), 0)
    
    @patch('subprocess.run')
    def test_icmp_ping_failure(self, mock_run):
        """Test ICMP ping failure."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        result = ping.icmp_ping("example.com", 3, 5)
        
        self.assertEqual(result["packet_loss"], 100.0)
        self.assertIsNone(result["avg"])
    
    @patch('subprocess.run')
    def test_icmp_ping_command_not_found(self, mock_run):
        """Test ICMP ping when command is not found."""
        mock_run.side_effect = FileNotFoundError()
        
        result = ping.icmp_ping("example.com", 3, 5)
        
        self.assertEqual(result["packet_loss"], 100.0)
    
    @patch('netwhy.ping.tcp_ping')
    def test_ping_target_success(self, mock_tcp_ping):
        """Test ping_target with successful TCP ping."""
        mock_tcp_ping.return_value = {
            "packet_loss": 0,
            "avg": 50.0,
            "method": "tcp",
        }
        
        result = ping.ping_target("example.com", 4, 5)
        
        self.assertEqual(result["method"], "tcp")
        mock_tcp_ping.assert_called_once_with("example.com", 80, 5, 4)
    
    @patch('netwhy.ping.icmp_ping')
    @patch('netwhy.ping.tcp_ping')
    def test_ping_target_tcp_fallback_to_icmp(self, mock_tcp_ping, mock_icmp_ping):
        """Test ping_target falling back to ICMP when TCP fails."""
        mock_tcp_ping.return_value = {
            "packet_loss": 100,
            "avg": None,
            "method": "tcp",
        }
        mock_icmp_ping.return_value = {
            "packet_loss": 0,
            "avg": 20.0,
            "method": "icmp",
        }
        
        result = ping.ping_target("example.com", 4, 5)
        
        self.assertEqual(result["method"], "icmp")
        mock_tcp_ping.assert_called_once()
        mock_icmp_ping.assert_called_once()


if __name__ == '__main__':
    unittest.main()
