##############################################################################
# server.py
##############################################################################

import socket
import chatlib

# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

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
    print("-----------------------------")
    print("We Sent The Client: \n" + message)


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
    print("-----------------------------")
    print("The Client Sent Us: \n" + message_gotten)
    # parse the message using chatlib
    command_code, msg_data = chatlib.parse_message(message_gotten)


    return command_code, msg_data

# Data Loaders #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    questions = {
        2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
        4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
               "correct": 3}
    }

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    users = {
        "test"	:	{"password" :"test" ,"score" :0 ,"questions_asked" :[]},
        "yossi"		:	{"password" :"123" ,"score" :50 ,"questions_asked" :[]},
        "master"	:	{"password" :"master" ,"score" :200 ,"questions_asked" :[]}
    }
    return users


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


def handle_getscore_message(conn, username):
    """
    the function identifies the username using getpeername and logged users dict than extracting the score from users dict and send it to the client
    :param conn: client sock
    :param username: username, taken from logged users dict where key is the address of the client sock
    :return: nothing
    """
    global users
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["user_score_msg"], str(users[username]["score"]))


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    # remove the client from the logged users dictionary
    del logged_users[conn.getpeername()]
    # close the socket of the client
    conn.close()

# Implement code ...


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users	 # To be used later
    # extract the username and the password from the given data message
    givenuname, givenpass = data.split("#")
    # check if the user is exist in the dictionary and that its password matches the the password that was given
    if givenuname in users.keys() and users[givenuname]["password"] == givenpass:
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
    global logged_users	 # To be used later
    # check if the client is logged
    is_logged = False
    if conn.getpeername() in logged_users.keys():
        is_logged = True

    # LOGIN COMMAND - check if the client is not connected yet
    if msg_code == chatlib.PROTOCOL_CLIENT["login_msg"] and not is_logged:
        handle_login_message(conn, data)

    # if the command of the message is not login message  and the client is connected
    elif is_logged:
        if msg_code == chatlib.PROTOCOL_CLIENT["login_msg"]:
            send_error(conn, "Error! Already Logged In")
        # LOGOUT COMMAND
        if msg_code == chatlib.PROTOCOL_CLIENT["logout_msg"] or msg_code == "":
            handle_logout_message(conn)

        # GET SCORE COMMAND
        elif msg_code == chatlib.PROTOCOL_CLIENT["get_score_msg"]:
            handle_getscore_message(conn, logged_users[conn.getpeername()])

        else:
            send_error(conn, "Error! The command is not recognized!")

    else:
        send_error(conn, "Error! You need to login first to have permission!")





def main():
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions

    print("Welcome to Trivia Server!")

    # load the db of the server
    users = load_user_database()
    questions = load_questions()

    # set up the socket of the server to listening
    sock = setup_socket()

    while True:
        # connection was made
        client_sock, addr = sock.accept()
        print(f'Connected with client {addr}')
        client_sock.getpeername()
        client_connected = True

        while client_connected:
            msg_code, data = recv_message_and_parse(client_sock)
            handle_client_message(client_sock, msg_code, data)
            # the client is no longer connected
            if msg_code == chatlib.PROTOCOL_CLIENT["logout_msg"]:
                client_connected = False

    ############################## NEED TO FIX A MESSAGE WITH A COMMAND WHO ISNT RECOGNIZED

if __name__ == '__main__':
    main()
