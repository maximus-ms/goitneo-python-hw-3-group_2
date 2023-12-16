from collections import UserDict


class Field:
    """Base class for record fields."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Class for storing a contact's name. Mandatory field."""


class Phone(Field):
    """Class for storing a phone number. Validates the format (10 digits)."""

    def __init__(self, value):
        self.validate_phone(value)
        super().__init__(value)

    def validate_phone(self, number: str):
        if len(number) == 10 and number.isdigit():
            return True
        raise ValueError("Invalid phone number format")


class Record:
    """Class for storing contact information, including name and a list of phones."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    def __find_phone_index__(self, phone):
        phone = Phone(phone)
        for i, i_phone in enumerate(self.phones):
            if i_phone.value == phone.value:
                return i
        raise ValueError("Phone number is not in the list")

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        self.phones.pop(Phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str):
        self.phones[self.__find_phone_index__(old_phone)] = Phone(new_phone)

    def find_phone(self, phone: str) -> Phone:
        return self.phones[self.__find_phone_index__(phone)]


class AddressBook(UserDict):
    """Class for storing and managing records."""

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        return self.data[name]

    def delete(self, name: str):
        self.data.pop(name)


if __name__ == "__main__":
    # Creating a new address book
    book = AddressBook()

    # Creating a record for John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Adding John's record to the address book
    book.add_record(john_record)

    # Creating and adding a new record for Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Displaying all records in the book
    for name, record in book.data.items():
        print(record)
        # Output: Contact name: John, phones: 1234567890; 5555555555
        # Output: Contact name: Jane, phones: 9876543210

    # Finding and editing the phone for John
    john = book.find("John")
    print("help", john)
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Output: Contact name: John, phones: 1112223333; 5555555555

    # Searching for a specific phone in John's record
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Output: John: 5555555555

    # Deleting Jane's record
    book.delete("Jane")
