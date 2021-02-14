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
    "logout_msg": "LOGOUT",
    "logged_msg": "LOGGED",
    "get_question_msg": "GET_QUESTION",
    "send_answer_msg": "SEND_ANSWER",
    "get_score_msg": "MY_SCORE",
    "high_score_msg": "HIGHSCORE",

}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR",
    "user_score_msg": "YOUR_SCORE",
    "no_questions_msg": "NO_QUESTIONS",
    "your_question_msg": "YOUR_QUESTION",
    "error_msg": "ERROR",
    "correct_answer_msg": "CORRECT_ANSWER",
    "wrong_answer_msg": "WRONG_ANSWER",
    "all_score_msg": "ALL_SCORE",
    "logged_users_msg": "LOGGED_ANSWER"

}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


# def is_msg_valid(msg):
#     msg_parts = msg.split(DELIMITER)
#     if msg_parts[0].length != CMD_FIELD_LENGTH:
#         return False
#     if msg_parts[1].length != LENGTH_FIELD_LENGTH or msg_parts[1].isnumeric() == False or int(msg_parts[1]) < 0:
#         return False
#     if msg_parts[2].length != int(msg_parts[1]):
#         return False
#     return True

def is_parameters_valid(command, data):
    """

    :param command_code:
    :param data:
    :return:
    """
    # check if the command_code is string
    if not isinstance(command, str):
        return False

    # check if the data is string
    if not isinstance(data, str):
        return False

    # check if the command name is in the commands dictionary values
    command_found = False
    for key in PROTOCOL_CLIENT.keys():
        if PROTOCOL_CLIENT[key] == command.strip():
            command_found = True
            break

    if not command_found:
        for key in PROTOCOL_SERVER.keys():
            if PROTOCOL_SERVER[key] == command.strip():
                command_found = True
                break

    if not command_found:
        return False

    # check if the data len is no more than the limit
    if len(data) > 9999:
        return False

    return True


def build_message(command_code, data): #לבדוק עם צביקה מה החוקים של הפרוטוקול
    """
    Gets command name and data field and creates a valid protocol message
    Returns: str, or None if error occured
    """
    # check if parameters sre valid
    if not is_parameters_valid(command_code, data):
        print("Values are not valid!")
        return ERROR_RETURN

    # first msg part
    command = command_code.ljust(16)
    # second msg part
    length_msg = str(len(data))
    length_msg = length_msg.rjust(4, '0')
    # third msg part is data
    message_fields = [command, length_msg, data]

    return join_msg(message_fields)


def is_fields_valid(command, length, data): # לבדוק אם להכניס 0 או רווח אם צריך להשלים את שדה האורך של ההודעה,
    """

    :param command: the command name
    :param length:
    :param data:
    :return:
    """
    # check if the command field length is ok
    if len(command) != CMD_FIELD_LENGTH:
        return False

    # check if the length field length is ok
    if len(length) != LENGTH_FIELD_LENGTH:
        return False

    # check if the command name is in the commands dictionary values
    command_found = False
    for key in PROTOCOL_CLIENT.keys():
        if PROTOCOL_CLIENT[key] == command.strip():
            command_found = True
            break

    if not command_found:
        for key in PROTOCOL_SERVER.keys():
            if PROTOCOL_SERVER[key] == command.strip():
                command_found = True
                break

    if not command_found:
        return False

    # check if the length is a number
    if not length.strip().isnumeric():
        return False

    # check if the data length is equal to length
    if int(length.strip()) != len(data):
        return False

    # check if the data len is no more than the limit
    if int(length.strip()) > MAX_DATA_LENGTH:
        return False

    return True


def parse_message(data): # לבדוק אם ניתן לקבל יותר מ2 מפרידים מסוג |
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured returns None, None
    """
    # split the message to its parts
    msg_fields = split_msg(data)

    # check if we got values for the message parts
    for field in msg_fields:
        if field is None:
            return ERROR_RETURN, ERROR_RETURN

    # the command id the first field
    command = msg_fields[0]
    # the length is the second field
    length = msg_fields[1]
    # the data is the third field
    data = msg_fields[2]

    # check if the command that was given is written right
    if not is_fields_valid(command, length, data):
        print("Message Fields Are Not Valid!")
        return ERROR_RETURN, ERROR_RETURN

    command_name = command.strip()

    return command_name, data


def split_msg(msg, expected_fields=3):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's delimiter (|) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    msg_fields = msg.split(DELIMITER)

    # check if the count of the fields is matching the expected
    if len(msg_fields) != expected_fields:
        return ERROR_RETURN, ERROR_RETURN

    return msg_fields


def join_msg(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the delimiter.
    Returns: string that looks like cell1|cell2|cell3
    """
    return DELIMITER.join(msg_fields)




