import socket  # for communication with the server
import chatlib  # To use chatlib functions or consts, use chatlib.****
import random   # for random compliments

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 6000

CLIENT_OPTIONS = ["Play", "Get Score", "LeaderBoard", "Logged Users", "Logout"]
# HELPER SOCKET METHODS

compliments = ["Well Done!", "Pure Genius!", "Good One!", "So Sharp!", "Amazing!", "Let's Go!"]

def build_and_send_message(conn, command_code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: nothing
    """
    message = chatlib.build_message(command_code, data)
    conn.send(message.encode())
    # Debug Info
    # print("-----------------------------")
    # print("We Sent The Server: \n" + message)


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    message_gotten = conn.recv(16384).decode()
    # Debug Info
    # print("-----------------------------")
    # print("The Server Sent Us: \n" + message_gotten)
    # parse the message using chatlib
    command_code, msg_data = chatlib.parse_message(message_gotten)

    # check for problems when getting a message
    if command_code is None or msg_data is None:
        error_and_exit("An error occurred while trying to get a message headers, None Values")

    return command_code, msg_data


def build_send_recv_parse(conn, command_code_sent, data):
    """
    a function that sends a message to the server and gets its response
    :param conn: socket connected to the server
    :param command_code: the name of the command we want to commit
    :param data: the data of the message
    :return: command_code: the command code of the response from the server data: the data of the response
    """
    # build and send the message
    build_and_send_message(conn, str(command_code_sent), str(data))
    # get the response from the server and extract the command and the data
    command_code_got, data = recv_message_and_parse(conn)
    # check for error respone from the server - and exit, except for failed attempt to login
    if command_code_got == chatlib.PROTOCOL_SERVER["error_msg"]:
        print("-----------------------------")
        print(f'Request Failed: {data}')
    return command_code_got, data


def connect():
    """
    creates a socket for the client for passing messages to the server
    :return: socket connected to the Trivia server
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))

    return sock


def error_and_exit(msg):
    """
    when error occurs the function finishes the program and prints the error message
    :param msg: error message
    :return: nothing
    """
    print(msg)
    exit()

def dont_have_special_keys(value):
    """
    the function checks that the string includes only letters between a to z or A to Z or numbers
    :param value: username or password
    :return: true if there are special keys else false
    """
    for i in value:
        if not(i.isdigit() or i.isalpha()):
            return False
    return True

def login(conn):
    """
    the function gets username and password builds a message according to the Protocol. tries to login, while login don't it requests again
    :param conn - socket connected to server:
    :return - finishes function:
    """
    # loop - as login failed asks again for username and password
    while True:
        # input from client
        print("-----------------------------")
        username = input("Please enter username: \n")
        while not dont_have_special_keys(username):
            print("-----------------------------")
            username = input("username can include only letters or numbers, please try again:\n")
        print("-----------------------------")
        password = input("Please enter password: \n")
        while not dont_have_special_keys(password):
            print("-----------------------------")
            password = input("Password can include only letters or numbers, please try again:\n")

        # create the data for login message
        message_data = username + "#" + password
        # build message using chatlib
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], message_data)
        # recieved answer from server
        command_code, message_gotten_data = recv_message_and_parse(conn)

        # cheking if login succeeded
        if command_code == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            print("-----------------------------")
            print(f'Logged in as: {username} :)')
            return

        # the login failed request the user for username and password again
        elif command_code == chatlib.PROTOCOL_SERVER["error_msg"]:
            print("-----------------------------")
            print(f"{message_gotten_data} \nTry Again!")

        else:
            print("-----------------------------")
            error_and_exit(f"Unexpected Error :(")


def logout(conn):
    """
    function disconnects client from server
    :param conn - socket connected to server:
    :return:
    """
    # build the logout message and send the message to the server
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")

    print("-----------------------------")
    print("Logged OUT! Take Care :)")


def get_score(conn):
    """
    builds MY_SCORE command sends the message and gets the score using build send get parse
    :param conn: socket
    :return: nothing
    """
    command_code, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_score_msg"], "")
    if command_code == chatlib.PROTOCOL_SERVER["user_score_msg"]:
        print("-----------------------------")
        print(f'Your Score is: {data}')

    # the server sent error, stop function
    elif command_code == chatlib.PROTOCOL_SERVER["error_msg"]:
        return

    else:
        print("-----------------------------")
        error_and_exit(f"Unexpected Error :(")


