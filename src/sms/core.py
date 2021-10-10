#!/usr/bin/env python3

from datetime import datetime as dt

from twilio.rest import Client

from . import utils
from .config import BRIGHT, GREEN, RESET_ALL, YELLOW


def send_sms(sid: str, token: str, from_: str, to: str, msg: str, debug: bool) -> None:
    if debug:
        utils.print_on_warning(f"Debug mode enabled. Sent message {BRIGHT}{GREEN}{msg}{RESET_ALL} to {to}")
        return

    client = Client(sid, token)
    message = client.messages.create(body=msg, from_=from_, to=to)
    utils.print_on_success(f"Message sent on {BRIGHT}{YELLOW}{dt.today().strftime('%c')}{RESET_ALL}")
