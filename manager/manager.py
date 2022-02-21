#!/usr/bin/env python3

import docker
import honeygain
import os
import sys


EMAIL = os.environ.get('HONEYGAIN_EMAIL')
PASS = os.environ.get('HONEYGAIN_PASS')

if not (EMAIL and PASS):
    print('You must specify both HONEYGAIN_EMAIL and HONEYGAIN_PASS.')
    sys.exit(1)


print('[-] Logging in...')
client = honeygain.Client()
try:
    with open('data/jwt-token.txt') as file:
        client.token = file.read().strip()
except FileNotFoundError:
    client.login(EMAIL, PASS)


def main():
    print('Successfully logged in')


if __name__ == '__main__':
    sys.exit(main())
