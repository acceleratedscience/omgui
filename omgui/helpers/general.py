import time
import socket
import readline
from openad.helpers.output import output_text


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
            output_text(f"<yellow>{question}</yellow>", return_val=False)
            reply = input("(y/n): ").casefold()
            readline.remove_history_item(readline.get_current_history_length() - 1)
        except KeyboardInterrupt:
            print("\n")
            return default
    if reply == "y":
        return True
    return False
