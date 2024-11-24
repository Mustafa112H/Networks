import socket
import random
import time
import threading
from clientObject import *

# Sample questions
questions = [
    {"text": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
    {"text": "What is the square root of 64?", "answer": "8"},
    {"text": "What year did World War II end?", "answer": "1945"},
    {"text": "What is the capital of Germany?", "answer": "Berlin"},
    {"text": "What is the smallest prime number?", "answer": "2"}
]

# Server configuration
serverPort = 6046
serverIP = socket.gethostbyname(socket.gethostname())

# Create a UDP socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((serverIP, serverPort))

# Declaring a list of client objects to keep track of active clients
activeClients = []

scores = {}
rounds_won = {}
round_number = 0

# Thread lock for thread-safe access to shared resources
lock = threading.Lock()

# Function to broadcast messages to all clients
def broadcast_message(message):
    for client in activeClients:
        serverSocket.sendto(message.encode(), client.address)

def play_round():
    global round_number
    round_number += 1
    print(f"\n--- Starting Round {round_number} ---")
    broadcast_message(f"--- Starting Round {round_number} ---")
    
    round_scores = {addr: 0 for addr in activeClients}
    selected_questions = random.sample(questions, 3)

    for q_index, question in enumerate(selected_questions):
        print(f"\nQuestion {q_index + 1}: {question['text']}")
        broadcast_message(f"Question {q_index + 1}: {question['text']}")

        # Collect answers for 30 seconds
        start_time = time.time()
        answered_clients = set()  # Track clients who have already answered
        timeout_clients = set()  # Track clients who timed out
        counter = 0

        while time.time() - start_time < 30:
            try:
                serverSocket.settimeout(1)  # Timeout for receiving answers
                data, addr = serverSocket.recvfrom(2048)

                if addr in activeClients and addr not in answered_clients:
                    answered_clients.add(addr)  # Mark client as having answered
                    answer = data.decode().strip()
                    correct = (answer.lower() == question['answer'].lower())

                    # Print and broadcast the client's answer
                    print(f"{activeClients[addr]} answered: '{answer}' (correct: {correct})")
                    

                    # If the answer is correct, increase the score
                    if correct:
                        round_scores[addr] += 1 - counter/len(activeClients)
                        counter+=1

            except socket.timeout:
                continue  # Timeout expired, continue checking until 30 seconds are up

        # After 30 seconds, mark clients who didn't answer
        for client in activeClients:
            if client not in answered_clients:
                timeout_clients.add(client)
                round_scores[client] += 0  # Treat their answer as "no answer"

        # After the 30 seconds, broadcast the correct answer
        broadcast_message(f"The correct answer was: {question['answer']}")

        # Short pause before broadcasting the updated leaderboard
        time.sleep(2)

    # After all questions, broadcast the leaderboard
    leaderboard = "\nCurrent Scores:\n" + "\n".join(
        [f"{activeClients[addr]}: {round_scores[addr]:.2f} points" for addr in activeClients]
    )
    broadcast_message(leaderboard)
    print(leaderboard)
    time.sleep(10)

    # Remove clients who didn't answer any questions in the round
    for client in timeout_clients:
        if client in activeClients:
            print(f"Removing client {activeClients[client]} due to inactivity.")
            del activeClients[client]
            del scores[client]
            del rounds_won[client]

    # Determine round winner(s)
    max_score = max(round_scores.values(), default=0)
    round_winners = [addr for addr, score in round_scores.items() if score == max_score]
    
    for addr in round_winners:
        rounds_won[addr] += 1
        scores[addr] += round_scores[addr]

    winner_names = ", ".join([activeClients[addr] for addr in round_winners])
    broadcast_message(f"Round {round_number} Winner(s): {winner_names} with {max_score:.2f} points!")
    print(f"Round {round_number} Winner(s): {winner_names} with {max_score:.2f} points!")

    # Announce overall winner
    max_rounds_won = max(rounds_won.values(), default=0)
    overall_winners = [addr for addr, wins in rounds_won.items() if wins == max_rounds_won]
    overall_winner_names = ", ".join([activeClients[addr] for addr in overall_winners])
    broadcast_message(f"Overall Leader: {overall_winner_names} with {max_rounds_won} rounds won!")
    print(f"Overall Leader: {overall_winner_names} with {max_rounds_won} rounds won!")
    time.sleep(3)  # Pause before starting the next round

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
            name, address = serverSocket.recvfrom(2048)
            # if not already active, append new client to the active list
            if not isClientActive(address):
                newClient = ClientObject(name.decode(), address)
                activeClients.append(newClient)
                
            
                # Create a child thread to take care of that client
                clientThread = threading.Thread(target=serviceClient, args=(newClient, ), daemon=True)
                clientThread.start()

                # Announce the new player
                broadcast_message(f"{newClient.name} has joined the game!\n Current number of players: {len(activeClients)}")
        except Exception as e:
            pass

# Function to listen to messages from each client
def serviceClient(client):
    print(f"{client.name} joined the game from {client.address}\n")
    

# Main function to carry out the server's logic
def main():
    print(f"Trivia Game server started and listening on ({serverIP}, {serverPort})")
    # Socket timeout to avoid blocking calls problem
    serverSocket.settimeout(5)

    # Creating a parent thread to handle clients while the game is on
    parentThread = threading.Thread(target=listenForClients, daemon=True)
    parentThread.start()

    # Main loop to start the game
    while True:
        # Start the game if at least two active clients
        if len(activeClients) >= 2:
            broadcast_message("The game will start in 90 seconds. New clients can join now!")
            print("\nThe game will start in 90 seconds. New clients can join now!\n")
            # Give players 90 seconds to perpare
            time.sleep(90) 

            # Starting the game
            play_round()
        else:
            time.sleep(5)
            print("Waiting for at least 2 clients to join the game...")

# Run main Function
main()
