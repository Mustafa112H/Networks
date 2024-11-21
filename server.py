import socket

HOST = ""  # Empty string means to listen on all available interfaces
PORT = 5689

# MIME Types for Static Files
MIME_TYPES = {
    "html": "text/html",
    "css": "text/css",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "js": "application/javascript",
    "gif": "image/gif",
    "mp4": "video/mp4",
}

# Function to determine MIME type
def get_mime_type(filename):
    extension = filename.split('.')[-1]
    return MIME_TYPES.get(extension, "application/octet-stream")

# Function to handle static requests (files)
def handle_static_request(path):
    try:
        # Strip leading '/' to get the file path
        file_path = path.lstrip("/")
        
        # Check if the file exists
        with open(file_path, 'rb') as file:
            content = file.read()
        
        # Determine MIME type
        mime_type = get_mime_type(file_path)
        return f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n\r\n".encode() + content

    except FileNotFoundError:
        # Handle file not found (404)
        return (f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
                f"<html><body><h1>404 Not Found</h1>"
                f"<p>The requested file was not found on the server.</p></body></html>").encode()

# Function to handle the material request (images/videos)
def handle_material_request(file_name):
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        redirect_url = f"https://www.google.com/search?q={file_name.replace(' ', '+')}&udm=2"
    elif file_name.lower().endswith(('.mp4', '.avi', '.mov')):
        redirect_url = f"https://www.youtube.com/results?search_query={file_name.replace(' ', '+')}"
    else:
        return (f"HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                f"<html><body><h1>400 Bad Request</h1>"
                f"<p>Invalid file type requested.</p></body></html>").encode()

    # Redirect to the appropriate URL (Google Images or YouTube)
    return (f"HTTP/1.1 307 Temporary Redirect\r\nLocation: {redirect_url}\r\n\r\n").encode()

# Main function to handle incoming requests
def handle_request(request, client_address):
    print(f"Request from {client_address}:\n{request}\n")
    
    try:
        headers, _, body = request.partition('\r\n\r\n')
        first_line = headers.split('\r\n')[0]
        method, path, http_version = first_line.split(' ')

        if method == "GET":
            if path == "/":
                path = "main_en.html"  # Default root file
            elif path == "/en":
                path = "main_en.html"
            elif path == "/supporting_material_en.html":
                path = "supporting_material_en.html"
            elif path.startswith("/request_material"):
                # Extract query parameters from the URL
                file_name = path.split('?')[-1].split('=')[-1] if '?' in path else ''
                return handle_material_request(file_name)
            else:
                # Try to handle static files
                return handle_static_request(path)
        else:
            # Unsupported method or missing handler for POST, etc.
            return (f"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n"
                    f"<html><body><h1>405 Method Not Allowed</h1></body></html>").encode()

    except Exception as e:
        return (f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n"
                f"<html><body><h1>500 Internal Server Error</h1>"
                f"<p>{e}</p></body></html>").encode()

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Listening on port {PORT}...")

# Server loop to handle incoming requests
while True:
    client_connection, client_address = server_socket.accept()
    request = client_connection.recv(1024).decode()

    if request:
        response = handle_request(request, client_address)
        client_connection.sendall(response)
    
    client_connection.close()
