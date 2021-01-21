import socket
# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR"
}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error

#server IP address and PORT
IP, PORT = "127.0.0.1", 8080

#create socket for communication with client
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((IP, PORT))
sock.listen(5)


def is_msg_valid(msg):
    msg_parts = msg.split(DELIMITER)
    if msg_parts[0].length != CMD_FIELD_LENGTH:
        return False
    if msg_parts[1].length != LENGTH_FIELD_LENGTH or msg_parts[1].isnumeric() == False or int(msg_parts[1]) < 0:
        return False
    if msg_parts[2].length != int(msg_parts[1]):
        return False
    return True

def build_message(cmd, data):
    """
    Gets command name and data field and creates a valid protocol message
    Returns: str, or None if error occured
    """
    # Implement code ...


#return full_msg


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    # Implement code ...

    # The function should return 2 values


#return cmd, msg


def split_msg(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's delimiter (|) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """


# Implement code ...


def join_msg(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the delimiter.
    Returns: string that looks like cell1|cell2|cell3
    """
# Implement code ...

if __name__ == "__main__":
    flag = True
    print("Server is up and Running")

    while flag:
        client, address = sock.accept()
        print(f'Connected with {address}')
        msg = client.recv(1024).decode()
        print(msg)
        client.close()




