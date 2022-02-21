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


client = honeygain.Client()
try:
    with open('data/jwt-token.txt', 'r') as file:
        print('[-] Logging in using stored credentials')
        client.token = file.read().strip()
except FileNotFoundError:
    print('[-] Logging in...')
    client.login(EMAIL, PASS)

    with open('data/jwt-token.txt', 'w+') as file:
        print('[-] Saving credentials for next start')
        file.write(client.token)


def main():
    print('Successfully logged in')


if __name__ == '__main__':
    sys.exit(main())
