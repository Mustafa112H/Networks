import os
import socket
from urllib.parse import urlparse, parse_qs
import urllib

# Constants for the server
HOST = 'localhost'
PORT = 5689

# Function to send HTTP response headers
def send_response(client_socket, status_code, content_type, location=None):
    client_socket.sendall(f"HTTP/1.1 {status_code}\r\n".encode())
    client_socket.sendall(f"Content-Type: {content_type}\r\n".encode())
    
    # If it's a redirect, include the Location header
    if location:
        client_socket.sendall(f"Location: {location}\r\n".encode())
    
    client_socket.sendall(b"Connection: close\r\n\r\n")

# Function to handle GET requests
def handle_get(client_socket, request_path):
    # Print request details for debugging
    print(f"Received request: {request_path}")
    
    # Redirect user based on requested file type
    if request_path.startswith("/request"):
        # Extract the file query parameter from the URL
        parsed_url = urlparse(request_path)
        query_params = parse_qs(parsed_url.query)
        file_name = query_params.get('file', [None])[0]
        
        if file_name:
            # Determine if it's an image or video
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                # Redirect to Google Images search if it's an image
                google_search_url = f"https://www.google.com/search?q={urllib.parse.quote(file_name)}&tbm=isch"
                send_response(client_socket, "307 Temporary Redirect", "text/html", google_search_url)
            
            elif file_name.lower().endswith(('.mp4', '.avi', '.mkv')):
                # Redirect to YouTube search if it's a video
                youtube_search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(file_name)}"
                send_response(client_socket, "307 Temporary Redirect", "text/html", youtube_search_url)
            
            else:
                # Unsupported file type, return error 400
                send_response(client_socket, "400 Bad Request", "text/html")
                client_socket.sendall(b"Unsupported file type. Please request an image or video.")
        
        else:
            # No file specified in the query
            send_response(client_socket, "400 Bad Request", "text/html")
            client_socket.sendall(b"File name is required in the query parameter.")
    
    elif request_path == "/":
        # Serve the main page (main_en.html)
        serve_file(client_socket, "html/main_en.html")
    
    elif request_path == "/en" or request_path == "/index.html" or request_path == "/main_en.html":
        # Serve the main page (main_en.html)
        serve_file(client_socket, "html/main_en.html")
    
    elif request_path == "/ar" or request_path == "/main_ar.html":
        # Serve the Arabic version of the main page
        serve_file(client_socket, "html/main_ar.html")
    
    else:
        # If file not found, send 404 error
        send_response(client_socket, "404 Not Found", "text/html")
        client_socket.sendall(b"Error 404: The file is not found.")

# Function to serve HTML files
def serve_file(client_socket, file_path):
    try:
        # Read the file and send the content as response
        with open(file_path, 'rb') as f:
            content = f.read()
        send_response(client_socket, "200 OK", "text/html")
        client_socket.sendall(content)
    except FileNotFoundError:
        send_response(client_socket, "404 Not Found", "text/html")
        client_socket.sendall(b"Error 404: The file is not found.")

# Function to start the server
def run_server():
    # Create and bind the socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server started on http://{HOST}:{PORT}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                # Receive the request from the client
                request = client_socket.recv(1024).decode()
                if request:
                    # Extract the requested path
                    request_line = request.splitlines()[0]
                    request_path = request_line.split()[1]
                    handle_get(client_socket, request_path)

if __name__ == "__main__":
    run_server()