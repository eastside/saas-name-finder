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

            if 5 <= len(name) <= 7:
                count += 1

                for suffix in suffixes:
                    complete_name = name + suffix
                    if domain_taken(complete_name):
                        print('.', end='', flush=True)
                    else:
                        print(f"\n{complete_name}\tAVAILABLE!\n", end='', flush=True)

    finally:
        print('count = ', count)

