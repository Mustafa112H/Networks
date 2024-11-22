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

# Track active clients, scores, and rounds won
active_clients = {}
scores = {}
rounds_won = {}
round_number = 0

# Thread lock for thread-safe access to shared resources
lock = threading.Lock()

# Function to broadcast messages to all clients
def broadcast_message(message):
    for client in active_clients:
        server_socket.sendto(message.encode(), client)

#def play_round():
    global round_number
    round_number += 1
    print(f"\n--- Starting Round {round_number} ---")
    broadcast_message(f"--- Starting Round {round_number} ---")
    
    round_scores = {addr: 0 for addr in active_clients}
    selected_questions = random.sample(questions, 3)

    active_participants = set()

    for q_index, question in enumerate(selected_questions):
        print(f"\nQuestion {q_index + 1}: {question['text']}")
        broadcast_message(f"Question {q_index + 1}: {question['text']}")

        # Collect answers for 30 seconds
        start_time = time.time()
        answers = []
        no_answer_clients = set(active_clients)  # Initially assume everyone hasn't answered
        answered_clients = set()  # Track clients who have already answered
        correct_answer_count = 0  # Track the order of correct answers

        while time.time() - start_time < 30:
            try:
                server_socket.settimeout(1)
                data, addr = server_socket.recvfrom(2048)

                if addr in active_clients and addr not in answered_clients:
                    answered_clients.add(addr)  # Mark client as having answered
                    no_answer_clients.discard(addr)  # Remove client from no-answer list
                    answer = data.decode().strip()
                    response_time = time.time() - start_time
                    correct = (answer.lower() == question['answer'].lower())
                    answers.append((addr, answer, response_time, correct))

                    # If the answer is correct, increase the correct_answer_count
                    if correct:
                        correct_answer_count +=1
                    round_scores[addr]+=(1-((correct_answer_count-1)/len(active_clients)))
                    print(f"{active_clients[addr]} answered: '{answer}' (correct: {correct})")
            except socket.timeout:
                continue

        # Mark clients who did not answer within the 30 seconds
        for addr in no_answer_clients:
            answers.append((addr, "nothing", 30, False))

        # Loop through the answers and assign points based on order of correct responses
        for addr, answer, _, correct in answers:
            if correct:  # Only process correct answers
                points = 1 - (correct_answer_count - 1) / len(active_clients) if correct_answer_count > 1 else 1
                round_scores[addr] += points

        # Broadcast the correct answer to all clients
        broadcast_message(f"The correct answer was: {question['answer']}")

        # Broadcast the updated leaderboard
        leaderboard = "\nCurrent Scores:\n" + "\n".join(
            [f"{active_clients[addr]}: {round_scores[addr]:.2f} points" for addr in active_clients]
        )
        broadcast_message(leaderboard)
        print(leaderboard)

        time.sleep(10)  # Wait before the next question

    # Determine round winner(s)
    max_score = max(round_scores.values(), default=0)
    round_winners = [addr for addr, score in round_scores.items() if score == max_score]
    
    for addr in round_winners:
        rounds_won[addr] += 1
        scores[addr] += round_scores[addr]

    winner_names = ", ".join([active_clients[addr] for addr in round_winners])
    broadcast_message(f"Round {round_number} Winner(s): {winner_names} with {max_score:.2f} points!")
    print(f"Round {round_number} Winner(s): {winner_names} with {max_score:.2f} points!")

    # Announce overall winner
    max_rounds_won = max(rounds_won.values(), default=0)
    overall_winners = [addr for addr, wins in rounds_won.items() if wins == max_rounds_won]
    overall_winner_names = ", ".join([active_clients[addr] for addr in overall_winners])
    broadcast_message(f"Overall Leader: {overall_winner_names} with {max_rounds_won} rounds won!")
    print(f"Overall Leader: {overall_winner_names} with {max_rounds_won} rounds won!")
    time.sleep(3)  # Pause before starting the next round


# Function to listen for new clients
def listen_for_new_clients():
    global active_clients
    while True:
        try:
            # Listen for incoming messages from any client
            data, addr = server_socket.recvfrom(2048)
            with lock:  # Ensure thread-safe access to active_clients
                if addr not in active_clients:
                    client_name = data.decode().strip()
                    active_clients[addr] = client_name
                    scores[addr] = 0
                    rounds_won[addr] = 0
                    print(f"\nNew client joined: {client_name} ({addr})\n")
                    broadcast_message(f"Welcome {client_name} to the trivia game!")
        except Exception as e:
            pass

# Server loop to accept clients and start the game
if __name__ == "__main__":
    print(f"Server is starting on {server_ip}:{server_port}")
    server_socket.settimeout(5)
    print("Server is ready and listening for clients...\n")

    # Start the client listening thread
    client_listener_thread = threading.Thread(target=listen_for_new_clients, daemon=True)
    client_listener_thread.start()

    while True:
        # Start game when at least 2 clients are connected
        if len(active_clients) >= 2:
            broadcast_message("The game will start in 90 seconds. New clients can join now!")
            print("\nThe game will start in 90 seconds. New clients can join now!\n")
            time.sleep(90)  # Wait for 90 seconds to accept new players

            # Start the round when at least 2 clients are connected
            play_round()
        else:
            time.sleep(5)
            print("Waiting for at least 2 players to join")
