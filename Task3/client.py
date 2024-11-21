import socket
import time
from threading import Thread

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5689
USERNAME = "Player 1"

# UDP client setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_message(message):
    try:
        client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"Error sending message: {e}")

def receive_message():
    while True:
        try:
            message, server_address = client_socket.recvfrom(1024)
            print(f"Received message: {message.decode()} from {server_address}")
        except OSError as e:
            print(f"Error receiving message: {e}")
            break

def game_loop():
    print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
    send_message(USERNAME)
    
    # Game loop
    while True:
        # Listening for game messages (questions, scores, etc.)
        time.sleep(1)

if __name__ == "__main__":
    # Start the message receiving thread
    receive_thread = Thread(target=receive_message)
    receive_thread.start()
    
    # Start the game loop
    game_loop()
