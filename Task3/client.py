from socket import *

# UDP client socket creation
clientSocket =socket(AF_INET, SOCK_DGRAM)

# Prompting the user to enter server info for connection
serverIP = input('Enter the server IP address: ')
serverPort = int(input('Enter the server port number: '))
clientName = input('Enter your name: ')


# Connection with server
def connectWithServer(serverIP, serverPort):
  clientSocket.sendto(clientName.encode(), (serverIP, serverPort))

  while (True):
    # Receive and print massages from server
    message, serverIP = clientSocket.recvfrom(2048)
    print()
    print(message.decode())
    
connectWithServer(serverIP, serverPort)

# clientSocket.close()