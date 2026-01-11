"""
Core orchestration and output formatting for network diagnostics.

Coordinates ping, DNS, and HTTP checks and generates human-readable summaries.
"""

import json
from . import ping
from . import dns_checks
from . import http_checks


def run_diagnostics(args):
    """
    Run network diagnostics based on command-line arguments.
    
    Args:
        args: argparse.Namespace with diagnostic configuration
        
    Returns:
        dict with keys:
            - ping_results: ping result dict (None if not performed)
            - dns_results: list of DNS result dicts (empty if not performed)
            - http_results: HTTP result dict (None if not performed)
    """
    ping_results = None
    dns_results = []
    http_results = None
    
    # Ping check
    if args.target:
        ping_results = ping.ping_target(args.target, args.count, args.timeout)
    
    # DNS checks
    if not args.no_dns:
        if args.dns:
            hostnames = args.dns if isinstance(args.dns, list) else [args.dns]
            dns_results = dns_checks.check_multiple_dns(hostnames, args.timeout)
        else:
            # Default DNS checks
            default_hostnames = ["google.com", "cloudflare.com"]
            dns_results = dns_checks.check_multiple_dns(default_hostnames, args.timeout)
    
    # HTTP check
    if args.http:
        http_results = http_checks.check_http(args.http, args.timeout)
    
    return {
        "ping_results": ping_results,
        "dns_results": dns_results,
        "http_results": http_results,
    }


def format_output(results, summary_only=False, json_format=False):
    """
    Format diagnostic results for output.
    
    Args:
        results: dict from run_diagnostics
        summary_only: if True, only show summary (no detailed output)
        json_format: if True, output as JSON
        
    Returns:
        string with formatted output
    """
    if json_format:
        return format_json_output(results)
    elif summary_only:
        return format_summary_only(results)
    else:
        return format_detailed_output(results)


def format_json_output(results):
    """Format results as JSON."""
    output = {}
    
    if results["ping_results"]:
        output["ping"] = results["ping_results"]
    
    if results["dns_results"]:
        output["dns"] = results["dns_results"]
    
    if results["http_results"]:
        output["http"] = results["http_results"]
    
    # Add summary
    summary = generate_summary(
        results["ping_results"],
        results["dns_results"],
        results["http_results"]
    )
    output["summary"] = summary
    
    return json.dumps(output, indent=2)


def format_summary_only(results):
    """Format only the summary."""
    summary = generate_summary(
        results["ping_results"],
        results["dns_results"],
        results["http_results"]
    )
    return summary + "\n"


def format_detailed_output(results):
    """Format detailed output with sections."""
    lines = []
    
    # Ping results
    if results["ping_results"]:
        pr = results["ping_results"]
        lines.append("=== Ping Results ===")
        lines.append(f"Target: {pr['host']}")
        if pr.get("port"):
            lines.append(f"Port: {pr['port']}")
        lines.append(f"Method: {pr['method']}")
        
        if pr["avg"] is not None:
            lines.append(f"Min/Avg/Max latency: {pr['min']:.2f} / {pr['avg']:.2f} / {pr['max']:.2f} ms")
            lines.append(f"Packet loss: {pr['packet_loss']:.1f}%")
        else:
            lines.append("All ping attempts failed")
        lines.append("")
    
    # DNS results
    if results["dns_results"]:
        lines.append("=== DNS Checks ===")
        for dns_result in results["dns_results"]:
            hostname = dns_result["hostname"]
            if dns_result["success"]:
                ips_str = ", ".join(dns_result["ips"])
                lines.append(f"{hostname}: OK ({ips_str})")
            else:
                lines.append(f"{hostname}: FAILED ({dns_result['error']})")
        lines.append("")
    
    # HTTP results
    if results["http_results"]:
        hr = results["http_results"]
        lines.append("=== HTTP Check ===")
        lines.append(f"URL: {hr['url']}")
        if hr["success"]:
            status_code = hr["status_code"]
            response_time = hr["response_time"]
            lines.append(f"Status: {status_code} OK")
            if response_time:
                lines.append(f"Response time: {response_time:.3f} s")
        else:
            lines.append(f"Status: FAILED ({hr['error']})")
        lines.append("")
    
    # Summary
    lines.append("=== Summary ===")
    summary = generate_summary(
        results["ping_results"],
        results["dns_results"],
        results["http_results"]
    )
    lines.append(summary)
    
    return "\n".join(lines)


def generate_summary(ping_results, dns_results, http_results):
    """
    Generate a natural language summary of diagnostic results.
    
    Args:
        ping_results: ping result dict or None
        dns_results: list of DNS result dicts
        http_results: HTTP result dict or None
        
    Returns:
        string with summary text
    """
    summary_parts = []
    
    # Analyze ping results
    if ping_results:
        if ping_results["packet_loss"] == 100:
            summary_parts.append("All ping attempts failed. No connectivity to target host.")
        elif ping_results["packet_loss"] > 50:
            summary_parts.append(f"Severe packet loss ({ping_results['packet_loss']:.1f}%) and connectivity issues.")
        elif ping_results["packet_loss"] > 20:
            summary_parts.append(f"High packet loss ({ping_results['packet_loss']:.1f}%) detected.")
        elif ping_results["avg"] is not None:
            if ping_results["avg"] > 500:
                summary_parts.append(f"Very high latency ({ping_results['avg']:.0f} ms average) suggests network congestion or routing issues.")
            elif ping_results["avg"] > 200:
                summary_parts.append(f"High latency ({ping_results['avg']:.0f} ms average) detected.")
            else:
                summary_parts.append(f"Average latency {ping_results['avg']:.0f} ms, packet loss {ping_results['packet_loss']:.1f}%.")
    
    # Analyze DNS results
    if dns_results:
        dns_success_count = sum(1 for r in dns_results if r["success"])
        dns_total_count = len(dns_results)
        
        if dns_success_count == 0:
            summary_parts.append("DNS resolution is failing for all tested hostnames.")
        elif dns_success_count < dns_total_count:
            failed = [r["hostname"] for r in dns_results if not r["success"]]
            summary_parts.append(f"DNS resolution failed for: {', '.join(failed)}")
        else:
            summary_parts.append("DNS resolution OK.")
    
    # Analyze HTTP results
    if http_results:
        if http_results["success"]:
            status_code = http_results["status_code"]
            response_time = http_results["response_time"]
            if response_time:
                summary_parts.append(f"HTTP GET {http_results['url']}: {status_code} OK in {response_time:.3f} s")
            else:
                summary_parts.append(f"HTTP GET {http_results['url']}: {status_code} OK")
        else:
            summary_parts.append(f"HTTP request to {http_results['url']} failed: {http_results['error']}")
    
    # Generate overall assessment
    if not summary_parts:
        return "No diagnostics performed."
    
    # Add interpretation
    interpretation = []
    if ping_results and ping_results["packet_loss"] > 30:
        interpretation.append("High packet loss suggests problems with your connection, ISP, or the target host.")
    
    if dns_results and all(not r["success"] for r in dns_results):
        if ping_results and ping_results["packet_loss"] < 50:
            interpretation.append("DNS resolution is failing, but raw IP connectivity appears fine. Check DNS server configuration.")
    
    if ping_results and ping_results["packet_loss"] == 100:
        interpretation.append("Complete connectivity failure suggests local network issues, firewall blocking, or host unreachable.")
    
    if interpretation:
        summary_parts.append("")
        summary_parts.append("Interpretation:")
        for interp in interpretation:
            summary_parts.append(f"  - {interp}")
    
    return "\n".join(summary_parts)
