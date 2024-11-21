import socket
import random
import time
from threading import Thread

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5689
MIN_CLIENTS = 2
QUESTION_TIME = 90  # seconds
PREPARE_TIME = 60  # seconds
NUM_QUESTIONS = 3

# Sample questions and answers (a dictionary for simplicity)
QUESTIONS = [
    ("What is the capital of France?", "Paris"),
    ("Who wrote 'Hamlet'?", "Shakespeare"),
    ("What is the largest ocean?", "Pacific"),
    ("Who discovered America?", "Columbus")
]

# Game state
clients = {}
scores = {}

# UDP server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

def broadcast_message(message):
    for client in clients:
        server_socket.sendto(message.encode(), client)

def handle_client(client_address, message):
    print(f"Received message from {client_address}: {message}")
    # Add logic to handle answers and other messages

def start_round():
    if len(clients) >= MIN_CLIENTS:
        print("Starting round with enough players...")
        broadcast_message("Round is starting!")
        for i in range(NUM_QUESTIONS):
            question, correct_answer = random.choice(QUESTIONS)
            broadcast_message(f"Question {i+1}: {question}")
            time.sleep(PREPARE_TIME)
            start_time = time.time()

            while time.time() - start_time < QUESTION_TIME:
                # Wait for answers
                pass
            
            # Evaluate answers
            # Broadcast correct answer and scores
            broadcast_message(f"The correct answer was: {correct_answer}")
            time.sleep(5)  # Pause between questions
        # End of round, announce winner
        announce_winner()

def announce_winner():
    winner = max(scores, key=scores.get)
    print(f"The winner of this round is {winner}!")
    broadcast_message(f"The winner is {winner}! Well done.")

def server_loop():
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    while True:
        message, client_address = server_socket.recvfrom(1024)
        if client_address not in clients:
            clients[client_address] = "Player " + str(len(clients)+1)
            scores[client_address] = 0
            print(f"New client connected: {client_address}")
        
        handle_client(client_address, message.decode())

if __name__ == "__main__":
    round_thread = Thread(target=start_round)
    round_thread.start()
    server_loop()
