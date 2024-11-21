from socket import *
from questions import *
import random
import time

# Port on which the server listens
serverPort = 8000
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

# Function to broadcast questions
def broadcast_question(question, count):
  message = f"Question {count}: {question}\n Your answer (or type 'exit' to quit):"
  for client in activeClients:
    serverSocket.sendto(message.encode(), client)

# Function to select a number of questions
def selectQuestions():
  numberOfQuestion = 3
  selectedQuestions = random.sample(questions, numberOfQuestion)
  count = 0
  # Broadcast questions to playeres
  for i in selectedQuestions:
    count += 1
    if count > 1:
      time.sleep(60)
    print(f"Question {count}: {i}\n")
    broadcast_question(i, count)
    ###############################################################################################
    ################# You can start working from here, accepting answers from players ##################
    ###################################################################################################

# Function to start the game
def startGame():
  print("Starting the Trivia Game Round in 90 seconds!")
  time.sleep(90)

  # broadcasting a welcome message to notify clients that the round is about to start
  startingMessage = "Starting the Trivia Game  Round in 90 seconds! Get ready!"
  for client in activeClients:
    serverSocket.sendto(startingMessage.encode(), client)
    selectQuestions()

while (True):
  # Check minimum number of players
  if (len(activeClients) < 2):
    print("Waiting for at least 2 clients to join the game . . .")
  else:
    startGame()

  clientName, clientIP = serverSocket.recvfrom(2048)
  # list client as active
  if clientIP not in activeClients:
    activeClients.append(clientIP)

    print()
    print(f"{clientName.decode()} joined the game from {clientIP}")
    welcomingMessage = f"Registered with Trivia Game server at IP {serverIP}, Port {serverPort}\n Waiting for the game to start . . ."

    serverSocket.sendto(welcomingMessage.encode(), clientIP)
    broadcast_players(clientName.decode())
