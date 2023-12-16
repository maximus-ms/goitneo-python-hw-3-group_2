from collections import defaultdict
from datetime import datetime, timedelta, time, date
from calendar import isleap, day_name


def get_birthdays_per_week(users, debug=False, today=None):
    days = defaultdict(list)
    if not today:
        today = datetime.today().date()
    if debug:
        print("Today:", today)
    for user in users:
        birthday = user["birthday"].date()
        if (
            not isleap(today.year)
            and birthday.month == 2
            and birthday.day == 29
        ):
            if not isleap(birthday.year):
                # looks like an error
                # it is impossible to have a BD at 29-Feb in non leap year
                # let's just skip this record for now
                continue
            # if User has BD at 29-Feb, usually he/she celebrates at 28-Feb if non-leap year
            birthday = birthday.replace(day=28)
        birthday_this_year = birthday.replace(year=today.year)
        delta_days = (birthday_this_year - today).days

        # According to the updated information about this task:
        #   we need users for the next 7 days, but
        #   if some BDs are on the nearest weekend: shift them forward to Monday
        #   if today is Monday:
        #       take BDs from the past weekend
        #       and BDs on next weekend are out of 7 days and will be celebrated next Monday

        is_monday = today.weekday() == 0
        min_delta = 0
        if is_monday:
            # on Mondays we want to congrats Users from Saturday and Sunday
            min_delta = -2

        if delta_days < min_delta:
            if delta_days < -(366 - 7):
                birthday_this_year = birthday_this_year.replace(
                    year=today.year + 1
                )
                delta_days = (birthday_this_year - today).days
            else:
                # there is no reason to handle passed BD if today is not Dec
                # and if BD later than 6-Jan even if today is 31-Dec of leap year
                continue
        elif delta_days >= 363 and is_monday:
            # if today is 1..2-Jan Monday
            birthday_this_year = birthday_this_year.replace(
                year=today.year - 1
            )
            delta_days = (birthday_this_year - today).days

        if min_delta <= delta_days < min_delta + 7:
            congrats_at = birthday_this_year.weekday()
            if congrats_at > 4:
                # BD at weekend (days 5 and 6) will congrats at Monday (day 0)
                congrats_at = 0
            if debug:
                print(
                    "BD at {}, in {:>2} days ({:>9}), congrats at {:>9}".format(
                        user["birthday"].date(),
                        delta_days,
                        day_name[birthday_this_year.weekday()],
                        day_name[congrats_at],
                    )
                )
            days[congrats_at].append(user["name"])
    for day in range(7):
        if len(days[day]) > 0:
            print("{}: {}".format(day_name[day], ", ".join(sorted(days[day]))))


