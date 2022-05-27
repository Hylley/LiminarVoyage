import re
from datetime import datetime
from random import randrange, getrandbits


def filter_text(text):
    text = re.sub(r"(?:\@|https?\://)\S+", "", str(text)).lstrip()

    return text


def string_to_date(text, timezone='+00:00'):
    try:
        date = datetime.strptime(text, f'%Y-%m-%d %H:%M:%S{timezone}')
        return date
    except:
        return False


def index(list, ind):
    if len(list) > ind:
        return list[ind]
    else:
        return None


def refactor(num, div):
    division = [num // 5 + (1 if x < num % 5 else 0) for x in range(5)]

    for i in range(5 - div):
        values = []

        for i in range(2):
            n = randrange(len(division))
            values.append(division[n])
            division.pop(n)

        division.insert(randrange(len(division) + 1), values[0] + values[1])

    return division