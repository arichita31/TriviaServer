##############################################################################
# server.py
##############################################################################

import socket
import chatlib
import random
import select

# GLOBALS
open_client_sockets = []
messages_to_send = []
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later


ERROR_MSG = "Error! "
SERVER_PORT = 6000
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

def build_and_send_message(conn, command_code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: nothing
    """
    global messages_to_send
    message = chatlib.build_message(command_code, str(data))
    messages_to_send.append((conn, message.encode()))
    # Debug Info
    print("-----------------------------")
    print("We Sent The Client: \n" + message)


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occurred, will return None, None
    """
    message_gotten = conn.recv(16384).decode()
    # Debug Info
    print("-----------------------------")
    print("The Client Sent Us: \n" + message_gotten)
    # check if the socket sent us empty message
    if message_gotten == "":
        return ("", "")
    # parse the message using chatlib
    command_code, msg_data = chatlib.parse_message(message_gotten)

    # check for problems when getting a message
    if command_code is None or msg_data is None:
        error_and_exit("An error occurred while trying to get a message headers, None Values")

    return command_code, msg_data


def print_client_sockets():
    """
    print all the clients connected to the server
    :return: None
    """
    global open_client_sockets
    print("These sockets are connected right now:")
    for client in open_client_sockets:
        print(client.getpeername())


# Data Loaders #
def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: None
    Returns: questions dictionary
    """
    questions = {
        2313: {"question": "Who invented the telephone?",
               "answers": ["Thomas Edison", "Albert Einstein", "Martin Cooper", "Alexander Graham Bell"], "correct": 4},
        4122: {"question": "What is the capital of France?",
               "answers": ["Lion", "Marseille", "Paris", "Montpellier"], "correct": 3},
        2212: {"question": "When did Israel gain independence?",
               "answers": ["1948", "1917", "1947", "1949"], "correct": 1},
        2314: {"question": "Who was the first commandant of Auschwitz?",
               "answers": ["Reinhard Heydrich", "Adolf Eiechmann", "Adolf Hitler", "Rudolf Hoess"], "correct": 4},
        4132: {"question": "Who was the first king of ancient Israel?",
               "answers": ["David", "Shlomo", "Shaul", "Rehavaam"],"correct": 3},
        4133: {"question": "Pasta is an _____ dish",
               "answers": ["Italian", "German", "British", "French"], "correct": 1},
        4135: {"question": "How many bones in human body?",
               "answers": ["248", "206", "365", "613"], "correct": 2},
        4131: {"question": "Which one of the following was the biggest empire at its best?",
               "answers": ["Roman Empire", "Russian Empire", "Turkish Empire", "British Empire"], "correct": 4},
        4130: {"question": "What is the most popular Programming Language in 2020?",
               "answers": ["C", "Python", "Java", "JavaScript"], "correct": 2},
        4139: {"question": "What year did World War I begin?",
               "answers": ["1914", "1918", "1939", "1919"], "correct": 1},
        3139: {"question": "What state is the largest state of the United States of America?",
               "answers": ["Texas", "Alaska", "Washington", "California"], "correct": 2},
        3129: {"question": "Which of these countries is NOT a part of the Asian continent?",
               "answers": ["Georgia", "Russia", "Suriname", "Singapore"], "correct": 3},
        3120: {"question": "What is the unit of currency in Australia?",
               "answers": ["USD", "RUB", "NIS", "AUD"], "correct": 4},
        3121: {"question": "In what year did the Wall Street Crash take place?",
               "answers": ["1929", "1939", "1931", "1933"], "correct": 1},
        3122: {"question": "When did the National Socialist German Workers' Party won the general election in Germany?",
               "answers": ["1929", "1939", "1931", "1933"], "correct": 4},
        3123: {"question": "Which ocean borders the west coast of the United States?",
               "answers": ["Pacific", "Atlantic", "Indian", "Arctic"], "correct": 1},
        3124: {"question": "What name was historically used for the Turkish city currently known as Istanbul?",
               "answers": ["Hüdavendigar", "Söğüt", "Constantinople", "Adrianople"], "correct": 3},
        3125: {"question": "What is the fastest land animal?",
               "answers": ["Cheetah", "Lion", "Ostrich", "Jaguar"], "correct": 1},
        3126: {"question": "Who was the greatest conqueror of all time",
               "answers": ["Alexander the Great", "Napoleon Bonaparte", "Adolf Hitler", "Genghis Khan"], "correct": 4},
        3128: {"question": "What is the 5th digit of pi?",
               "answers": ["five", "one", "four", "nine"], "correct": 1},
    }

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    global users
    # users = {
    #     "test": {"password": "test", "score": 0, "questions_asked": []},
    #     "yossi": {"password": "123", "score": 50, "questions_asked": []},
    #     "master": {"password": "master", "score": 200, "questions_asked": []}
    # }
    # open the text file that contains all of the users
    file = open("database.txt")
    content_file = file.read()
    # each row stands for a user, separate the user by separating the rows with \n
    content_rows = content_file.split("\n")
    # for each row separate the fields of each information about the user (in file separated by ,)
    for row in content_rows:
        row_parts = row.split(",")
        username = row_parts[0]
        password = row_parts[1]
        score = int(row_parts[2])
        questions_asked = []
        # if there are questions that the user has encountered with separate them to a list (in file separated by $)
        if row_parts[3] != "":
            for question in row_parts[3].split("$"):
                questions_asked.append(int(question))

        # finally, build the dictionary that will give us eay access to the users info during the run
        users[username] = {"password": password, "score": score, "questions_asked": questions_asked}
    # close the file
    file.close()
    return users


def upload_to_database():
    """
    this function updates the database everytime there is a change in users data.
    :return: None
    """
    # create a string that contains the rows of the database
    rows_to_load = []
    for user in users.keys():
        # the questions part of each user is stored while joined by $ so we need to take this list than convert each
        # value to string and join it by $
        questions_asked = [str(i) for i in users[user]["questions_asked"]]
        # create lambda that checks if list empty than returns "" or format to match database
        x = lambda l: "" if list == [] else "$".join(l)
        # add each user to as a different row in the database
        rows_to_load.append(f'{user},{users[user]["password"]},{users[user]["score"]},{x(questions_asked)}')
    # after we formatted as a string the information we wanted to load. open the database, overwrite it then close file
    file = open("database.txt", "w")
    file.write("\n".join(rows_to_load))
    file.close()

# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: nothing
    Returns: the socket object
    """
    # Implement code ...
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen()
    return sock


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["error_msg"], error_msg)


