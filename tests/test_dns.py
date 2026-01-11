"""
Tests for DNS checks.
"""

import unittest
from unittest.mock import patch, MagicMock
import socket
from netwhy import dns_checks


class TestDNSChecks(unittest.TestCase):
    """Test DNS check functions."""
    
    @patch('netwhy.dns_checks.socket.getaddrinfo')
    def test_check_dns_success(self, mock_getaddrinfo):
        """Test successful DNS resolution."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 0)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2606:2800:220:1:248:1893:25c8:1946', 0)),
        ]
        
        result = dns_checks.check_dns("example.com", 5)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["hostname"], "example.com")
        self.assertIn("93.184.216.34", result["ips"])
        self.assertIsNone(result["error"])
    
    @patch('netwhy.dns_checks.socket.getaddrinfo')
    def test_check_dns_failure(self, mock_getaddrinfo):
        """Test DNS resolution failure."""
        mock_getaddrinfo.side_effect = socket.gaierror("Name or service not known")
        
        result = dns_checks.check_dns("nonexistent.example.invalid", 5)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["hostname"], "nonexistent.example.invalid")
        self.assertEqual(len(result["ips"]), 0)
        self.assertIsNotNone(result["error"])
    
    @patch('netwhy.dns_checks.socket.getaddrinfo')
    def test_check_dns_timeout(self, mock_getaddrinfo):
        """Test DNS resolution timeout."""
        mock_getaddrinfo.side_effect = socket.timeout("Timeout")
        
        result = dns_checks.check_dns("example.com", 5)
        
        self.assertFalse(result["success"])
        self.assertEqual(len(result["ips"]), 0)
        self.assertIsNotNone(result["error"])
    
    @patch('netwhy.dns_checks.check_dns')
    def test_check_multiple_dns(self, mock_check_dns):
        """Test checking multiple hostnames."""
        mock_check_dns.side_effect = [
            {"hostname": "example.com", "success": True, "ips": ["93.184.216.34"], "error": None},
            {"hostname": "test.com", "success": False, "ips": [], "error": "Name not found"},
        ]
        
        results = dns_checks.check_multiple_dns(["example.com", "test.com"], 5)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]["success"])
        self.assertFalse(results[1]["success"])
        self.assertEqual(mock_check_dns.call_count, 2)


if __name__ == '__main__':
    unittest.main()