if __name__ == "__main__":
    import sys, re
    import json
    from faker import Faker
    from random import randint

    __usage_help_message = """
    Usage:
        python ./birthday.py [<fake_today_ix>]|[<year month day>] [filename] [--users_number=<N>] [--print_users_only]

        <fake_today_ix>:    Use fake date but not today
                                List of fake_todays = [
                                    0: date(2024, 1, 1) # Monday,     leap year
                                    1: date(2024, 1, 2) # Tuesday,    leap year
                                    2: date(1999, 3, 1) # Monday, non-leap year
                                    3: date(1976, 3, 1) # Monday,     leap year
                                    4: date(1998, 3, 2) # Monday, non-leap year
                                ]

        <year month day>:   Use custom Year Month Day (2000 12 1)

        --print_users_only: Print list of user dicts (1000+ items), and exit
        --users_number=<N>: Generate <N> entries + corner cases, not used if [filename], default is 1000 + corner cases
        -h, --help:         Show this message

    Example:
        $python ./birthday.py                       # to run for today with autogenerated input data
        $python ./birthday.py ./users.txt           # to run for today with data from the file
        $python ./birthday.py 3                     # to run for 1999-Mar-1 with autogenerated input data
        $python ./birthday.py 2001 12 4 ./users.txt # to run for 2001-Dec-4 with data from the file
        $python ./birthday.py 2 --users_number=10   # to run for 1999-Mar-1 with autogenerated input data (10 entries + corner cases)
    """

    def __find_years(month, day, weekday, is_leap_year=None):
        years = []
        for i in range(2024, 1899, -1):
            if type(is_leap_year) is bool and isleap(i) != is_leap_year:
                continue
            if date(i, month, day).weekday() == weekday:
                years.append(f"{'*' if isleap(i) else ''}{i}")
        return years

    def __generate_user_birthdays_test_data(
        num: int, add_corner_cases=False, today=None
    ):
        data = []
        fake = Faker()
        for i in range(num):
            d = {
                "name": fake.name(),
                "birthday": datetime.combine(
                    fake.date_between("-80y"), time()
                ),
            }
            data.append(d)
        if add_corner_cases:
            # add users with BD in a range -3..15 days from today
            if today is None:
                today = datetime.today().date()
            for i in range(-3, 9):
                for iters in range(randint(1, 3)):
                    new_date = date(2000, today.month, today.day) + timedelta(
                        days=i
                    )
                    fake_year = int(fake.year())
                    while (
                        new_date.month == 2
                        and new_date.day == 29
                        and not isleap(fake_year)
                    ):
                        fake_year = int(fake.year())
                    new_date = new_date.replace(year=fake_year)
                    d = {
                        "name": fake.name(),
                        "birthday": datetime.combine(new_date, time()),
                    }
                    data.append(d)
        return data

    def __args_parser():
        print_users_only = False
        users_number = 1000
        args = sys.argv[1:]
        for arg in sys.argv[1:]:
            if arg in ("-h", "--help"):
                print(__usage_help_message)
                exit()
            if arg == "--print_users_only":
                print_users_only = True
                args.remove(arg)
            if "--users_number" in arg:
                try:
                    users_number = arg.split("=")
                    users_number = int(users_number[1])
                    args.remove(arg)
                except BaseException as e:
                    print("Error to parse args:", type(e).__name__)
                    exit()
        return args, users_number, print_users_only

    def __get_today(args):
        fake_today = [
            date(2024, 1, 1),  # Monday,     leap year
            date(2024, 1, 2),  # Tuesday,    leap year
            date(1999, 3, 1),  # Monday, non-leap year
            date(1976, 3, 1),  # Monday,     leap year
            date(1998, 3, 2),  # Monday, non-leap year
        ]
        try:
            if len(args) == 0 or not args[0].isdigit():
                today = None
            elif len(args) <= 2:
                today = fake_today[int(args[0])]
            elif len(args) >= 3:
                today = date(int(args[0]), int(args[1]), int(args[2]))
        except BaseException as e:
            print("Error to parse args:", type(e).__name__)
            exit()
        return today

    def __get_users(args, users_number, in_today):
        users = []
        if len(args) == 0 or args[-1].isdigit():
            users = __generate_user_birthdays_test_data(
                users_number, add_corner_cases=True, today=in_today
            )
        else:
            fname = args[-1]
            try:
                with open(fname, "r") as file:
                    for in_data in file.readlines():
                        in_data = (
                            in_data.replace("'", '"')
                            .replace("datetime.", "")
                            .replace("datetime", "")
                            .replace("(", '"')
                            .replace(")", '"')
                        )
                        in_dict = json.loads(in_data)
                        in_date = in_dict["birthday"].split(",")
                        in_date = date(
                            int(in_date[0]), int(in_date[1]), int(in_date[2])
                        )
                        in_dict["birthday"] = datetime.combine(in_date, time())
                        users.append(in_dict)
            except BaseException as e:
                print(
                    f"Error to parse input file '{fname}':", type(e).__name__
                )
                exit()
        return users

    args, users_number, print_users_only = __args_parser()
    fake_today = __get_today(args)
    users = __get_users(args, users_number, fake_today)
    if print_users_only:
        for user in users:
            print(user)
        exit()
    get_birthdays_per_week(users, debug=True, today=fake_today)