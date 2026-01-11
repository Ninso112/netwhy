"""
Ping functionality for network diagnostics.

Provides TCP-connect ping (primary) and ICMP ping via subprocess (fallback).
"""

import socket
import subprocess
import time
import statistics


def tcp_ping(host, port, timeout, count):
    """
    Perform TCP-connect ping to a host:port.
    
    Args:
        host: Target hostname or IP address
        port: Target port number
        timeout: Timeout in seconds for each connection attempt
        count: Number of ping attempts
        
    Returns:
        dict with keys:
            - latencies: list of latency values in ms (None for failed attempts)
            - min: minimum latency in ms (None if all failed)
            - avg: average latency in ms (None if all failed)
            - max: maximum latency in ms (None if all failed)
            - packet_loss: packet loss percentage (0-100)
            - method: "tcp"
            - host: target host
            - port: target port
    """
    latencies = []
    
    for _ in range(count):
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            latencies.append(elapsed)
        except (socket.timeout, socket.error, OSError):
            latencies.append(None)
        finally:
            try:
                sock.close()
            except:
                pass
    
    # Calculate statistics
    successful = [l for l in latencies if l is not None]
    packet_loss = ((count - len(successful)) / count) * 100 if count > 0 else 100
    
    result = {
        "latencies": latencies,
        "min": min(successful) if successful else None,
        "avg": statistics.mean(successful) if successful else None,
        "max": max(successful) if successful else None,
        "packet_loss": packet_loss,
        "method": "tcp",
        "host": host,
        "port": port,
    }
    
    return result


def icmp_ping(host, count, timeout):
    """
    Perform ICMP ping using external ping command (fallback).
    
    Args:
        host: Target hostname or IP address
        count: Number of ping attempts
        timeout: Timeout in seconds for the entire ping operation
        
    Returns:
        dict with same structure as tcp_ping, method="icmp", port=None
    """
    latencies = []
    
    try:
        # Try to run ping command
        # Use -c for count, -W for timeout (Linux), parse output
        cmd = ["ping", "-c", str(count), "-W", str(int(timeout)), host]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 1,
        )
        
        if result.returncode == 0:
            # Parse ping output to extract latencies
            # Format: "time=12.345 ms" or "time<1.000 ms"
            for line in result.stdout.split("\n"):
                if "time=" in line or "time<" in line:
                    try:
                        # Extract time value
                        time_part = line.split("time")[1].split()[0]
                        time_part = time_part.replace("=", "").replace("<", "").replace("ms", "")
                        latency = float(time_part)
                        latencies.append(latency)
                    except (ValueError, IndexError):
                        continue
        else:
            # All pings failed
            latencies = [None] * count
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # ping command not available or timed out
        latencies = [None] * count
    
    # Calculate statistics
    successful = [l for l in latencies if l is not None]
    packet_loss = ((count - len(successful)) / count) * 100 if count > 0 else 100
    
    result = {
        "latencies": latencies,
        "min": min(successful) if successful else None,
        "avg": statistics.mean(successful) if successful else None,
        "max": max(successful) if successful else None,
        "packet_loss": packet_loss,
        "method": "icmp",
        "host": host,
        "port": None,
    }
    
    return result


def ping_target(host, count=4, timeout=5):
    """
    Ping a target host using TCP-connect (primary) or ICMP (fallback).
    
    Args:
        host: Target hostname or IP address
        count: Number of ping attempts (default: 4)
        timeout: Timeout in seconds per attempt (default: 5)
        
    Returns:
        dict with ping results (same structure as tcp_ping/icmp_ping)
    """
    # Default ports: try 80 (HTTP) first, then 443 (HTTPS)
    # Try TCP ping on port 80 first
    result = tcp_ping(host, 80, timeout, count)
    
    # If TCP ping fails completely, try ICMP as fallback
    if result["packet_loss"] == 100:
        try:
            icmp_result = icmp_ping(host, count, timeout)
            # Use ICMP if it has any successful results
            if icmp_result["packet_loss"] < 100:
                return icmp_result
        except Exception:
            pass  # Fall through to return TCP result
    
    return result
