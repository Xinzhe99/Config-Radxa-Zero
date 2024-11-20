import os
import socket


class ImageReceiver:
    def __init__(self, host, port, save_dir, max_wait_time=30):
        """
        Initialize the image receiver

        Args:
            host (str): Host IP to bind to
            port (int): Port number to listen on
            save_dir (str): Directory to save received images
            max_wait_time (int): Maximum time to wait for data in seconds
        """
        self.host = host
        self.port = port
        self.save_dir = save_dir
        self.max_wait_time = max_wait_time
        self.stop_event = False
        os.makedirs(save_dir, exist_ok=True)

    def start(self):
        """Start the image receiver server"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((self.host, self.port))
                server_socket.listen(1)
                print(f"Server listening on {self.host}:{self.port}")

                while not self.stop_event:
                    try:
                        server_socket.settimeout(1.0)  # Allow checking stop_event periodically
                        client_socket, client_address = server_socket.accept()
                        self._handle_client(client_socket, client_address)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"Error accepting connection: {e}")

        except Exception as e:
            print(f"Server error: {e}")
        finally:
            print("Server stopped")

    def _handle_client(self, client_socket, client_address):
        """Handle individual client connections"""
        try:
            with client_socket:
                print(f"Connection from {client_address}")
                client_socket.settimeout(self.max_wait_time)

                # Receive file name length and name
                name_length = int.from_bytes(client_socket.recv(4), byteorder='big')
                file_name = client_socket.recv(name_length).decode()

                # Receive file size
                file_size = int.from_bytes(client_socket.recv(8), byteorder='big')

                # Prepare file path
                save_path = os.path.join(self.save_dir, file_name)

                # Receive and save file
                received_size = 0
                with open(save_path, 'wb') as f:
                    while received_size < file_size:
                        bytes_left = file_size - received_size
                        chunk_size = min(8192, bytes_left)
                        data = client_socket.recv(chunk_size)
                        if not data:
                            raise Exception("Connection closed prematurely")
                        f.write(data)
                        received_size += len(data)

                # Send confirmation
                client_socket.sendall(b'OK')
                print(f"Successfully saved image to {save_path}")

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            try:
                client_socket.sendall(b'ER')
            except:
                pass

    def stop(self):
        """Stop the server"""
        self.stop_event = True


# Example usage of server
if __name__ == '__main__':
    # Server configuration\

    SERVER_HOST = '10.92.201.113'
    SERVER_PORT = 11111
    SAVE_DIR = r'C:\Users\dell\Desktop\Working\配置瑞莎系统\code\test_dir'

    # Create and start server
    server = ImageReceiver(SERVER_HOST, SERVER_PORT, SAVE_DIR)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()