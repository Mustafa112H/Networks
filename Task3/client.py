from socket import *

# UDP client socket creation
clientSocket =socket(AF_INET, SOCK_DGRAM)

# Prompting the user to enter server info for connection
serverIP = input('Enter the server IP address: ')
serverPort = int(input('Enter the server port number: '))
clientName = input('Enter your name: ')

# Connection with server
def connectWithServer():
  clientSocket.sendto(clientName.encode(), (serverIP, serverPort))
  # Receive massages from server
  welcomingMessage, serverIP = clientSocket.recvfrom(2048)
  gameStatus, serverIP = clientSocket.recvfrom(2048)

  print()
  print(welcomingMessage.decode())
  print()
  print(gameStatus.decode())

connectWithServer()

clientSocket.close()