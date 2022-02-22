#!/usr/bin/env python3

import logging
import os
import sys

import honeygain

logging.basicConfig(level=logging.INFO)

EMAIL = os.environ.get('HONEYGAIN_EMAIL')
PASS = os.environ.get('HONEYGAIN_PASS')

if not (EMAIL and PASS):
    logging.error('You must specify both HONEYGAIN_EMAIL and HONEYGAIN_PASS.')
    sys.exit(1)

client = honeygain.Client()
try:
    with open('data/jwt-token.txt', 'r') as file:
        logging.info('Logging in using stored credentials')
        client.token = file.read().strip()
except FileNotFoundError:
    logging.info('Logging in...')
    client.login(EMAIL, PASS)

    with open('data/jwt-token.txt', 'w+') as file:
        logging.info('Saving credentials for next start')
        file.write(client.token)


def _get_online_devices():
    devices = client.get_devices()
    active_devices = [d.name for d in devices if d.status == 'active']

    return active_devices


def main():
    me = client.get_profile()
    logging.info('Logged in as ' + me.email)

    devices = _get_online_devices()
    print(devices)


if __name__ == '__main__':
    sys.exit(main())
