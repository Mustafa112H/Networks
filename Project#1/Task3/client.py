# ENCS3320: Computer Networks course project
# Task 3 – UDP Client-Server Trivia Game Using Socket Programming
# Partners: 
#           Maysam Habbash 1220075, section: 1
#           Heba Mustafa 1221916, section: 1

from socket import *

# UDP client socket creation
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Prompting the user to enter server info for connection
serverIP = input('Enter the server IP address: ')
serverPort = int(input('Enter the server port number: '))
clientName = input('Enter your name: ')

# Connection with the server
def connectWithServer(serverIP, serverPort):
    # Send client name to the server to register
    clientSocket.sendto(clientName.encode(), (serverIP, serverPort))

    while True:
        try:
            # Receive and print messages from the server
            message, _ = clientSocket.recvfrom(2048)
            print(message.decode())

            # Check if the message is a question or other game instruction
            if "Question" in message.decode():
                # Prompt for an answer when a question is received
                answer = input("Enter your answer (or type 'exit' to quit): ")

                # Send answer to the server
                if answer.lower() == 'exit':
                    clientSocket.sendto("exit".encode(), (serverIP, serverPort))
                    print("Exiting the game...")
                    break

                clientSocket.sendto(answer.encode(), (serverIP, serverPort))

            elif "The game has ended" in message.decode():
                print("\nThe game has ended. Thank you for playing!")
                break

        except Exception as e:
            print(f"Error: {e}")
            break

    clientSocket.close()

# Call the function to start the connection and game
connectWithServer(serverIP, serverPort)
