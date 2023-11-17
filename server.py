import socket
import threading
from urllib.parse import urlparse

# Define the proxy server's listening address and port
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8888

# Dictionary to store cached responses
cache = {}

# Function to handle communication with the client
def handle_client(client_socket):
    # Receive the client's request
    request_data = client_socket.recv(4096)
    request = request_data.decode('utf-8')
    
    # Extract the request URL
    url = request.split(' ')[1]
    parsed_url = urlparse(url)
    
    # Check if the response is cached
    if url in cache:
        # If cached, send the cached response to the client
        cached_response = cache[url]
        client_socket.send(cached_response)
    else:
        # If not cached, connect to the destination server
        destination_host = parsed_url.netloc
        destination_port = 80
        destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        destination_socket.connect((destination_host, destination_port))
        
        # Forward the client's request to the destination server
        destination_socket.send(request_data)
        
        # Receive the response from the destination server
        destination_response = b""
        while True:
            response_data = destination_socket.recv(4096)
            if len(response_data) == 0:
                break
            destination_response += response_data
        
        # Send the response back to the client and cache it
        client_socket.send(destination_response)
        cache[url] = destination_response
        
        # Close the sockets
        client_socket.close()
        destination_socket.close()

# Main function for setting up the proxy server
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((PROXY_HOST, PROXY_PORT))
    server.listen(5)
    
    print(f'[*] Listening on {PROXY_HOST}:{PROXY_PORT}')
    
    while True:
        client_socket, addr = server.accept()
        print(f'[*] Accepted connection from {addr[0]}:{addr[1]}')
        
        # Create a thread to handle the client's request
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
