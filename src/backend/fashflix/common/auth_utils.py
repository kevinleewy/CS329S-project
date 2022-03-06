import string
import random

def get_random_string(n):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))
