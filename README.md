## GoITNeo Python HW-3

### Task 1: Bot-assistant
#### CLI Bot-assistant for a phone-book
```
List of supported commands:
  - add <name> <phone>                  : Add a new contact with a name and phone number.
  - change <name> <new phone>           : Change the phone number for the specified contact.
  - phone <name>                        : Show the phone number for the specified contact.
  - all                                 : Show all contacts in the address book.
  - add-birthday <name> <date_of_birth> : Add a date of birth for the specified contact (DD.MM.YYYY).
  - show-birthday <name>                : Show the date of birth for the specified contact.
  - birthdays                           : Show birthdays that will occur during the next week.
  - hello                               : Receive a greeting from the bot.
  - close, exit, q                      : Close the program.
  - help, h                             : Show this message.
```

#### Used technics
```
 - defaultdict
 - pickle
 - UserDict
 - custom Exceptions
 - functors
 - decorators
 - getter/setter
 - abstract method
 - reload magic methods
    - __iter__
    - __getitem__
    - __setitem__
    - __call__
 - etc.
```


### Task 2: Save/restore address book to/from bin file
Addressbook automatically restores records from binary file if it is provided and exists.
All records are stored to binary file in decorated methods ```add_record(), delete(), delete_all(), __setitem__()``` and on exit from the bot.


