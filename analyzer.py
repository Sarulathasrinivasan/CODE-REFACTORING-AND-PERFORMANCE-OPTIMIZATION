import re
from collections import Counter
from typing import Dict, Generator

# --- Configuration & Optimization ---
# Pre-compiling regex patterns outside the loop saves significant CPU cycles
ERROR_PATTERNS = {
    "DATABASE_FAILURE": re.compile(r"connection_refused|timeout", re.IGNORECASE),
    "NETWORK_ERROR": re.compile(r"404|500|unreachable", re.IGNORECASE),
    "AUTH_DENIED": re.compile(r"invalid_token|unauthorized", re.IGNORECASE),
}

def stream_log_lines(filepath: str) -> Generator[str, None, None]:
    """
    Memory-efficient file reader.
    Yields lines one by one to keep memory usage at O(1).
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                # Early filter: only yield lines that contain 'ERROR'
                if "ERROR" in line.upper():
                    yield line
    except FileNotFoundError:
        print(f"Critial Error: The file '{filepath}' was not found.")
    except PermissionError:
        print(f"Critical Error: Insufficient permissions to read '{filepath}'.")

def analyze_logs(filepath: str) -> Dict[str, int]:
    """
    Processes log data in a single pass and returns a summary.
    """
    # Counter is highly optimized for this specific use case
    error_summary = Counter()

    for line in stream_log_lines(filepath):
        for error_type, pattern in ERROR_PATTERNS.items():
            if pattern.search(line):
                error_summary[error_type] += 1
    
    return dict(error_summary)

# --- Entry Point ---
if __name__ == "__main__":
    LOG_FILE = "production_logs.txt"
    
    print(f"Starting analysis on {LOG_FILE}...")
    results = analyze_logs(LOG_FILE)
    
    print("\n--- Error Analysis Report ---")
    if not results:
        print("No errors found or file is empty.")
    else:
        for error, count in results.items():
            print(f"{error:18}: {count} occurrences")