import os.path
import random
import string


def gen_token():
    charset = random.choices(string.digits + string.ascii_letters, k=24)
    return ''.join(charset)


def refactor_filename(path):
    i = 1
    root, ext = os.path.splitext(path)
    while True:
        yield '%s(%d)%s' % (root, i, ext)
        i += 1
