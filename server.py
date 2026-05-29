import socket
import threading

# Configuration
HOST = '192.168.1.22'
PORT = 65432
BUFFER_SIZE = 1024

# Dictionary to keep track of connected clients: {client_socket: username}
clients = {}

def broadcast(message, sender_socket=None):
    """Sends a message to all connected clients except the sender."""
    for client in list(clients.keys()):
        if client != sender_socket:
            try:
                client.sendall(message.encode('utf-8'))
            except (ConnectionResetError, BrokenPipeError):
                # Clean up broken connections found during broadcast
                remove_client(client)

def remove_client(client_socket):
    """Removes a client from the active pool and closes its connection."""
    if client_socket in clients:
        username = clients[client_socket]
        del clients[client_socket]
        client_socket.close()
        leave_msg = f"📢 {username} has left the chat."
        print(leave_msg)
        broadcast(leave_msg)

def handle_client(client_socket, client_address):
    """Handles the lifecycle of a single client connection."""
    print(f"**New connection attempt from {client_address}**")
    
    try:
        # First message from client must be their username
        username = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
        if not username:
            username = f"Anonymous-{client_address[1]}"
            
        clients[client_socket] = username
        
        join_msg = f"🎉 {username} has joined the chat!"
        print(join_msg)
        broadcast(join_msg, sender_socket=client_socket)
        
        # Welcome message sent only to the connected client
        client_socket.sendall(f"Welcome to the chat, {username}! Type 'quit' to exit.\n".encode('utf-8'))

        # Continuous listening loop for this specific client
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
                
            message = data.decode('utf-8')
            if message.lower() == 'quit':
                break
                
            # Broadcast the formatted message to everyone else
            formatted_msg = f"[{username}]: {message}"
            print(formatted_msg) # Log to server console
            broadcast(formatted_msg, sender_socket=client_socket)

    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        remove_client(client_socket)

def main():
    """Main server loop to accept incoming connections."""
    print("🚀 Central Chat Server is starting up...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        
        print(f"📡 Server is listening on {HOST}:{PORT}. Ready for users!")
        
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                # Spin up a new thread for each client so they don't block each other
                client_thread = threading.Thread(
                    target=handle_client, 
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\n🛑 Server shutting down by admin.")
        finally:
            # Clean close for all remaining sockets
            for client in list(clients.keys()):
                client.close()

if __name__ == "__main__":
    main()
