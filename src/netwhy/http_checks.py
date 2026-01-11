"""
HTTP reachability checks for network diagnostics.

Uses urllib and http.client for HTTP/HTTPS checks.
"""

import socket
import urllib.parse
import urllib.request
import http.client
import time


def check_http(url, timeout=5, method="HEAD"):
    """
    Check HTTP/HTTPS reachability for a URL.
    
    Args:
        url: URL to check (should include scheme, e.g., http:// or https://)
        timeout: Timeout in seconds for the HTTP request
        method: HTTP method to use ("HEAD" or "GET", default: "HEAD")
        
    Returns:
        dict with keys:
            - url: the URL checked
            - success: boolean indicating if request succeeded
            - status_code: HTTP status code (None if failed)
            - response_time: response time in seconds (None if failed)
            - error: error message string (None if successful)
    """
    start_time = time.time()
    
    try:
        # Parse URL
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme:
            # Default to http if no scheme provided
            url = "http://" + url
            parsed = urllib.parse.urlparse(url)
        
        # Create request
        req = urllib.request.Request(url, method=method.upper())
        
        # Make request with timeout
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_time = time.time() - start_time
            status_code = response.getcode()
            
            return {
                "url": url,
                "success": True,
                "status_code": status_code,
                "response_time": response_time,
                "error": None,
            }
    except urllib.error.HTTPError as e:
        # HTTP error (4xx, 5xx) - server responded, so it's "reachable"
        response_time = time.time() - start_time
        return {
            "url": url,
            "success": True,  # Server responded, even with error
            "status_code": e.code,
            "response_time": response_time,
            "error": None,
        }
    except (urllib.error.URLError, socket.timeout, OSError) as e:
        response_time = time.time() - start_time if time.time() - start_time < timeout else None
        return {
            "url": url,
            "success": False,
            "status_code": None,
            "response_time": response_time,
            "error": str(e),
        }
    except Exception as e:
        response_time = time.time() - start_time if time.time() - start_time < timeout else None
        return {
            "url": url,
            "success": False,
            "status_code": None,
            "response_time": response_time,
            "error": str(e),
        }