def play_question(conn):
    """
    the function shows the player the trivia question than waits for the answer
    :param conn: socket connected to server
    :return:
    """
    # ask the server for question
    command_code, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_question_msg"], "")
    # check the command we got
    if command_code == chatlib.PROTOCOL_SERVER["no_questions_msg"]:
        print("-----------------------------")
        print(f'WOW! You have answered all the questions, you better find something better to do with your life...')
        return

    # we got question
    elif command_code == chatlib.PROTOCOL_SERVER["your_question_msg"]:
        # split the data off the message we got from the server
        data_arr = data.split("#")
        # extract the id of the question
        id = data_arr[0]
        # extrct the question
        question = data_arr[1]
        # extract the options
        answer_options = [data_arr[2], data_arr[3], data_arr[4], data_arr[5]]
        # organize the options
        options_message = "Choose the correct answer"
        for option in answer_options:
            options_message += f'\n{answer_options.index(option) + 1} - {option}'


        while True:
            # print the question and the answers
            print("-----------------------------")
            client_answer = input(f'Your Question Is: {question}\n{options_message}\n')
            # check if the client enterd a number within the range of the options
            try:
                client_answer = int(client_answer)
                if client_answer in range(1,len(answer_options) + 1): #check if this valid
                    break
                else:
                    print("-----------------------------")
                    print(f"Enter a number between 1 - {len(answer_options)}")

            except:
                print("-----------------------------")
                print(f"Enter a number between 1 - {len(answer_options)}")

        # build the message answer of the client send it and get the response
        command_code, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["send_answer_msg"], id + "#" + str(client_answer))

        # check the response of the server - and show to client
        # right answer
        if command_code == chatlib.PROTOCOL_SERVER["correct_answer_msg"]:
            print("-----------------------------")
            print(f"CORRECT! {compliments[random.randint(0, len(compliments) - 1)]} ")
        # wrong answer
        elif command_code == chatlib.PROTOCOL_SERVER["wrong_answer_msg"]:
            print("-----------------------------")
            print(f"INCORRECT! The correct answer is {data}, you better remember this for next time!")
        # unexpected error - how did you get here
        else:
            print("-----------------------------")
            error_and_exit(f"Unexpected Error :(")

    # the server sent error, stop function
    elif command_code == chatlib.PROTOCOL_SERVER["error_msg"]:
        return

    # unexpected error - how did you get here
    else:
        print("-----------------------------")
        error_and_exit(f"Unexpected Response :(")


def get_high_score(conn):
    """
    builds HIGH_SCORE command sends the message and gets the highest score using build send get parse
    :param conn: socket connected to server
    :return: nothing
    """
    command_code, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["high_score_msg"], "")
    if command_code == chatlib.PROTOCOL_SERVER["all_score_msg"]:
        print("-----------------------------")
        print(f'Leader Board \n{data}')

    # the server sent error, stop function
    elif command_code == chatlib.PROTOCOL_SERVER["error_msg"]:
        return

    else:
        print("-----------------------------")
        error_and_exit(f"Unexpected Error :(")


def logged_users(conn):
    """
    builds LOGGED command sends the message and gets the logged players list build send get parse
    :param conn: socket connected to server
    :return: nothing
    """
    command_code, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged_msg"], "")
    if command_code == chatlib.PROTOCOL_SERVER["logged_users_msg"]:
        print("-----------------------------")
        print("Logged Users")
        usernames = data.split(",")
        for username in usernames:
            print(username)

    # the server sent error, stop function
    elif command_code == chatlib.PROTOCOL_SERVER["error_msg"]:
       return

    else:
        print("-----------------------------")
        error_and_exit(f"Unexpected Error :(")


def main():
    """
    connect socket to server then ask login then logout and finish
    :return:
    """
    # connect socket to server
    sock = connect()

    # login your user
    login(sock)

    # show all the options
    options_message = "-----------------------------"
    for option in CLIENT_OPTIONS:
        options_message += f'\n{option} - {CLIENT_OPTIONS.index(option) + 1}'
    print(options_message)

    while True:
        print("-----------------------------")
        choice = input("What do you want?\n")

        # play a question
        if choice in [str(CLIENT_OPTIONS.index("Play") + 1), "play", "Play"]:
            play_question(sock)

        # get the personal score
        elif choice in [str(CLIENT_OPTIONS.index("Get Score") + 1), "score", "Score", "Get Score", "get score", "my score"]:
            get_score(sock)

        # get the leader board
        elif choice in [str(CLIENT_OPTIONS.index("LeaderBoard") + 1), "leaderboard", "LeaderBoard", "High Score", "high score"]:
            get_high_score(sock)

        # get logged in users
        elif choice in [str(CLIENT_OPTIONS.index("Logged Users") + 1), "logged in", "logged users", "Logged Users", "Logged In"]:
            logged_users(sock)

        # logout and close connection
        elif choice in [str(CLIENT_OPTIONS.index("Logout") + 1), "logout", "Logout"]:
            logout(sock)
            # close the socket
            sock.close()
            # finish the loop
            break


        # if the client chooses not according to the options
        else:
            print("-----------------------------")
            print("Sorry this is not available!")
            print(options_message)

    ####################### the messages print is for debugging in the meanwhile!!!!!!!!!!!!
    # code for cheking
    # while True:
    #
    #     msg = input("enter")
    #     msg2 = input("enter")
    #     build_send_recv_parse(sock, msg, msg2)
if __name__ == '__main__':
    main()