import socket

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
        <html><body>
        <h1>Error 404</h1>
        <p style='color: red;'>The file is not found</p>
        <p>Client IP: {client_address[0]}, Port: {client_address[1]}</p>
        </body></html>
        """
        response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n{error_message}"
        return response.encode()

# Basic server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 5689))  # Bind to port 5689
server_socket.listen(5)  # Listen for up to 5 connections
print("Server is listening on port 5689...")

# Main server loop
while True:
    client_connection, client_address = server_socket.accept()
    request = client_connection.recv(1024).decode()

    if request:
        print(f"Request from {client_address}:\n{request}")  # Log request for debugging

        # Parse the request
        try:
            request_line = request.split("\r\n")[0]
            method, path, _ = request_line.split(" ")

            # Handle GET requests
            if method == "GET":
                response = serve_file(path, client_address)
            else:
                # Method not allowed
                response = (f"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n"
                            f"<html><body><h1>405 Method Not Allowed</h1></body></html>").encode()

        except Exception as e:
            # Internal server error
            response = (f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n"
                        f"<html><body><h1>500 Internal Server Error</h1>"
                        f"<p>{e}</p></body></html>").encode()

        client_connection.sendall(response)

    client_connection.close()
