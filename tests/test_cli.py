"""
Tests for CLI argument parsing.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from netwhy import cli


class TestCLI(unittest.TestCase):
    """Test command-line argument parsing."""
    
    def test_default_args(self):
        """Test default arguments."""
        test_args = ["netwhy"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertEqual(args.target, "8.8.8.8")
            self.assertEqual(args.count, 4)
            self.assertFalse(args.no_dns)
            self.assertIsNone(args.http)
            self.assertEqual(args.timeout, 5.0)
            self.assertFalse(args.summary)
            self.assertFalse(args.json)
    
    def test_target_option(self):
        """Test --target option."""
        test_args = ["netwhy", "--target", "example.com"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertEqual(args.target, "example.com")
    
    def test_count_option(self):
        """Test --count option."""
        test_args = ["netwhy", "--count", "10"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertEqual(args.count, 10)
    
    def test_dns_option(self):
        """Test --dns option."""
        test_args = ["netwhy", "--dns", "example.com"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertEqual(args.dns, ["example.com"])
    
    def test_multiple_dns_options(self):
        """Test multiple --dns options."""
        test_args = ["netwhy", "--dns", "example.com", "--dns", "test.com"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertEqual(args.dns, ["example.com", "test.com"])
    
    def test_no_dns_option(self):
        """Test --no-dns option."""
        test_args = ["netwhy", "--no-dns"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertTrue(args.no_dns)
    
    def test_http_option(self):
        """Test --http option."""
        test_args = ["netwhy", "--http", "https://example.com"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertEqual(args.http, "https://example.com")
    
    def test_timeout_option(self):
        """Test --timeout option."""
        test_args = ["netwhy", "--timeout", "10"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertEqual(args.timeout, 10.0)
    
    def test_summary_option(self):
        """Test --summary option."""
        test_args = ["netwhy", "--summary"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertTrue(args.summary)
    
    def test_json_option(self):
        """Test --json option."""
        test_args = ["netwhy", "--json"]
        with patch.object(sys, 'argv', test_args):
            args = cli.parse_args()
            self.assertTrue(args.json)
    
    @patch('netwhy.cli.core.run_diagnostics')
    @patch('netwhy.cli.core.format_output')
    @patch('sys.exit')
    def test_main_success(self, mock_exit, mock_format, mock_run):
        """Test main function with successful diagnostics."""
        mock_run.return_value = {
            "ping_results": {"packet_loss": 0},
            "dns_results": [{"success": True}],
            "http_results": None,
        }
        mock_format.return_value = "Test output"
        
        test_args = ["netwhy"]
        with patch.object(sys, 'argv', test_args):
            cli.main()
        
        mock_run.assert_called_once()
        mock_format.assert_called_once()
        mock_exit.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main()
