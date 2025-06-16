import struct
from crypto_utils import encrypt, decrypt

def send_message(sock, message):
    encrypted = encrypt(message)
    msg_len = struct.pack('>I', len(encrypted))
    sock.sendall(msg_len + encrypted)

def recv_message(sock):
    raw_len = recvall(sock, 4)
    if not raw_len:
        return None
    msg_len = struct.unpack('>I', raw_len)[0]
    encrypted_msg = recvall(sock, msg_len)
    return decrypt(encrypted_msg)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data