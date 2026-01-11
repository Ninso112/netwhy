"""
Command-line interface for netwhy network diagnostics tool.
"""

import argparse
import sys
from . import __version__
from . import core


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="netwhy - A lightweight Linux CLI tool for network diagnostics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  netwhy                              # Standard diagnosis
  netwhy --target example.com --count 10
  netwhy --dns example.com --http https://example.com --summary
  netwhy --json                       # JSON output
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"netwhy {__version__}"
    )
    
    parser.add_argument(
        "--target",
        type=str,
        metavar="HOST",
        default="8.8.8.8",
        help="Target hostname or IP address for ping checks (default: 8.8.8.8)"
    )
    
    parser.add_argument(
        "--count",
        type=int,
        metavar="N",
        default=4,
        help="Number of ping attempts (default: 4)"
    )
    
    parser.add_argument(
        "--dns",
        type=str,
        action="append",
        metavar="HOSTNAME",
        help="DNS check for hostname (can be specified multiple times, default: google.com, cloudflare.com)"
    )
    
    parser.add_argument(
        "--no-dns",
        action="store_true",
        help="Disable DNS checks"
    )
    
    parser.add_argument(
        "--http",
        type=str,
        metavar="URL",
        help="HTTP reachability check for URL"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        metavar="SECONDS",
        default=5.0,
        help="Timeout for individual checks in seconds (default: 5.0)"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Only show summary, no detailed output"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for netwhy CLI."""
    args = parse_args()
    
    try:
        # Run diagnostics
        results = core.run_diagnostics(args)
        
        # Format and output results
        output = core.format_output(results, args.summary, args.json)
        print(output)
        
        # Exit code: 0 if everything OK, 1 if problems detected
        exit_code = 0
        
        # Determine exit code based on results
        if results["ping_results"] and results["ping_results"]["packet_loss"] == 100:
            exit_code = 1
        elif results["dns_results"] and all(not r["success"] for r in results["dns_results"]):
            exit_code = 1
        elif results["http_results"] and not results["http_results"]["success"]:
            exit_code = 1
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
