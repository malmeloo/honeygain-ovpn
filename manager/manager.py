#!/usr/bin/env python3

import logging
import os
import re
import sys

import docker
import docker.errors
import honeygain

logging.basicConfig(level=logging.INFO)

EMAIL = os.environ.get('HONEYGAIN_EMAIL')
PASS = os.environ.get('HONEYGAIN_PASS')

DEVICENAME_RE = re.compile(r'DOCKER_(\w+)')
CONTAINER_RE = re.compile(r'honeygain-(\w+)')
CONFIG_RE = re.compile(r'config-(\w+)\.ovpn')

if not (EMAIL and PASS):
    logging.error('You must specify both HONEYGAIN_EMAIL and HONEYGAIN_PASS.')
    sys.exit(1)

docker_client = docker.from_env()
hg = honeygain.Client()
try:
    with open('data/jwt-token.txt', 'r') as token_file:
        logging.info('Logging in using stored credentials')
        hg.token = token_file.read().strip()
except FileNotFoundError:
    logging.info('Logging in...')
    hg.login(EMAIL, PASS)

    with open('data/jwt-token.txt', 'w+') as token_file:
        logging.info('Saving credentials for next start')
        token_file.write(hg.token)


def _get_devices():
    active_devices = set()
    inactive_devices = set()
    for device in hg.get_devices():
        matches = DEVICENAME_RE.match(device.name)
        if matches:
            if device.status == 'active':
                active_devices.add(matches.group(1).lower())
            else:
                inactive_devices.add(matches.group(1).lower())

    return active_devices, inactive_devices


def _get_configs():
    configs = set()
    for file in os.listdir('/app/configs'):
        matches = CONFIG_RE.match(file)
        if matches:
            configs.add(matches.group(1))

    return configs


def _restart_container(code):
    try:
        container = docker_client.containers.get(f'honeygain-{code}')
        container.restart()
        logging.info(f'Restarted client {code}')
    except docker.errors.NotFound:
        logging.warning(f'Remote client {code} not found running locally')
        return


def main():
    me = hg.get_profile()
    logging.info('Logged in as ' + me.email)

    active_devices, inactive_devices = _get_devices()
    all_devices = active_devices | inactive_devices
    configs = _get_configs()

    to_remove = all_devices - configs
    to_add = configs - active_devices

    for device in to_remove:
        print('Removing device ' + device)
    for device in to_add:
        print('Adding device ' + device)


if __name__ == '__main__':
    sys.exit(main())
