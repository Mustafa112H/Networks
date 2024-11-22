import socket
import random
import time

# Define the questions and correct answers
questions = [
    {"text": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
    {"text": "What is the square root of 64?", "answer": "8"},
    {"text": "What year did World War II end?", "answer": "1945"},
    {"text": "What is the capital of Germany?", "answer": "Berlin"},
    {"text": "What is the smallest prime number?", "answer": "2"}
]

# Server settings
server_port = 5689

# Get the actual IP address of the server (excluding localhost)
server_ip = socket.gethostbyname(socket.gethostname())

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

# Track active clients, their scores, and rounds won
active_clients = {}
scores = {}  # Track scores separately
rounds_won = {}  # Track the number of rounds won by each client
round_number = 0  # Track the number of rounds

# Function to broadcast messages to all active clients
def broadcast_message(message):
    for client in active_clients:
        server_socket.sendto(message.encode(), client)

# Function to handle client responses and play a round of trivia
def play_round():
    global round_number
    round_number += 1
    print(f"Round {round_number} is starting!")
    broadcast_message(f"Round {round_number} is starting! Good luck!")
    
    # Reset round-specific scores
    round_scores = {addr: 0 for addr in active_clients}

    # Randomly select questions
    selected_questions = random.sample(questions, 3)
    
    for q_index, question in enumerate(selected_questions):
        broadcast_message(f"Question {q_index + 1}: {question['text']}")

        # Collect answers for 60 seconds
        start_time = time.time()
        answers = {}

        while time.time() - start_time < 60:
            try:
                server_socket.settimeout(1)
                data, addr = server_socket.recvfrom(2048)
                
                # Register new clients based on the address
                if addr not in active_clients:
                    active_clients[addr] = data.decode()  # Save the client's name
                    scores[addr] = 0  # Initialize their total score
                    rounds_won[addr] = 0  # Initialize rounds won
                    print(f"New client joined: {addr} - {data.decode()}")

                answer = data.decode().strip()
                if addr not in answers:  # Only accept the first answer
                    answers[addr] = answer
                    client_name = active_clients[addr]  # Get the client name
                    print(f"Received answer from {client_name} ({addr}): '{answer}'")
            except socket.timeout:
                continue

        # Validate answers and update round scores
        correct_answer = question["answer"].lower()
        broadcast_message(f"The correct answer was: {correct_answer}")
        
        for addr, answer in answers.items():
            client_name = active_clients[addr]  # Get client name
            if answer.lower() == correct_answer:
                print(f"{client_name} answered '{answer}' correctly!")
                round_scores[addr] += 1  # Update round score for correct answer
            else:
                print(f"{client_name} answered '{answer}' incorrectly.")

    # Determine the round winner(s)
    max_score = max(round_scores.values(), default=0)
    round_winners = [addr for addr, score in round_scores.items() if score == max_score]

    for addr in round_winners:
        rounds_won[addr] += 1  # Increment rounds won for the winner
        scores[addr] += round_scores[addr]  # Add round score to total score

    # Announce round winner(s)
    winner_names = ", ".join([active_clients[addr] for addr in round_winners])
    broadcast_message(f"The winner of Round {round_number} is: {winner_names} with {max_score} points!")
    print(f"The winner of Round {round_number} is: {winner_names} with {max_score} points!")

    # Show current leaderboard
    leaderboard = "Current Leaderboard:\n" + "\n".join(
        [f"{active_clients[addr]}: {scores[addr]} points, {rounds_won[addr]} rounds won" for addr in scores]
    )
    broadcast_message(leaderboard)
    print(leaderboard)

    # Wait a moment before starting the next round
    time.sleep(2)

# Server loop to handle new clients and start game rounds
if __name__ == "__main__":
    print(f"Server is starting on {server_ip}:{server_port}")
    print("Server is ready and listening for clients...\nwaiting for at least 2 clients...")
    server_socket.settimeout(1)
    while True:
        # Handle new client connections dynamically
        try:
            data, addr = server_socket.recvfrom(2048)
            if addr not in active_clients:
                active_clients[addr] = data.decode()  # Register the new client
                scores[addr] = 0  # Initialize total score
                rounds_won[addr] = 0  # Initialize rounds won
                print(f"New client joined: {addr} - {data.decode()}")

                # Send a welcome message to the new client
                server_socket.sendto("Welcome to the trivia game!".encode(), addr)
                broadcast_message(f"A new player has joined the game: {data.decode()}")
        except Exception as e:
            pass

        # Start a new round if there are at least 2 clients
        if len(active_clients) >= 2:
            broadcast_message("The round will start after 90 seconds. New clients can join now.")
            print("The round will start after 90 seconds. New clients can join now.")

            # Wait for 90 seconds to accept new players
            t_end = time.time() + 90 
            while time.time() < t_end:
                try:    
                    data, addr = server_socket.recvfrom(2048)
                    if addr not in active_clients:
                        active_clients[addr] = data.decode()  # Register the new client
                        scores[addr] = 0  # Initialize total score
                        rounds_won[addr] = 0  # Initialize rounds won
                        print(f"New client joined: {addr} - {data.decode()}")

                        # Send a welcome message to the new client
                        server_socket.sendto("Welcome to the trivia game!".encode(), addr)
                        broadcast_message(f"A new player has joined the game: {data.decode()}")
                except:
                    pass
            # Start the round after 90 seconds
            play_round()