def error_and_exit(msg):
    """
    when error occurs the function finishes the program and prints the error message
    :param msg: error message
    :return: nothing
    """
    print(msg)
    exit()


def handle_get_score_message(conn, username):
    """
    the function identifies the username using getpeername and logged users dict than extracting the score from users dict and send it to the client
    :param conn: client sock
    :param username: username, taken from logged users dict where key is the address of the client sock
    :return: None
    """
    global users
    # build a message and send to the client with YOUR_SCORE command and the score which is int so cast it to str
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["user_score_msg"], str(users[username]["score"]))


def handle_get_highscore_message(conn):
    """
    the function extracts all the scores of the users in our game and sorts it by their values from highest to lowest
    then sends it to the client according to the protocol
    :param conn: the client socket
    :return: None
    """
    global users
    # list for usernames and their scores
    users_and_scores = []
    data = ""
    for username in users.keys():
        users_and_scores.append((username, users[username]["score"]))
    # sort the list of the users and scores by the second index of the tuple
    users_and_scores = sorted(users_and_scores, key=lambda users_and_scores: users_and_scores[1],  reverse=True)
    # define how many users to show on the table of high scores
    users_to_show = len(users_and_scores)
    if users_to_show > 5:
        users_to_show = 5
    # build the data of the message according to the protocol
    for i in range(users_to_show):
        # take each user and score from users and scores and order it to data
        data += str(i + 1) + "." + " " + users_and_scores[i][0] + ":" + " " + str(users_and_scores[i][1]) + "\n"
    # send to the client
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score_msg"], data)


