import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


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
    print("We Sent The Server: \n" + message)




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
    print("The Server Sent Us: \n" + message_gotten)
    # parse the message using chatlib
    command_code, msg_data = chatlib.parse_message(message_gotten)
    return command_code, msg_data


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
        print("-----------------------------")
        password = input("Please enter password: \n")
        # create the data for login message
        message_data = username + "#" + password
        # build message using chatlib
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], message_data)
        # Debug Info



        # recieved answer from server
        command_code, message_gotten_data = recv_message_and_parse(conn)

        # cheking if login succeeded
        if command_code == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            print("-----------------------------")
            print(f'Logged in as: {username} :)')
            return
        else:
            print("-----------------------------")
            print("Login failed :( \n Try Again!")




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




def main():
    """
    connect socket to server then ask login then logout and finish
    :return:
    """
    # connect socket to server
    sock = connect()
    # login your user
    login(sock)
    # logot from system
    logout(sock)
    # close the socket
    sock.close()

if __name__ == '__main__':
    main()