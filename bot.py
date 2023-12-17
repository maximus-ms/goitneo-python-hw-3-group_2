from collections import defaultdict
from addressbook import *


class Cmd:
    def __init__(self, name, handler, help_short, help_long):
        self.name = name
        self.handler = handler
        self.help_short = help_short
        self.help_long = help_long

    def __call__(self, args):
        return self.handler(args)


class Bot:
    INVALID_CMD_MSG = "Invalid command!"

    HELP_MSG_HEAD = "\nThis is a CLI Bot-assistant for a phone-book.\nList of supported commands:\n"
    HELP_MSG_CMDS_FORMAT = "  {:<35} : {}"
    CMD_NAME_LIST = [
        "add",
        "change",
        "phone",
        "all",
        "add-birthday",
        "show-birthday",
        "birthdays",
        "hello",
        "close",
        "exit",
        "q",
        "help",
        "h",
    ]

    def __init__(self, addressbook: AddressBook):
        self.cmds = defaultdict(
            lambda: Cmd("unknown_cmd", self.unknown_cmd, "", "")
        )
        self.cmds["add"] = Cmd(
            "add",
            self.add,
            "add <name> <phone>",
            "Add a new contact with a name and phone number.",
        )
        self.cmds["change"] = Cmd(
            "change",
            self.change,
            "change <name> <new phone>",
            "Change the phone number for the specified contact.",
        )
        self.cmds["phone"] = Cmd(
            "phone",
            self.phone,
            "phone <name>",
            "Show the phone number for the specified contact.",
        )
        self.cmds["all"] = Cmd(
            "all", self.all, "all", "Show all contacts in the address book."
        )
        self.cmds["add-birthday"] = Cmd(
            "add-birthday",
            self.add_birthday,
            "add-birthday <name> <date_of_birth>",
            "Add a date of birth for the specified contact (DD.MM.YYYY).",
        )
        self.cmds["show-birthday"] = Cmd(
            "show-birthday",
            self.show_birthday,
            "show-birthday <name>",
            "Show the date of birth for the specified contact.",
        )
        self.cmds["birthdays"] = Cmd(
            "birthdays",
            self.birthdays,
            "birthdays",
            "Show birthdays that will occur during the next week.",
        )
        self.cmds["hello"] = Cmd(
            "hello", self.hello, "hello", "Receive a greeting from the bot."
        )
        self.cmds["close"] = Cmd(
            "close", self.close, "close", "Close the program."
        )
        self.cmds["exit"] = Cmd(
            "exit", self.close, "exit", "Close the program."
        )
        self.cmds["q"] = Cmd("q", self.close, "q", "Close the program.")
        self.cmds["help"] = Cmd("help", self.help, "help", "Show this message.")
        self.cmds["h"] = Cmd("h", self.help, "h", "Show this message.")
        self.cmds["unknown_cmd"] = Cmd("unknown_cmd", self.unknown_cmd, "", "")
        self.addressbook = addressbook
        self.finish = False

    def parsing_errors(func):
        def inner(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
                return ret
            except Exception as e:
                return "", ""

        return inner

    def help_message(self):
        message = list()
        message.append(Bot.HELP_MSG_HEAD)
        for l in Bot.CMD_NAME_LIST:
            message.append(
                Bot.HELP_MSG_CMDS_FORMAT.format(
                    self.cmds[l].help_short, self.cmds[l].help_long
                )
            )
        return "\n".join(message) + "\n"

    def cmd_errors(func):
        def inner(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
                return ret
            except ErrorWithMsg as e:
                return e
            except ValueError as e:
                __self = args[0]
                return f"{Bot.INVALID_CMD_MSG} Expected format: {__self.cmds[func.__name__.replace('_','-')].help_short}"

        return inner

    @cmd_errors
    def add(self, args):
        name, number = args
        self.addressbook.add_record(Record(name, number))
        return f"Contact '{name}' added."

    @cmd_errors
    def change(self, args):
        name, number = args
        self.addressbook[name].replace_phone(number)
        return f"Contact '{name}' updated."

    @cmd_errors
    def phone(self, args):
        (name,) = args
        return self.addressbook[name].get_phone()

    @cmd_errors
    def all(self, args):
        if len(args) > 0:
            raise ValueError
        records = [str(r) for r in self.addressbook.values()]
        return "\n".join(records)

    @cmd_errors
    def add_birthday(self, args):
        name, birthday = args
        self.addressbook[name].add_birthday(birthday)
        return f"Contact '{name}' updated: birthday at {self.addressbook[name].show_birthday()}"

    @cmd_errors
    def show_birthday(self, args):
        (name,) = args
        return self.addressbook[name].show_birthday()

    @cmd_errors
    def birthdays(self, args):
        if len(args) > 0:
            raise ValueError
        return self.addressbook.get_birthdays_per_week()

    @cmd_errors
    def hello(self, args):
        if len(args) > 0:
            raise ValueError
        return "How can I help you?"

    @cmd_errors
    def close(self, args):
        if len(args) > 0:
            raise ValueError
        self.addressbook.dump_to_file()
        self.finish = True
        return "Good bye!"

    @cmd_errors
    def help(self, args):
        if len(args) > 0:
            raise ValueError
        return self.help_message()

    @cmd_errors
    def unknown_cmd(self, args):
        return Bot.INVALID_CMD_MSG

    @parsing_errors
    def get_input(self, message):
        user_input = input(message)
        cmd, *args = user_input.split()
        return cmd.strip().lower(), args

    def run(self):
        print("Welcome to the assistant bot!")
        while not self.finish:
            cmd, args = self.get_input("Enter a command: ")
            print(self.cmds[cmd](args))

