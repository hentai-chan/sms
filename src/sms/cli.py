#!/usr/bin/env python3

import argparse
import errno
import random
import sys
from collections import namedtuple

from twilio.base.exceptions import TwilioRestException

from . import core, utils
from .__init__ import __version__, package_name
from .config import CONFIGFILE, GREEN, LOGFILE, RESET_ALL


def cli():
    parser = argparse.ArgumentParser(prog=package_name, description='Twilio CLI for profesional developers.')
    parser._positionals.title = 'Commands'
    parser._optionals.title = 'Arguments'
    parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('--verbose', default=False, action='store_true', help="increase output verbosity (default: %(default)s)")

    subparser = parser.add_subparsers(dest='command')

    log_parser = subparser.add_parser('log', description="interact with the application log")
    log_parser.add_argument('--path', action='store_true', help="return the log file path")
    log_parser.add_argument('--reset', action='store_true', help="purge the log file")
    log_parser.add_argument('--list', action='store_true', help='read the log file')

    config_parser = subparser.add_parser('config', description="configure default application settings")
    config_parser.add_argument('--sid', type=str, nargs='?', help="set the account SID")
    config_parser.add_argument('--token', type=str, nargs='?', help="set the authentication token")
    config_parser.add_argument('--phone', type=str, nargs='?', help="set the twilio phone number")
    config_parser.add_argument('--excuses', type=str, nargs='+', help="define a list of made-up excuses")
    config_parser.add_argument('--add', type=str, nargs=2, metavar=('NAME', 'PHONE'), help="add a new contact")
    config_parser.add_argument('--delete', type=str, nargs=1, metavar='NAME', help="remove a contact")
    config_parser.add_argument('--home',type=str, nargs='?', metavar='NAME', help="name of home contact")
    config_parser.add_argument('--path', action='store_true', help="return the config file path")
    config_parser.add_argument('--reset', action='store_true', help='purge the config file')
    config_parser.add_argument('--list', action='store_true', help="list all user configuration")

    send_parser = subparser.add_parser('send', description="send a SMS back home or to a receiver")
    send_parser.add_argument('--sid', type=str, nargs='?', help="set the account SID")
    send_parser.add_argument('--token', type=str, nargs='?', help="set the authentication token")
    send_parser.add_argument('--phone', type=str, nargs='?', help="set the twilio phone number")
    send_parser.add_argument('--msg', type=str, nargs='?', help="the message to send")
    send_parser.add_argument('--late', action='store_true', help="selects a random excuse to send home")
    send_parser.add_argument('--receiver', type=str, nargs=1, help="name of contact, or a cell phone number")
    send_parser.add_argument('--debug', default=False, action='store_true', help="don't send a message and debug this application")

    args = parser.parse_args()
    config_data = utils.read_json_file(CONFIGFILE)

    if not 'Excuses' in config_data:
        config_data['Excuses'] = [
            "Working hard, I'll be home late.",
            "Gotta ship this feature, this might take a little longer",
            "Staying late, someone fucked the system again.",
            "Stuck in traffic."
        ]

    if not 'Contacts' in config_data:
        config_data['Contacts'] = []

    if args.command == 'log':
        logfile = utils.get_resource_path(LOGFILE)

        if args.path:
            return logfile
        if args.reset:
            utils.reset_file(logfile)
            return
        if args.list:
            with open(logfile, mode='r', encoding='utf-8') as file_handler:
                log = file_handler.readlines()

                if not log:
                    utils.print_on_warning("Nothing to read because the log file is empty")
                    return

                parse = lambda line: line.strip('\n').split('::')
                Entry = namedtuple('Entry', 'timestamp levelname lineno name message')

                tabulate = "{:<20} {:<5} {:<6} {:<12} {:<15}".format

                print('\n' + GREEN + tabulate('Timestamp', 'Line', 'Level', 'File Name', 'Message') + RESET_ALL)

                for line in log:
                    entry = Entry(parse(line)[0], parse(line)[1], parse(line)[2], parse(line)[3], parse(line)[4])
                    print(tabulate(entry.timestamp, entry.lineno.zfill(4), entry.levelname, entry.name, entry.message))

    if args.command == 'config':
        config_file = utils.get_resource_path(CONFIGFILE)

        filter_contact: list=lambda name: [contact for contact in config_data['Contacts'] if contact['Name'] != name.capitalize()]

        if args.sid:
            config_data['AccountSID'] = args.sid
            utils.write_json_file(config_file, config_data)
        if args.token:
            config_data['AuthToken'] = args.token
            utils.write_json_file(config_file, config_data)
        if args.phone:
            config_data['PhoneNumber'] = args.phone
            utils.write_json_file(config_file, config_data)
        if args.excuses:
            config_data['Excuses'] = args.excuses
            utils.write_json_file(config_file, config_data)
        if args.add:
            name, phone = args.add[0].capitalize(), args.add[1]
            config_data['Contacts'] = filter_contact(name)
            config_data['Contacts'].append({'Name': name, 'PhoneNumber': phone})
            utils.write_json_file(config_file, config_data)
        if args.delete:
            config_data['Contacts'] = filter_contact(args.delete[0])
            utils.write_json_file(config_file, config_data)
        if args.home:
            config_data['HomeContact'] = args.home.capitalize()
            utils.write_json_file(config_file, config_data)
        if args.path:
            return config_file
        if args.reset:
            utils.reset_file(config_file)
            return
        if args.list:
            utils.print_dict(config_data)
            return

    if args.command == 'send':
        try:
            sid = args.sid or config_data['AccountSID']
            token = args.token or config_data['AuthToken']
            sender = args.phone or config_data['PhoneNumber']
            receiver = None

            search_contact: list=lambda name: [contact['PhoneNumber'] for contact in config_data['Contacts'] if contact['Name'] == name.capitalize()]

            if args.receiver:
                from_name = search_contact(args.receiver[0])
                receiver = from_name[0] if from_name else args.receiver[0]

            if not (args.receiver or args.late):
                raise ValueError("Expected receiver, got %s" % args.receiver)

            if args.msg:
                core.send_sms(sid, token, sender, receiver, args.msg, args.debug)
                return

            if args.late:
                receiver = search_contact(config_data['HomeContact'])[0]
                excuse = random.choice(config_data['Excuses'])
                core.send_sms(sid, token, sender, receiver, excuse, args.debug)
                return

        except ValueError as error:
            utils.print_on_error("Invalid or no receiver specified.")
            utils.logger.error(str(error))
        except TwilioRestException as error:
            utils.print_on_error("Message delivery failed.")
            utils.logger.error(error.msg)
        except Exception as exception:
            print("Ups, something went wrong. Check the error log.")
            utils.logger.error(str(exception))
