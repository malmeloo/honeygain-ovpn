#!/usr/bin/env python3

import logging
import os
import re
import sys
import time

import docker
import docker.errors
import honeygain

logging.basicConfig(level=logging.INFO)

EMAIL = os.environ.get('HONEYGAIN_EMAIL')
PASS = os.environ.get('HONEYGAIN_PASS')
ROOT = os.environ.get('ROOT')

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


###################################################


def _get_devices():
    active_devices = set()
    inactive_devices = set()
    total = 0
    for device in hg.get_devices():
        total += 1
        matches = DEVICENAME_RE.match(device.name)
        if matches:
            if device.status == 'active':
                active_devices.add(matches.group(1).lower())
            else:
                inactive_devices.add(matches.group(1).lower())

    return active_devices, inactive_devices, total


def _get_configs():
    configs = set()
    for file in os.listdir('/app/configs'):
        matches = CONFIG_RE.match(file)
        if matches:
            configs.add(matches.group(1))

    return configs


###############################################


def _remove_client(code):
    try:
        container = docker_client.containers.get(f'DOCKER_{code.upper()}')
        container.remove(force=True)
    except docker.errors.NotFound:  # already removed
        pass
    logging.info(f'Removed client {code}')


def _restart_client(code):
    try:
        container = docker_client.containers.get(f'honeygain-{code}')
        container.restart()
        logging.info(f'Restarted client {code}')
    except docker.errors.NotFound:
        logging.warning(f'Remote client {code} not found running locally')
        return _start_client(code)


def _start_client(code):
    logging.info('Starting client ' + code)
    config_path = os.path.join(ROOT, 'configs', f'config-{code}.ovpn')
    dev_name = f'DOCKER_{code.upper()}'

    docker_client.containers.run(
        image='honeygain-ovpn',
        name=f'honeygain-{code}',
        command=f'-tou-accept -email {EMAIL} -pass {PASS} -device {dev_name}',
        detach=True,

        volumes=[f'{config_path}:/config.ovpn'],
        privileged=True,
        sysctls={'net.ipv6.conf.all.disable_ipv6': '0'},
        cap_add=['NET_ADMIN']
    )
    logging.info('Started container for ' + code)


################################################


def run_once():
    logging.info(' --- Running manager tasks')

    active_devices, inactive_devices, dev_count = _get_devices()
    all_devices = active_devices | inactive_devices
    configs = _get_configs()

    to_remove = all_devices - configs
    to_restart = inactive_devices - to_remove
    to_add = configs - all_devices

    max_new_dev_count = 10 - dev_count
    if len(to_add) > max_new_dev_count:
        logging.warning(f'Limiting new devices to {max_new_dev_count}')
        to_add = set(list(to_add)[:max_new_dev_count])

    if client.can_claim_credits:
        winnings = client.claim_credits()
        print(f"Claimed your daily credits! ({winnings})")

    for device in to_remove:
        _remove_client(device)
    for device in to_restart:
        _restart_client(device)
    for device in to_add:
        _start_client(device)

    logging.info(' --- Manager done')


def main():
    me = hg.get_profile()
    logging.info('Logged in as ' + me.email)

    try:
        while True:
            run_once()
            time.sleep(60 * 15)

    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    sys.exit(main())