def handle_get_logged_users(conn):
    """
    the function extracts all the logged users then sends it to the client according to the protocol
    :param conn: the client socket
    :return: None
    """
    global logged_users
    data = ""
    # extract all the usernames from the values of the sictionary
    for username in logged_users.values():
        data += username + ","
    # remove the last letter
    data = data[:-1]
    # send to the client
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["logged_users_msg"], data)


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    # remove the client from the logged users dictionary
    del logged_users[conn.getpeername()]
    # remove it from open client sockets list
    open_client_sockets.remove(conn)
    # notify that a client disconnected
    print("-----------------------------")
    print(f"Connection with client {conn.getpeername()} closed.")
    # close the socket of the client
    conn.close()
    # print the open connections
    print("-----------------------------")
    print_client_sockets()


# Implement code ...


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later
    # extract the username and the password from the given data message
    givenuname, givenpass = data.split("#")
    # check if the user is not logged in
    if givenuname in logged_users.values():
        send_error(conn, "Error! this user already logged in!")
    # check if the user is exist in the dictionary and that its password matches the the password that was given
    elif givenuname in users.keys() and users[givenuname]["password"] == givenpass:
        logged_users[conn.getpeername()] = givenuname
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], "")
    # if not send error
    else:
        send_error(conn, "Error! This user does not exist!")


