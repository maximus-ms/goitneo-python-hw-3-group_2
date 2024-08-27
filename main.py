from bot import Bot
from addressbook import AddressBook


def main():
    address_book = AddressBook("my_book.bin")
    bot = Bot(address_book)
    bot.run()


if __name__ == "__main__":
    main()

