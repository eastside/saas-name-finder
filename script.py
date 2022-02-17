import argparse


parser = argparse.ArgumentParser(description=\
"""Saas name finder!

Reads English words from stdin, and prints only those words that are AVAIALLBE
under ALL suffixes.

For example, if you want to check what names are available under {name}.app, 
{name}.dev, and {name}app.com, then you'll want

ex:

>>> python3 script.py .app .dev app.com < words.txt

if a word  
"""
)
parser.add_argument(
    'suffixes', type=str, nargs='+', help='list of suffixes to check, i.e., `.app` or`.dev`'
)
meh_word_endings = ['ied', 's', 'ing', 'ly', 'ize', 'able', 'ish', 'er', 'iest', 'ate', 'ism', 'ed']
parser.add_argument(
    '--ban-meh-word-endings', 
    default=True, 
    help=f"Words that end in {meh_word_endings} will not be checked"
)
parser.add_argument(
    '--max-len',
    default=7,
    help=f"Words longer than this will not be checked"
)
args = parser.parse_args()
suffixes = args.suffixes
ban_meh_word_endings = args.ban_meh_word_endings
max_len = args.max_len

import os
import sys
import whois
import time
import signal


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def domain_has_ip(domain_name):
    """Returns True if the domain is open"""
    try:
        with timeout(seconds=1):
            out = os.popen(f'host {domain_name}')
            output = out.readlines()
            for line in output:
                if "NXDOMAIN" in line:
                    return False
    except Exception as e:
        return True
    return True


def domain_registry(domain_name):
    """Returns the registered domain name"""
    try:
        with timeout(seconds=1):
            entry = whois.whois(domain_name)
    except Exception as e:
        return False
    else:
        return entry.domain_name


def domain_taken(domain_name):
    if domain_has_ip(domain_name):
        return True
    if domain_registry(domain_name):
        return True
    return False


def word_is_english(name):
    if name in _scrabble_words_set:
        return True

COLOR_END = "\x1b[39m"
F_Red = "\x1b[31m"
F_Green = "\x1b[32m"
F_Yellow = "\x1b[33m"
F_Blue = "\x1b[34m"
F_Magenta = "\x1b[35m"
F_Cyan = "\x1b[36m"

if __name__ == "__main__":
    print(F_Blue + "finding your next product name!" + COLOR_END)
    print(F_Cyan + f"skipping words ending in {meh_word_endings}" + COLOR_END)
    print(F_Cyan + f"skipping words longer than {max_len} characters" + COLOR_END)
    print(F_Yellow + f"if a name appears below, it's available under ALL suffixes {', '.join(suffixes)}!" + COLOR_END)
    count = 0
    matches = 0

    try:
        for line in sys.stdin:
            name = line.rstrip()
            name = name.lower()

            # These seem like bad names
            if ban_meh_word_endings and any(map(name.endswith, meh_word_endings)):
                continue

            if len(name) > max_len:
                continue

            count += 1

            for suffix in suffixes:
                complete_name = name + suffix
                if domain_taken(complete_name):
                    # print('.', end='', flush=True)
                    break
            else:
                matches += 1
                print(f"{name}\n", end='', flush=True)

    finally:
        print('done! total names checked = {count} total matches = {matches}')

