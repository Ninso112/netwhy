"""
DNS resolution checks for network diagnostics.

Uses socket.getaddrinfo for DNS resolution testing.
"""

import socket


def check_dns(hostname, timeout=5):
    """
    Check DNS resolution for a hostname.
    
    Args:
        hostname: Hostname to resolve
        timeout: Timeout in seconds for DNS resolution
        
    Returns:
        dict with keys:
            - hostname: the hostname checked
            - success: boolean indicating if resolution succeeded
            - ips: list of resolved IP addresses (empty if failed)
            - error: error message string (None if successful)
    """
    try:
        # Set socket timeout
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        
        try:
            # Resolve hostname to IP addresses
            addrinfo = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
            ips = list(set([addr[4][0] for addr in addrinfo]))
            
            return {
                "hostname": hostname,
                "success": True,
                "ips": ips,
                "error": None,
            }
        except socket.gaierror as e:
            return {
                "hostname": hostname,
                "success": False,
                "ips": [],
                "error": str(e),
            }
        except (socket.timeout, OSError) as e:
            return {
                "hostname": hostname,
                "success": False,
                "ips": [],
                "error": str(e),
            }
        finally:
            socket.setdefaulttimeout(old_timeout)
    except Exception as e:
        return {
            "hostname": hostname,
            "success": False,
            "ips": [],
            "error": str(e),
        }


def check_multiple_dns(hostnames, timeout=5):
    """
    Check DNS resolution for multiple hostnames.
    
    Args:
        hostnames: List of hostnames to check
        timeout: Timeout in seconds for each DNS resolution
        
    Returns:
        list of result dicts (one per hostname, same structure as check_dns)
    """
    results = []
    for hostname in hostnames:
        results.append(check_dns(hostname, timeout))
    return results
