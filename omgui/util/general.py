import time
import socket
import datetime
import readline
from spf import spf


def next_avail_port(port=8024, host="127.0.0.1"):
    """
    Returns the next available port starting with 8024.

    This lets us avoid multiple apps trying to run on the same port.

    Note: Binding our server to the 0.0.0.0 interface would
    allow it to accept connections from any network interface
    on the host machine, in other words from external devices.
    """

    # Check if a port is open
    def _is_port_open(host, port):
        try:
            # Create a socket object and attempt to connect
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Set a timeout for the connection attempt
                s.connect((host, port))
            return False  # Port is occupied
        except (ConnectionRefusedError, socket.timeout):
            return True  # Port is available

    while not _is_port_open(host, port):
        port += 1
    return host, port


def wait_for_port(host, port, timeout=5.0, interval=0.1):
    """
    Pauses the process until a given port
    starts accepting TCP connections.

    timeout & interval are expressed in seconds.
    """

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=interval):
                return True
        except OSError:
            # Keep retrying until the deadline is reached
            time.sleep(interval)
    # Timed out
    return False


# Confirm promt for True or False Questions
def confirm_prompt(question: str = "", default=False) -> bool:
    reply = None
    while reply not in ("y", "n"):
        try:
            spf(f"<yellow>{question}</yellow>")
            reply = input("(y/n): ").casefold()
            readline.remove_history_item(readline.get_current_history_length() - 1)
        except KeyboardInterrupt:
            print("\n")
            return default
    if reply == "y":
        return True
    return False


def pretty_date(timestamp=None, style="log", include_time=True):
    """
    Prettify a timestamp.
    """
    # If no timestamp provided, use the current time
    if not timestamp:
        timestamp = time.time()

    # Choose the output format
    fmt = None
    if style == "log":
        fmt = "%d-%m-%Y"  # 07-01-2024
        if include_time:
            fmt += ", %H:%M:%S"  # 07-01-2024, 15:12:45
    elif style == "pretty":
        fmt = "%b %d, %Y"  # Jan 7, 2024
        if include_time:
            fmt += " at %H:%M"  # Jan 7, 2024 at 15:12
    else:
        raise ValueError(f"Invalid '{style}' style parameter")

    # Parse date/time string
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime(fmt)


def is_numeric(str_or_nr):
    """
    Check if a variable (string or number) is numeric.
    """
    try:
        float(str_or_nr)
        return True
    except ValueError:
        return False


def merge_dict_lists(list1, list2):
    """
    Merge two lists of dictionaries while avoiding duplicates.
    """
    # Convert dictionaries to tuples of sorted items
    list1_tuples = [tuple(sorted(d.items())) for d in list1]
    list2_tuples = [tuple(sorted(d.items())) for d in list2]

    # Perform set operations to merge the lists while avoiding duplicates
    merged_tuples = list1_tuples + list(set(list2_tuples) - set(list1_tuples))

    # Convert the tuples back to dictionaries
    merged_list = [dict(t) for t in merged_tuples]

    return merged_list


def encode_uri_component(string):
    """
    Python equivalent of JavaScript's encodeURIComponent.
    """
    from urllib.parse import quote

    return quote(string.encode("utf-8"), safe="~()*!.'")
