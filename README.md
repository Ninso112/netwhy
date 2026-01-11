# netwhy

netwhy is a lightweight Linux command-line tool that diagnoses slow or unreliable network connections. It runs quick checks (latency, packet loss, DNS, optional HTTP) and summarizes where problems are most likely: local link, DNS, or remote host.

## Features

- **Latency and packet loss testing**: TCP-connect ping (no root required) with ICMP fallback
- **DNS resolution checks**: Verify DNS functionality for multiple hostnames
- **HTTP reachability checks**: Test HTTP/HTTPS connectivity to URLs
- **Clear summaries**: Human-readable output with natural language interpretations
- **JSON output**: Structured JSON format for scripting and automation
- **Zero dependencies**: Uses only Python standard library

## Installation

### From source

```bash
git clone <repository-url>
cd netwhy
pip install .
```

Alternatively, you can run directly from the source directory:

```bash
cd netwhy
python -m netwhy.cli
```

Or make it executable and add to PATH:

```bash
chmod +x src/netwhy/cli.py
# Or use: pip install -e .
```

## Usage

### Standard diagnosis

Run without arguments to perform a standard diagnostic:

```bash
netwhy
```

This will:
- Ping 8.8.8.8 (Google's DNS server) with 4 attempts
- Check DNS resolution for google.com and cloudflare.com
- Display results and a summary

### Target-specific latency test

Test connectivity to a specific host with more attempts:

```bash
netwhy --target example.com --count 10
```

Output shows min/avg/max latency and packet loss percentage.

### Combined DNS and HTTP test

Check DNS resolution and HTTP reachability:

```bash
netwhy --dns example.com --http https://example.com --summary
```

The `--summary` flag shows only the final summary, without detailed per-probe output.

### JSON output

Generate JSON output for scripting:

```bash
netwhy --json
```

JSON output includes all metrics and the summary text in a structured format.

## Command-line Options

- `--target HOST`: Target hostname or IP address for ping checks (default: 8.8.8.8)
- `--count N`: Number of ping attempts (default: 4)
- `--dns HOSTNAME`: DNS check for hostname (can be specified multiple times, default: google.com, cloudflare.com)
- `--no-dns`: Disable DNS checks
- `--http URL`: HTTP reachability check for URL
- `--timeout SECONDS`: Timeout for individual checks in seconds (default: 5.0)
- `--summary`: Only show summary, no detailed output
- `--json`: Output results as JSON
- `--version`: Show version information
- `--help`: Show help message

## Examples

### Diagnose connectivity to a specific server

```bash
netwhy --target 1.1.1.1 --count 5
```

### Check DNS resolution for multiple domains

```bash
netwhy --dns google.com --dns cloudflare.com --dns github.com
```

### Full diagnostic with HTTP check

```bash
netwhy --target 8.8.8.8 --dns google.com --http https://www.google.com
```

### Quick summary only

```bash
netwhy --summary
```

### JSON output for automation

```bash
netwhy --target example.com --json > results.json
```

## Known Limitations

1. **ICMP ping**: ICMP ping requires root privileges on most Linux systems. netwhy uses TCP-connect ping by default, which works without root. If TCP ping fails completely, it falls back to ICMP via the system's `ping` command (if available).

2. **TCP ping limitations**: TCP-connect ping measures connection establishment time, not true ICMP latency. Results may differ from traditional ping tools.

3. **Interpretation vs. raw data**: The tool provides interpretations based on common network issues, but these are suggestions, not definitive diagnoses. Always consider your specific network environment.

4. **Timeout behavior**: Very slow connections may timeout, which could indicate network issues but may also be due to overly strict timeout settings.

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.
