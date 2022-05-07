import re

def filter_text(text):
    text = re.sub(r"(?:\@|https?\://)\S+", "", str(text)).lstrip()

    return text