import socket
import threading
from protocol_utils import send_message, recv_message

HOST = '127.0.0.1'
PORT = 12345
clients = []

def broadcast(message, sender_socket):
    for client in clients[:]:
        try:
            if client != sender_socket:
                send_message(client, message)
        except:
            print("[WARNING] Removing dead client")
            clients.remove(client)
            client.close()

def handle_client(client_socket):
    while True:
        try:
            message = recv_message(client_socket)
            if not message:
                break
            print("Received:", message)
            broadcast(message, client_socket)
        except Exception as e:
            print(f"[CLIENT ERROR] {e}")
            break

    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[+] Encrypted server running on {HOST}:{PORT}")

    while True:
        client_socket, _ = server.accept()
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

start_server()
