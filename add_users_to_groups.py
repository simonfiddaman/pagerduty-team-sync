#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Using a source email address, identify a unique user and their Team memberships
Apply all Team memberships to the target user(s), identified by target email address
"""

import os
import json
import logging, logging.config
import sys
from argparse import ArgumentParser
import requests
import pdpyras
pdpyras.APISession.raise_if_http_error = True

SECRETS_FILE = '../secrets.json'
LOGGER_FILE = 'logging.json'


def parse_args():
    """
    Argument parsing is fun!
    """

    parser = ArgumentParser()
    parser.add_argument(
        '--secrets',
        help='Full path to secrets file.',
        metavar='path'
    )
    parser.add_argument(
        '--source',
        help='Email address of an existing user from whom to copy Team memberships.',
        metavar='source'
    )
    parser.add_argument(
        '--target',
        action='append',
        help='Email address(es) of the user(s) to apply the copied Team memberships to.',
        metavar='target'
    )
    return parser.parse_args()


def post_message(webhook, channel, botname, message):
    """
    Push the message to the channel as the botname
    """

    payload = {"channel": channel,
               "username": botname,
               "text": message,
               "icon_emoji": ":thumbsup:"}
    try:
        response = requests.post(webhook, data=json.dumps(payload))
        return response.text
    except requests.exceptions.RequestException as error:
        logging.warning(u'Post message to Slack failed: %s', error)


def main():
    """
    For each user, add them to every team they are not already a member of
    """


    if os.path.exists(LOGGER_FILE):
        with open(LOGGER_FILE, 'rt') as logger_file:
            logging_config = json.load(logger_file)
        logging.config.dictConfig(logging_config)
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    # Parse configuration
    args = parse_args()
    with open(args.secrets or SECRETS_FILE) as secrets:
        secrets = json.load(secrets)
    if args.source is None:
        logging.fatal("No source email address supplied. Exiting.")
        exit(1)
    if args.target is None:
        logging.fatal("No target email address supplied. Exiting.")
        exit(2)

    # instantiate a PagerDuty Python REST API Sessions object
    pdapi = pdpyras.APISession(secrets.get('pagerduty').get('key'))

    # Find source user in PagerDuty API by email address
    user_source = pdapi.find('users', args.source, attribute='email')
    if user_source is None:
        logging.fatal("Supplied source email address (%s) did not match a user. Exiting.", args.source)
        exit(3)
    else:
        logging.info("Found source user %s (%s) with %d Teams", user_source.get('name'), user_source.get('email'), len(user_source.get('teams')))
        for team in user_source.get('teams'):
            logging.debug("Source Team: %s: %s", team.get('id'), team.get('summary'))

    # Find target user(s) in PagerDuty API by email address
    for target in args.target:
        try:
            user_target = pdapi.find('users', target, attribute='email')
        except pdpyras.PDClientError as error:
            logging.critical(error)
            exit(4)
        if user_target is None:
            logging.error("Supplied target email address (%s) did not match a user.", target)
        else:
            logging.info("Found target user %s (%s) with %d Teams", user_target.get('name'), user_target.get('email'), len(user_target.get('teams')))
            for team in user_source.get('teams'):
                # scan the target user's teams for this team id - don't add them if it's already present
                if not any(d['id'] == team.get('id') for d in user_target.get('teams')):
                    method = '/teams/{:s}/users/{:s}'.format(team.get('id'), user_target.get('id'))
                    response = pdapi.request('PUT', method)
                    if response.ok:
                        logging.info("User %s (%s) added to Team %s: %s", user_target.get('name'), user_target.get('email'), team.get('id'), team.get('summary'))
                    else:
                        logging.warning("User%s (%s) WAS NOT added to Team %s: %s", user_target.get('name'), user_target.get('email'), team.get('id'), team.get('summary'))
                else:
                    logging.info("User %s is already a member of %s", user_target.get('name'), team.get('summary'))



if __name__ == '__main__':
    sys.exit(main())
