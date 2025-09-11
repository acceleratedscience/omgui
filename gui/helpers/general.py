import socket


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
