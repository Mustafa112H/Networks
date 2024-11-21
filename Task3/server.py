from socket import *

# Port on which the server listens
serverPort = 6000
hostName = gethostname()
serverIP = gethostbyname(hostName)

# UDP socket creation
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Binding host address and port number
serverSocket.bind((serverIP, serverPort))

# serverSocket.listen(3)
print(f"Trivia Game server started and listening on ({serverIP}, {serverPort})\n")

# List of active clients on the server
activeClients = []

# Function to broadcast players in the game
def broadcast_players(name):
  message = f"{name} has joined the game!\n Current number of players: {len(activeClients)}"
  for client in activeClients:
    serverSocket.sendto(message.encode(), client)

while (True):
  # while (len(activeClients) < 2):
  #   print("Waiting for at least 2 clients to join the game . . .")
  clientName, clientIP = serverSocket.recvfrom(2048)
  # list client as active
  if clientIP not in activeClients:
    activeClients.append(clientIP)
    print(f"{clientName.decode()} joined the game from {clientIP}")
    welcomingMessage = f"Registered with Trivia Game server at IP {serverIP}, Port {serverPort}\n"
    if (len(activeClients) < 2):
      welcomingMessage += "Wainting for the game to start . . ."
    serverSocket.sendto(welcomingMessage.encode(), clientIP)
    broadcast_players(clientName.decode())
