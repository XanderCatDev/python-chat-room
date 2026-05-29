import socket
import threading

# Configuration
HOST = '192.168.1.22'
PORT = 1023      # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 1024

def handle_client(conn, addr):
    """Handles receiving messages from the client and sending responses."""
    print(f"**Connected by {addr}**")
    try:
        # Start a thread to continuously receive messages
        receive_thread = threading.Thread(target=receive_messages, args=(conn,))
        receive_thread.daemon = True
        receive_thread.start()

        # Main thread handles sending messages
        while True:
            message = input("You: ")
            if message.lower() == 'quit':
                conn.sendall('Partner has disconnected.'.encode('utf-8'))
                break
            conn.sendall(message.encode('utf-8'))

    except (ConnectionResetError, BrokenPipeError):
        print("\n**Client disconnected unexpectedly.**")
    except EOFError:
        print("\n**Server is shutting down.**")
    finally:
        conn.close()

def receive_messages(conn):
    """Continuously receives and prints messages from the client."""
    while True:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                print("\n**Partner has left the chat.**")
                break
            print(f"\nPartner: {data.decode('utf-8')}")
        except:
            break

def main():
    """Sets up the server socket and listens for connections."""
    print("Starting chat server...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Allows reuse of the port even if a previous connection was abruptly closed
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on {HOST}:{PORT}. Waiting for a client to connect...")
        
        try:
            conn, addr = s.accept()
            handle_client(conn, addr)
        except KeyboardInterrupt:
            print("\n**Server shut down by user.**")
        finally:
            print("**Server process finished.**")

if __name__ == "__main__":
    main()
