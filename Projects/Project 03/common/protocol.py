import json
import struct
from common.constants import HEADER_SIZE, FORMAT, BUF_SIZE


def send_msg(sock, data):
    """
    Send a JSON message with fixed-size header.
    """
    try:
        raw = json.dumps(data).encode(FORMAT)
        header = struct.pack("!I", len(raw))
        sock.sendall(header + raw)
    except:
        pass


def recv_msg(sock):
    """
    Receive a JSON message with fixed-size header.
    """
    try:
        header = _recv_all(sock, HEADER_SIZE)
        if not header:
            return None

        length = struct.unpack("!I", header)[0]
        payload = _recv_all(sock, length)
        if not payload:
            return None

        return json.loads(payload.decode(FORMAT))
    except:
        return None


def _recv_all(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data
