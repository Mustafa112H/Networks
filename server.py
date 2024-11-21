import socket

# Basic server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 5689))  # Bind to port 5689
server_socket.listen(5)  # Listen for up to 5 connections
print("Server is listening on port 5689...")

# Function to determine MIME type
def get_mime_type(filename):
    if filename.endswith(".html"):
        return "text/html"
    elif filename.endswith(".css"):
        return "text/css"
    elif filename.endswith(".png"):
        return "image/png"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        return "image/jpeg"
    else:
        return "application/octet-stream"  # Default for unknown types

# Function to serve files
def serve_file(path, client_address):
    try:
        # Remove leading "/"
        if path.startswith("/"):
            path = path[1:]

        # Handle default to "main_en.html" for root or specific page requests
        if path == "" or path == "index.html" or path == "main_en.html" or path == "en":
            path = "html/main_en.html"
        elif path == "ar" or path == "main_ar.html":
            path = "html/main_ar.html"

        # Open and read the requested file
        with open(path, "rb") as file:
            content = file.read()

        # Determine MIME type
        mime_type = get_mime_type(path)

        # Send response with content
        response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n\r\n".encode()
        response += content
        return response

    except FileNotFoundError:
        # Return 404 if the file is not found
        error_message = f"""
        <html><head><title>Error 404</title></head><body>
        <h1>Error 404</h1>
        <p style='color: red;'>The file is not found</p>
        <p>Client IP: {client_address[0]}, Port: {client_address[1]}</p>
        </body></html>
        """
        status_line = "HTTP/1.1 404 Not Found\r\n"
        headers = "Content-Type: text/html\r\n\r\n"
        response = status_line + headers + error_message
        return response.encode()

# Accept client connections and serve files
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")
    
    # Receive the HTTP request (assuming a simple GET request)
    request = client_socket.recv(1024).decode()
    
    # Extract the file path from the request
    if request:
        request_line = request.splitlines()[0]
        requested_path = request_line.split(" ")[1]
        
        # Serve the file (or handle error if not found)
        response = serve_file(requested_path, client_address)
        
        # Send the response to the client
        client_socket.sendall(response)
    
    # Close the client socket after handling the request
    client_socket.close()


