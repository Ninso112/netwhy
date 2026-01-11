"""
Tests for HTTP checks.
"""

import unittest
from unittest.mock import patch, MagicMock
import urllib.error
from netwhy import http_checks


class TestHTTPChecks(unittest.TestCase):
    """Test HTTP check functions."""
    
    @patch('netwhy.http_checks.urllib.request.urlopen')
    def test_check_http_success(self, mock_urlopen):
        """Test successful HTTP check."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = http_checks.check_http("https://example.com", 5)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["status_code"], 200)
        self.assertIsNotNone(result["response_time"])
        self.assertIsNone(result["error"])
    
    @patch('netwhy.http_checks.urllib.request.urlopen')
    def test_check_http_404(self, mock_urlopen):
        """Test HTTP check with 404 error (server responded)."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://example.com", 404, "Not Found", {}, None
        )
        
        result = http_checks.check_http("https://example.com", 5)
        
        # Server responded, so it's considered "success" (reachable)
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 404)
        self.assertIsNotNone(result["response_time"])
    
    @patch('netwhy.http_checks.urllib.request.urlopen')
    def test_check_http_connection_error(self, mock_urlopen):
        """Test HTTP check with connection error."""
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        
        result = http_checks.check_http("https://example.com", 5)
        
        self.assertFalse(result["success"])
        self.assertIsNone(result["status_code"])
        self.assertIsNotNone(result["error"])
    
    @patch('netwhy.http_checks.urllib.request.urlopen')
    def test_check_http_timeout(self, mock_urlopen):
        """Test HTTP check with timeout."""
        import socket
        mock_urlopen.side_effect = socket.timeout("Timeout")
        
        result = http_checks.check_http("https://example.com", 5)
        
        self.assertFalse(result["success"])
        self.assertIsNone(result["status_code"])
        self.assertIsNotNone(result["error"])
    
    @patch('netwhy.http_checks.urllib.request.urlopen')
    def test_check_http_no_scheme(self, mock_urlopen):
        """Test HTTP check with URL without scheme (should default to http)."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = http_checks.check_http("example.com", 5)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["url"], "http://example.com")


if __name__ == '__main__':
    unittest.main()