def handle_client_message(conn, msg_code, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users  # To be used later
    # check if the client is premitted made login
    is_permitted = False
    if conn.getpeername() in logged_users.keys():
        is_permitted = True

    # LOGIN COMMAND - check if the client is not connected yet
    if msg_code == chatlib.PROTOCOL_CLIENT["login_msg"] and not is_permitted:
        handle_login_message(conn, data)

    # if the command of the message is not login message  and the client is connected
    elif is_permitted:
        username = logged_users[conn.getpeername()]
        # if the client requested login and his address already connected
        if msg_code == chatlib.PROTOCOL_CLIENT["login_msg"]:
            send_error(conn, "Error! Already Logged In")

        # LOGOUT COMMAND
        if msg_code == chatlib.PROTOCOL_CLIENT["logout_msg"] or msg_code == "":
            handle_logout_message(conn)

        # GET SCORE COMMAND
        elif msg_code == chatlib.PROTOCOL_CLIENT["get_score_msg"]:
            handle_get_score_message(conn, username)

        # GET QUESTION COMMAND
        elif msg_code == chatlib.PROTOCOL_CLIENT["get_question_msg"]:
            handle_question_message(conn, username)

        # SEND ANSWER COMMAND
        elif msg_code == chatlib.PROTOCOL_CLIENT["send_answer_msg"]:
            handle_answer_message(conn, username, data)

        # HIGH SCORE COMMAND
        elif msg_code == chatlib.PROTOCOL_CLIENT["high_score_msg"]:
            handle_get_highscore_message(conn)

        # LOGGED USERS COMMAND
        elif msg_code == chatlib.PROTOCOL_CLIENT["logged_msg"]:
            handle_get_logged_users(conn)

        else:
            send_error(conn, "Error! The command is not recognized!")

    else:
        send_error(conn, "Error! You need to login first to have permission!")


def create_random_question(username):
    """
       Return the question and answers in YOUR QUESTION format(only the data)
       :param username: the name of the user
       :return: the data for YOUR_QUESTION
       """
    global users
    global questions
    # the number of the questions
    questions_dict_len = len(questions)
    # list of all th questions codes
    questions_codes_list = list(questions.keys())

    while True:  # search random question that wasn't answered until you find one then return
        # random index between 0 and end index
        random_question_num = random.randint(0, questions_dict_len - 1)
        question_code = questions_codes_list[random_question_num]

        if question_code not in users[username]["questions_asked"]:
            # if the question wasn't asked return the question and answers
            # add the question code to the questions that were asked
            users[username]["questions_asked"].append(question_code)
            # update the database
            upload_to_database()
            # arrange the answer by the YOUR_QUESTION format

            answers = questions[question_code]["answers"]
            data_fields = [str(question_code), questions[question_code]["question"], answers[0], answers[1], answers[2],
                           answers[3]]
            data = "#".join(data_fields)
            return data
        # if the question was already asked check if all the questions
        # were asked (by length) and return None if True
        else:
            if len(questions) == len(users[username]["questions_asked"]):
                return ""


def handle_question_message(conn, username):
    """
    Send appropriate message: send question in Your_Question format
    or send No_Questions message in the appropriate format

    :param conn: the client socket
    :param username: the name of the user
    :return: nothing
    """
    data = create_random_question(username)
    if data != "":
        # return the Your_Question message
        msg_code = chatlib.PROTOCOL_SERVER["your_question_msg"]
    else:
        # return the No Questions message
        msg_code = chatlib.PROTOCOL_SERVER["no_questions_msg"]
    build_and_send_message(conn, msg_code, data)


def handle_answer_message(conn, username, answer_msg):
    """
    the functions get the answer for the question that the client was asked check if it is right
    and sends a proper answer based on the protocol
    :param conn: the client socket
    :param username: the client username where key is the address of the client in logged users dict
    :param answer: the client answer to the questions
    :return: nothing
    """
    global users
    global questions
    # extract the id and the choice of the client from the data of the message id#choice
    question_code, choice = answer_msg.split("#")
    # extract the right answer for the question using the questions dict - we get int so cast it to str
    correct_answer = str(questions[int(question_code)]["correct"])
    # check if the choice of the client is the right answer
    # correct answer
    if correct_answer == choice:
        command_code = chatlib.PROTOCOL_SERVER["correct_answer_msg"]
        data = ""
        # add 5 points
        users[username]["score"] += 5
        # score was changed update database
        upload_to_database()

    # wrong answer
    else:
        command_code = chatlib.PROTOCOL_SERVER["wrong_answer_msg"]
        data = str(correct_answer)

    # build and send the response message
    build_and_send_message(conn, command_code, data)


def send_waiting_messages(wlist):
    """

    :param wlist:
    :return:
    """
    global messages_to_send
    for message in messages_to_send:
       client_socket, data = message
       if client_socket in wlist:
           client_socket.send(data)
           messages_to_send.remove(message)


def main():
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions
    global messages_to_send

    print("Welcome to Trivia Server!")

    # load the db of the server
    users = load_user_database()
    questions = load_questions()

    # set up the socket of the server to listening
    sock = setup_socket()

    # while True:
    #     # connection was made
    #     client_sock, addr = sock.accept()
    #     print(f'Connected with client {client_sock.getpeername()}')
    #     client_connected = True
    
    #     while client_connected:
    #         msg_code, data = recv_message_and_parse(client_sock)
    #         handle_client_message(client_sock, msg_code, data)
    #         # the client is no longer connected
    #         if msg_code == chatlib.PROTOCOL_CLIENT["logout_msg"]:
    #             client_connected = False

    while True:
        rlist, wlist, xlist = select.select([sock] + open_client_sockets, open_client_sockets, [])
        for current_socket in rlist:
            try:
                # get new connections from clients who try to reach the server
                if current_socket is sock:
                    (new_socket, address) = sock.accept()
                    print("-----------------------------")
                    print("new socket connected to server: ", new_socket.getpeername())
                    open_client_sockets.append(new_socket)
                    print_client_sockets()
                # handle sort of requests from the clients
                else:
                    print("-----------------------------")
                    print(f'New data from client {current_socket.getpeername()}')
                    msg_code, data = recv_message_and_parse(current_socket)
                    handle_client_message(current_socket, msg_code, data)

            # catch an error if a client forcibly closed the socket without logout
            except ConnectionResetError:
                # if the client was logged in make an arranged logout
                if current_socket.getpeername() in logged_users:
                    handle_logout_message(current_socket)
                # if not removing him from open clients sockets is enough
                else:
                    open_client_sockets.remove(current_socket)
                    print("-----------------------------")
                    print(f"Connection with client {current_socket.getpeername()} closed.")
                    print("-----------------------------")
                    current_socket.close()
                    print_client_sockets()

        send_waiting_messages(wlist)

# TO CHECK
# 1. if needed dictionary "data_queue" for client messages
# 2. how to upload changes to the file


if __name__ == '__main__':
    main()
