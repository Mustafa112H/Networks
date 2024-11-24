# ENCS3320: Computer Networks course project
# Task 3 – UDP Client-Server Trivia Game Using Socket Programming
# Partners: 
#           Maysam Habbash 1220075, section: 1
#           Heba Mustafa 1221916, section: 1

import socket
import random
import time
import threading
from clientObject import *
import json
import queue

# Sample questions
questions = [
    {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
    {"question": "What is the square root of 64?", "answer": "8"},
    {"question": "What year did World War II end?", "answer": "1945"},
    {"question": "What is the capital of Germany?", "answer": "Berlin"},
    {"question": "What is the smallest prime number?", "answer": "2"}
]

# Loading data from JSON file into a dictionary
with open('gameSettings.json', 'r') as jsonFile:
    config = json.load(jsonFile)

# Server configuration
serverPort = 5689
serverIP = socket.gethostbyname(socket.gethostname())

# Create a UDP socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((serverIP, serverPort))

# Declaring a list of client objects to keep track of active clients
activeClients = []
# Declaring a queue to store client's answers before correction
answersQueue = queue.Queue()
tempQueue = queue.Queue()

# Thread lock for thread-safe access to shared resources
lock = threading.Lock()

# Function to broadcast messages to all clients
def broadcastMessage(message):
    for client in activeClients:
        serverSocket.sendto(message.encode(), client.address)

# Function to calculate and broadcast scores
def broadcastScores(correctAnswersCount):
    correct = 0
    temp = correctAnswersCount
    # Iterate through answers
    for i in range(tempQueue.qsize()):
        address, _ = tempQueue.get()
        for client in activeClients: 
            # Acknowledge client
            if (client.address == address):
                if client.isCorrect == True:
                    # First client to answer correctly
                    correct += 1
                    if (correct) == 1:
                        client.score += 1
                    else:
                        temp -= 1
                        client.score += (temp)/correctAnswersCount
    # brodcast scores
    broadcastMessage("Current scores:")
    for client in activeClients:
        broadcastMessage(f"\t* {client.name}: {client.score} points")

def resetInRound():
    # Reset clients' answering status
    for client in activeClients:
        client.hasAnswered = False
        client.isCorrect = False

# Function to collect answers from clients
def collectAnswers(question, startTime):
    correctAnswersCount = 0
    # Keep collecting answers for specific amount of time
    while time.time() - startTime < int(config['answerCollectionTime']):
        if answersQueue.qsize() > 0:
            # retrieve answers in order
            address, answer = answersQueue.get()
            for client in activeClients:
                if client.address == address:
                    # determine correctness of the answer
                    status = "Incorrect!"
                    if answer.lower() == question['answer'].lower():
                        correctAnswersCount += 1
                        status = "Correct!"
                        client.isCorrect = True
                    print(f"Received answer from {client.name} {client.address}: {answer} - {status}\n")

    print("Time's up!\n")
    broadcastMessage(f"Time's up! The correct answer was: {question['answer']}\n")
    broadcastScores(correctAnswersCount)
    resetInRound()

# Function to start a round in the game
def startRound():
    # Select random questions to display
    selectedQuestions = random.sample(questions, int(config['numberOfQuestions']))

    # Iterate through selected questions
    for index, question in enumerate(selectedQuestions, start=1):
        print(f"Question {index}: {question['question']}")
        broadcastMessage(f"\nQuestion {index}: {question['question']}")
        startTime = time.time()

        # Create a thread to handle answer collection
        # collectionThread = threading.Thread(target=collectAnswers,args=(startTime, ) daemon=True)
        # collectionThread.start()
        collectAnswers(question, startTime)
        time.sleep(int(config['waitingBetweenQuestionsTime']))
    
    # End round
    broadcastMessage("GAME OVER!")
    # Announce winner
        #round Winner   
    maxScore = 0
    for client in activeClients:
        if client.score > maxScore:
            maxScore = client.score
            roundWinner = client
    roundWinner.roundsWon += 1

        # max rounds winner
    maxRoundWins = 0
    for client in activeClients:
        if client.roundsWon > maxRoundWins:
            maxRoundWins = client.roundsWon
            winner = client

        # disconnect inactive clients
        if client.score == 0:
            serverSocket.sendto("The game has ended".encode(), client.address)
            activeClients.remove(client)
        # reset score
        client.score = 0
    broadcastMessage(f"The winner is {winner.name} with {winner.roundsWon} rounds! Congratulations!")

# Function to start the game
def startGame():
    for i in range(int(config['numberOfRounds'])):
        print(f"\t--- Round {i+1} ---")
        broadcastMessage(f"\t--- Round {i+1} ---")
        # Start the round
        startRound()

        # not last round
        if i != int(config['numberOfRounds'])-1:
            # allowing players time to review the leaderboard and prepare for the next round
            print(f"Next round will start in {config['waitingBetweenRoundsTime']} seconds")
            broadcastMessage(f"Next round will start in {config['waitingBetweenRoundsTime']} seconds")
            time.sleep(int(config['waitingBetweenRoundsTime']))
    # end game
    broadcastMessage("The game has ended")
    for i in activeClients:
        activeClients.remove(i)

# Function to check if a client is active before appending to the list
def isClientActive(address):
    for client in activeClients:
        if client.address == address:
            return True
    return False

# Function to listen for new clients and assign a child thread to each
def listenForClients():
    while True:
        try:
            # Listen for incoming messages from any client
            message, address = serverSocket.recvfrom(2048)
            # if not already active, append new client to the active list
            if not isClientActive(address):
                newClient = ClientObject(message.decode(), address)
                activeClients.append(newClient)
                
                # Announce the new player
                print(f"{newClient.name} joined the game from {newClient.address}\n")
                broadcastMessage(f"\n{newClient.name} has joined the game!\n Current number of players: {len(activeClients)}")
            else:
                # Create a child thread to take care of that client
                clientThread = threading.Thread(target=serviceClient, args=(message, address, ), daemon=True)
                clientThread.start()
        except Exception as e:
            pass

# Function to listen to messages from each client
def serviceClient(answer, address):
    # Acknowledge client from address
    for client in activeClients:
        if client.address == address:
            # accept answer if not a duplicate
            if ( answer.decode() and client.hasAnswered != True):
                # change state
                client.hasAnswered = True
                # Enqueue answer
                answersQueue.put((address, answer.decode()))
                tempQueue.put((address, answer.decode()))
                serverSocket.sendto(f"Answer submitted: {answer.decode()}".encode(), address)
    

# Main function to carry out the server's logic
def main():
    print(f"Trivia Game server started and listening on ({serverIP}, {serverPort})")
    # Socket timeout to avoid blocking calls problem
    serverSocket.settimeout(5)

    # Creating a parent thread to handle clients while the game is on
    parentThread = threading.Thread(target=listenForClients, daemon=True)
    parentThread.start()
    # listenForClients()

    # Main loop to start the game
    while True:
        # Start the game if at least two active clients
        if len(activeClients) >= 2:
            broadcastMessage("\nThe game will start in 90 seconds. New clients can join now!")
            print("\nThe game will start in 90 seconds. New clients can join now!\n")
            # Give players 90 seconds to perpare
            time.sleep(30) 

            # Starting the game
            startGame()
        else:
            time.sleep(5)
            print("Waiting for at least 2 clients to join the game...")

# Run main Function
main()
