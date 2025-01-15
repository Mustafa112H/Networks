import socket
import random
import time
import threading

# Sample questions
questions = [
    {"text": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
    {"text": "What is the square root of 64?", "answer": "8"},
    {"text": "What year did World War II end?", "answer": "1945"},
    {"text": "What is the capital of Germany?", "answer": "Berlin"},
    {"text": "What is the smallest prime number?", "answer": "2"}
]

# Server configuration
server_port = 5689
server_ip = socket.gethostbyname(socket.gethostname())

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

# Track active clients and scores
active_clients = {}
scores = {}
round_number = 0

# Thread lock for thread-safe access to shared resources
lock = threading.Lock()

# Event to stop listening for responses after 30 seconds
stop_event = threading.Event()
first_answer_received = threading.Event()  # To track the first answer

# Function to broadcast messages to all clients
def broadcast_message(message):
    for client in active_clients:
        server_socket.sendto(message.encode(), client)

def listen_for_client_answer(addr, question, round_scores):
    try:
        data, client_addr = server_socket.recvfrom(2048)
        if client_addr == addr and not stop_event.is_set():
            answer = data.decode().strip()
            correct = (answer.lower() == question['answer'].lower())

            if correct and not first_answer_received.is_set():
                first_answer_received.set()  # Mark that the first correct answer is received
                print(f"{active_clients[addr]} answered correctly: '{answer}'")
                broadcast_message(f"{active_clients[addr]} answered correctly!")
                round_scores[addr] += 1  # Increment score for the round
            elif correct:
                print(f"{active_clients[addr]} answered correctly: '{answer}' (but it's after the first correct answer)")
            else:
                print(f"{active_clients[addr]} answered incorrectly: '{answer}'")

    except Exception as e:
        print(f"Error receiving response from {addr}: {e}")

def play_round():
    global round_number
    round_number += 1
    print(f"\n--- Starting Round {round_number} ---")
    broadcast_message(f"--- Starting Round {round_number} ---")
    
    round_scores = {addr: 0 for addr in active_clients}
    selected_questions = random.sample(questions, 3)

    for q_index, question in enumerate(selected_questions):
        print(f"\nQuestion {q_index + 1}: {question['text']}")
        broadcast_message(f"Question {q_index + 1}: {question['text']}")

        stop_event.clear()  # Reset the stop event at the start of the question
        first_answer_received.clear()  # Reset the first answer flag

        # Start listening for answers from clients
        threads = []
        for addr in active_clients:
            thread = threading.Thread(target=listen_for_client_answer, args=(addr, question, round_scores))
            threads.append(thread)
            thread.start()

        # Wait for 30 seconds or until the first answer is received
        start_time = time.time()
        while time.time() - start_time < 30:
            if first_answer_received.is_set():  # If the first correct answer is received, stop accepting responses
                stop_event.set()  # Stop all threads
                break
            time.sleep(0.1)

        # Ensure all threads finish within the time limit
        for thread in threads:
            thread.join()

        # After 30 seconds or after the first answer, broadcast the correct answer
        broadcast_message(f"The correct answer was: {question['answer']}")

        # Short pause before broadcasting the updated leaderboard
        time.sleep(2)

        # Broadcast the leaderboard
        leaderboard = "\nCurrent Scores:\n" + "\n".join(
        [f"{active_clients[addr]}: {round_scores[addr]:.2f} points" for addr in active_clients]
        )
        broadcast_message(leaderboard)
        print(leaderboard)
        time.sleep(10)

    # Determine round winner(s)
    max_score = max(round_scores.values(), default=0)
    round_winners = [addr for addr, score in round_scores.items() if score == max_score]
    
    for addr in round_winners:
        scores[addr] += round_scores[addr]

    winner_names = ", ".join([active_clients[addr] for addr in round_winners])
    broadcast_message(f"Round {round_number} Winner(s): {winner_names} with {max_score:.2f} points!")
    print(f"Round {round_number} Winner(s): {winner_names} with {max_score:.2f} points!")

# Function to listen for new clients
def listen_for_new_clients():
    while True:
        try:
            # Listen for incoming messages from any client
            data, addr = server_socket.recvfrom(2048)
            with lock:  # Ensure thread-safe access to active_clients
                if addr not in active_clients:
                    client_name = data.decode().strip()
                    active_clients[addr] = client_name
                    scores[addr] = 0
                    print(f"\nNew client joined: {client_name} ({addr})\n")
                    broadcast_message(f"Welcome {client_name} to the trivia game!")
        except Exception as e:
            pass

def monitor_clients():
    while True:
        time.sleep(10)  # Check every 10 seconds
        with lock:
            if len(active_clients) < 2:
                print("\nLess than 2 players connected. Waiting for more players...\n")
                broadcast_message("Not enough players. Waiting for more players to join...")

                # Wait for 90 seconds to see if new players join
                time.sleep(90)

                # Check again if the number of players is still less than 2
                if len(active_clients) < 2:
                    print("Not enough players. Shutting down the server...")
                    broadcast_message("Not enough players. The server is shutting down.")
                    
                    # Close the server socket and exit
                    server_socket.close()
                    exit(0)  # Exit the program

# Server loop to accept clients and start the game
if __name__ == "__main__":
    print(f"Server is starting on {server_ip}:{server_port}")
    server_socket.settimeout(5)
    print("Server is ready and listening for clients...\n")

    # Start the client listening thread
    client_listener_thread = threading.Thread(target=listen_for_new_clients, daemon=True)
    client_listener_thread.start()
   # Start the client monitoring thread
    client_monitor_thread = threading.Thread(target=monitor_clients, daemon=True)
    client_monitor_thread.start()
    while True:
        if len(active_clients) >= 2:
            broadcast_message("The game will start in 90 seconds. New clients can join now!")
            print("\nThe game will start in 90 seconds. New clients can join now!\n")
            time.sleep(90)  # Wait for 90 seconds to accept new players

            # Start the round when at least 2 clients are connected
            play_round()
    
