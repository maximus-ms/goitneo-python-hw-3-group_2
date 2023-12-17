from collections import UserDict
import os
import pickle
import json
from abc import ABC, abstractmethod
from datetime import datetime

import birthdays

class ErrorWithMsg(Exception): pass

class Field(ABC):
    """Base class for record fields."""

    def __init__(self, value=None):
        self.__value = None
        if not value is None:
            self.value = value

    def __str__(self):
        return self.value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = self.validate(new_value)

    @abstractmethod
    def validate(self, value) -> None:
        """Must raise an exception if not valid or return a value"""
        raise ErrorWithMsg("Unknown value validator")


class Name(Field):
    """Class for storing a contact's name. Mandatory field."""

    def validate(self, name: str):
        name = name.strip()
        if type(name) is str:
            return name
        raise ErrorWithMsg("Name must be a string")


class Phone(Field):
    """Class for storing a phone number. Validates the format (10 digits)."""

    def validate(self, number: str):
        number = number.strip()
        if len(number) == 10 and number.isdigit():
            return number
        raise ErrorWithMsg("Invalid phone number format (expecting 10 digits)")


class Birthday(Field):
    """Class for storing a birthday. Validates the format (expecting DD.MM.YYYY)."""

    def validate(self, birthday: str):
        birthday = birthday.strip()
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
        except:
            raise ErrorWithMsg("Invalid birthday format (DD.MM.YYYY)")
        return birthday


class Record:
    """Class for storing contact information, including name and a list of phones."""

    def __init__(self, name:str, phone:str=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday()
        if phone:
            self.add_phone(phone)

    def __str__(self):
        text = f"Contact name: {self.get_name()}, phones: {'; '.join(p.value for p in self.phones)}"
        if self.birthday.value:
            text += f", birthday: {self.birthday.value}"
        return text

    def __find_phone_index__(self, phone):
        phone = Phone(phone)
        for i, i_phone in enumerate(self.phones):
            if i_phone.value == phone.value:
                return i
        raise ErrorWithMsg("Phone number is not in the list")

    def get_name(self) -> str:
        return self.name.value

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        self.phones.pop(Phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str):
        self.phones[self.__find_phone_index__(old_phone)] = Phone(new_phone)

    def replace_phone(self, new_phone: str):
        if len(self.phones) == 0:
            raise ErrorWithMsg("Contact '{self.name.value}' has no phone.")
        self.phones[0] = Phone(new_phone)

    def get_phone(self) -> str:
        if len(self.phones) == 0:
            raise ErrorWithMsg("Contact '{self.name.value}' has no phone.")
        return self.phones[0].value

    def find_phone(self, phone: str) -> Phone:
        return self.phones[self.__find_phone_index__(phone)]

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        birthday = self.birthday.value
        if birthday is None:
            raise ErrorWithMsg("Birthday is not set")
        return birthday

class AddressBook(UserDict):
    """Class for storing and managing records."""
    def __init__(self, filename:str=None):
        super().__init__()
        self.__dump_to_file = self.dummy_dump_to_file
        self.__filename = filename
        if self.__filename:
            if filename.endswith(".json"):
                print("JSON does not supported yet. Please use bin file.")
                exit(1)
                self.__serializer = json
                self.__file_mode = ''
            else:
                self.__serializer = pickle
                self.__file_mode = 'b'
            self.__dump_to_file = self.write_to_file
            self.load_from_file()

    def write_to_file(self):
        with open(self.__filename, 'w'+self.__file_mode) as fd:
            self.__serializer.dump(self.data, fd)

    def load_from_file(self):
        if not os.path.isfile(self.__filename): return
        try:
            with open(self.__filename, 'r'+self.__file_mode) as fd:
                self.data = self.__serializer.load(fd)
        except:
            print(f"Can not load addressbook from the file '{self.__filename}'")

    def save_data(func):
        def inner(*args, **kwargs):
            ret = func(*args, **kwargs)
            __self = args[0]
            __self.dump_to_file()
            return ret
        return inner

    def dump_to_file(self):
        # Will be used by decorator
        return self.__dump_to_file()

    def dummy_dump_to_file():
        pass

    def __getitem__(self, name):
        if not name in self.data:
            raise ErrorWithMsg(f"Contact '{name}' does not exist.")
        return self.data[name]

    def __iter__(self):
        if len(self.data) == 0:
            raise ErrorWithMsg(f"Addressbook is empty.")
        return super().__iter__()

    @save_data
    def __setitem__(self, name, value):
        # Can change only existing records
        if not name in self.data:
            raise ErrorWithMsg(f"Contact '{name}' does not exist.")
        self.data[name] = value

    @save_data
    def add_record(self, record: Record):
        if record.name.value in self.data:
            raise ErrorWithMsg(f"Contact '{record.name.value}' already exists.")
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        return self[name]

    def get_all_birthdays(self):
        birthday_list = []
        for record in self.data.values():
            birthday = record.birthday.value
            if birthday:
                birthday_list.append({
                        "name": record.name.value,
                        'birthday': datetime.strptime(birthday, "%d.%m.%Y")
                    })
        return birthday_list

    def get_birthdays_per_week(self):
        return birthdays.get_birthdays_per_week(self.get_all_birthdays())

    @save_data
    def delete(self, name: str):
        self.data.pop(name)

    @save_data
    def delete_all(self):
        self.data.clear()

