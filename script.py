import argparse


parser = argparse.ArgumentParser(description=\
"""Saas name finder!

Reads English words from stdin and checks if they're avialable under the given suffixes.


ex:

python3 script.py .app app.com .tech tech.com < words.txt
"""
)
parser.add_argument(
    'suffixes', type=str, nargs='+', help='list of suffixes to check, i.e., `.app`'
)
args = parser.parse_args()
suffixes = args.suffixes


import os
import sys
import whois
import time
import signal


COLOR_END = "\x1b[39m"
F_Red = "\x1b[31m"
F_Green = "\x1b[32m"
F_Yellow = "\x1b[33m"
F_Blue = "\x1b[34m"
F_Magenta = "\x1b[35m"
F_Cyan = "\x1b[36m"


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
        # print(f"domain {domain_name} failed to get ip, {e}")
        return True
    return True


def domain_registry(domain_name):
    """Returns the registered domain name"""
    try:
        with timeout(seconds=1):
            entry = whois.whois(domain_name)
    except Exception as e:
        # print(f"domain {domain_name} lookup failed due to {e}")
        return False
    else:
        # print(f"domain_registered({domain_name}) ", entry.domain_name)
        return entry.domain_name


def domain_taken(domain_name):
    # print('i')
    if domain_has_ip(domain_name):
        return True
    # print('d')
    if domain_registry(domain_name):
        return True
    return False


_scrabble_file = open('scrabble-words.txt')
_scrabble_words = _scrabble_file.read()
_scrabble_words_set = set(word.lower() for word in _scrabble_words.split('\n'))


def word_is_english(name):
    if name in _scrabble_words_set:
        return True


if __name__ == "__main__":
    print("starting up...")
    count = 0

    try:
        for line in sys.stdin:
            name = line.rstrip()
            name = name.lower()
            name, *_ = name.split('\t', 1)

            if any(map(name.endswith, ['ed', 's', 'ing', 'ly', 'ize', 'able', 'ish', 'er'])):
                continue

            if not word_is_english(name):
                continue

            if 5 <= len(name) <= 7:
                count += 1

                for suffix in suffixes:
                    complete_name = name + suffix
                    if domain_taken(complete_name):
                        print('.', end='', flush=True)
                    else:
                        print(f"\n{complete_name}\tAVAILABLE!\n", end='', flush=True)

                # domain_tech = name + '.tech'
                # domain_nametech = name + 'tech.com'
                # domain_app = name + '.app'
                # domain_nameapp = name + 'app.com'
                # # print(f'trying {domain}')

                # if domain_taken(domain_tech):
                #     print('.', end='', flush=True)
                # elif domain_taken(domain_nametech):
                #     print(F_Red + '.' + COLOR_END, end='', flush=True)
                # elif domain_taken(domain_app):
                #     print(F_Green + '.' + COLOR_END, end='', flush=True)
                # elif domain_taken(domain_nameapp):
                #     print(F_Yellow + '.' + COLOR_END, end='', flush=True)
                # else:
                #     print(f"\n{name}\tAVAILABLE!\n", end='', flush=True)

    finally:
        print('count = ', count)
        _scrabble_file.close()

