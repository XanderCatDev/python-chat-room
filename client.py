import socket
import threading
import sys

# Configuration
HOST = input('IP?  : ')
PORT = 65432
BUFFER_SIZE = 1024

def receive_messages(client_socket):
    """Continuously listens for broadcasts from the server."""
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                print("\n❌ Disconnected from server.")
                break
            # Clear the current input line visual glitch, print msg, re-prompt
            sys.stdout.write(f"\r{data.decode('utf-8')}\nYou: ")
            sys.stdout.flush()
        except (ConnectionResetError, ConnectionAbortedError):
            print("\n❌ Connection to the server was lost.")
            break
        except Exception:
            break

def main():
    print("--- Welcome to the CLI Chat Board ---")
    username = input("Enter your username: ").strip()
    if not username:
        username = "Guest"

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        # Step 1: Handshake by sending the username first
        client_socket.sendall(username.encode('utf-8'))
    except ConnectionRefusedError:
        print("❌ Could not connect to the server. Is it running?")
        return

    # Background thread to handle incoming chatroom traffic
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    # Main thread handles your typing inputs
    try:
        while True:
            # We add a slight prompt visual. 
            message = input("You: ")
            if message.lower() == 'quit':
                client_socket.sendall('quit'.encode('utf-8'))
                break
            if message.strip(): # Don't send empty messages
                client_socket.sendall(message.encode('utf-8'))
    except KeyboardInterrupt:
        print("\n👋 Exiting chat.")
    finally:
        client_socket.close()
        print("Process finished.")

if __name__ == "__main__":
    main()
