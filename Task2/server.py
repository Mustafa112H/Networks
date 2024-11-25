import os
import socket
# ENCS3320: Computer Networks course project
# Task 2
# Partners: 
#           Maysam Habbash 1220075, section: 1
#           Heba Mustafa 1221916, section: 1

#setting up the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 5689))  #connect with this scoket
server_socket.listen(6)  #listen to find connection
print("Server is listening on port 5689...")

#tell us the type of file
def gettype(filename):
    if filename.endswith(".html"):       
        return "text/html"    
    elif filename.endswith(".css"):
        return "text/css"
    elif filename.endswith(".png"):
        return "image/png"      
    elif filename.endswith(".jpg") or   filename.endswith(".jpeg"):
        return "image/jpeg"
    elif filename.endswith(".mp4"):
        return "video/mp4"
    else:
        return "application/octet-stream"  #Default for unknown types


#give us correct file so it opens the correct page 
def openfile(path, client_address):
    try:
        #remove /
        if path.startswith("/"):
            path = path[1:]

        #for the main page
        if path == "" or path == "index.html" or path == "main_en.html" or path == "en":
            path = "html/main_en.html"
        elif path == "ar" or path == "main_ar.html":
            path = "html/main_ar.html"
        elif path == "supporting_material_en.html":
            path = "html/supporting_material_en.html"
        elif path == "supporting_material_ar.html":
            path = "html/supporting_material_ar.html"

        #open the file that was requested
        with open(path, "rb") as file:
            content = file.read()

        # Determine type of file 
        type = gettype(path)

        # Send response with content
        response= f"HTTP/1.1 200 OK\r\nContent-Type: {type}\r\n\r\n".encode()
        response+= content             
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
        response = status_line +headers+error_message
        return response.encode()

#request support mat from here 
def materialreq(file_name, client_socket):
    #here the folders that we should check first before redirect
    img_fold = "imgs"
    vid_fold = "vids"
    
    #Check if the file is in the images folder
    if any(file_name.endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
        file_path = os.path.join(img_fold, file_name)
        if os.path.exists(file_path):
            #check if the image is int the folder else redirect
            response = openfile(file_path, client_socket.getpeername())
            client_socket.sendall(response)
            return
        search_url = f"https://www.google.com/search?q={file_name}&udm=2"
            #this will, send the redirect messgae
        status_line = "HTTP/1.1 307 Temporary Redirect\r\n"
        headers = f"Location: {search_url}\r\n\r\n"
        response = status_line.encode() + headers.encode()
        client_socket.sendall(response)
    
    # Check if the file is in the videos folder
    elif any(file_name.endswith(ext) for ext in [".mp4"]):
        file_path = os.path.join(vid_fold, file_name)
        if os.path.exists(file_path):
            #Serve the video file if it exists
            response = openfile(file_path, client_socket.getpeername())
            client_socket.sendall(response)
            return
        search_url = f"https://www.youtube.com/results?search_query={file_name}"
            #this will, send the redirect messgae
        status_line = "HTTP/1.1 307 Temporary Redirect\r\n"
        headers = f"Location: {search_url}\r\n\r\n"
        response = status_line.encode() + headers.encode()
        client_socket.sendall(response)
        
    else:
        #if the ext doesnt exist then show us an error
        response = openfile("/404", client_socket.getpeername())
        client_socket.sendall(response)
        return




#get the req and handle them
while True:
    client_socket, client_address=server_socket.accept()
    print(f"Connection from {client_address}")
    
    #recieve req
    request = client_socket.recv(1024).decode()
    
    #get the file path from the req
    if request:
           #Print the HTTP request details
        print("HTTP Request Received:")
        print(request)  
        request_line = request.splitlines()[0]
        requested = request_line.split(" ")[1]
        
        # Handle supporting material request
        if "/request_material" in requested:
            # Extract file name from query parameters
            query = requested.split("?")[1]
            file_name = query.split("=")[1]
            materialreq(file_name, client_socket)
        else:
            #Serve the file (or handle error if not found)
            response = openfile(requested,client_address)               
            client_socket.sendall(response)              
    
    # Close the client socket after handling the request
    client_socket.close()


