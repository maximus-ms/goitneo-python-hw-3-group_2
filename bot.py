# from addressbook import AddressBook, Record, Phone

invalid_cmd_msg = "Invalid command."

help_message = """
    This is a CLI Bot-assistant for a phone-book.
    List of supported commands:
        - "hello"
        - "add"
        - "change"
        - "phone"
        - "all"
        - "close", "exit"
        - "help"
"""


class ErrorNoContact(Exception):
    pass


class ErrorNoContacts(Exception):
    pass


class ErrorContactExist(Exception):
    pass


def parsing_errors(func):
    def inner(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except Exception as e:
            return "", ""

    return inner


def any_errors(func):
    def inner(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except Exception as e:
            return invalid_cmd_msg

    return inner


def get_errors(func):
    def inner(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except ErrorNoContact:
            return "Contact doesn't exist."
        except ErrorNoContacts:
            return "Address book is empty."
        except ValueError:
            return "Give me a name please."

    return inner


def input_errors(func):
    def inner(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except ErrorContactExist:
            return "Contact already exists."
        except ValueError:
            return "Give me name and phone please."

    return inner


@any_errors
@input_errors
def add(phone_book, args):
    name, number = args
    if name in phone_book:
        raise ErrorContactExist
    phone_book[name] = number
    return "Contact added."


@any_errors
@get_errors
@input_errors
def update(phone_book, args):
    name, number = args
    if not name in phone_book:
        raise ErrorNoContact
    phone_book[name] = number
    return "Contact updated."


@any_errors
@get_errors
def get(phone_book, args):
    if len(phone_book) == 0:
        raise ErrorNoContacts
    (name,) = args
    return phone_book.get(name, "Contact doesn't exist.")


@any_errors
@get_errors
def get_all(phone_book):
    if len(phone_book) == 0:
        raise ErrorNoContacts
    ret = []
    for user in phone_book:
        ret.append(f"{user}: {phone_book[user]}")
    return "\n".join(ret)


@parsing_errors
def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.strip().lower(), args


def run_phone_book_bot(phone_book):
    print("Welcome to the assistant bot!")
    finish = False
    while not finish:
        cmd, args = parse_input(input("Enter a command: "))
        if cmd == "hello":
            message = "How can I help you?"
        elif cmd == "add":
            message = add(phone_book, args)
        elif cmd == "change":
            message = update(phone_book, args)
        elif cmd in ("phone"):
            message = get(phone_book, args)
        elif cmd == "all":
            message = get_all(phone_book)
        elif cmd in ("close", "exit"):
            message = "Good bye!"
            finish = True
        elif cmd == "help":
            message = help_message
        else:
            message = invalid_cmd_msg
        print(message)


def main():
    local_phone_book = dict()
    run_phone_book_bot(local_phone_book)


if __name__ == "__main__":
    main()
