<p align="center">
  <a title="Project Logo">
    <img height="150" style="margin-top:15px" src="https://www.twilio.com/docs/static/company/img/logos/red/twilio-mark-red.cda4b5cd0.svg">
  </a>
</p>

<h1 align="center">Twilio Terminal SMS</h1>

<p align="center">
    <a href="https://github.com/hentai-chan/sms" title="Release Version">
        <img src="https://img.shields.io/badge/Release-0.0.2%20-blue">
    </a>
    <a href="https://github.com/hentai-chan/sms/actions/workflows/python-app.yml" title="Unit Tests">
        <img src="https://github.com/hentai-chan/sms/actions/workflows/python-app.yml/badge.svg">
    </a>
    <a title="Supported Python Versions">
        <img src="https://img.shields.io/badge/Python-3.8%20%7C%203.9%20-blue">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" title="License Information" target="_blank" rel="noopener noreferrer">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
    <a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/hentai-chan/sms" title="Software Heritage Archive" target="_blank" rel="noopener noreferrer">
        <img src="https://archive.softwareheritage.org/badge/origin/https://github.com/hentai-chan/sms.git/">
    </a>
</p>

## Setup

<details>
<summary>Installation</summary>

[pipx](https://pypa.github.io/pipx/) is the recommended way to install
Python applications in an isolated environment:

```cli
pipx install git+https://github.com/hentai-chan/sms.git
```

Fire up a debug build in `./venv`:

```cli
git clone https://github.com/hentai-chan/sms.git
cd ./speedtest
python -m venv venv/
source venv/bin/activate
pip install -e .
```

</details>

## Configuration

<details>
<summary>Customize Application Settings</summary>

To send a SMS over `twilio` you need to set these three values in the configuration file:

```cli
sms config --token <auth_token>
sms config --sid <account_sid>
sms config --phone <twilio_number>
```

Before you register a new `twilio` phone number, make sure its able to send a SMS to
other cell phones. If you didn't sign up for a subscription, you will only be able to
send a SMS to your own cell phone that you registered with this website. In general,
cell phone numbers that you want to send a message to need to contain the country code.

Optional: Define an array of excuses that are to be sent (at random) when you use
the `--late` option.

```cli
sms config --excuses <excuse1,excuse2,...>
```

Add a new contact to your address book:

```cli
sms config --add <name> <phone>
```

Read the configuration file:

```cli
sms config --list
```

Get help:

```cli
sms --help
```

</details>

## Basic Usage

<details>
<summary>Command Line Usage</summary>

Send a message. Either pass a contact `name` from your address book, or pass a
phone number that you want to send a message to:

```cli
sms send --msg <msg> --receiver <phone>
```

You can use the dry run option to preview the command invocation:

```cli
sms send --msg "Hello, World!" --receiver haydee --dry-run
```

```cli
sms send --late
```

Note: You need to configure a home contact (e.g. your significant other) with

```cli
sms config --add <name> <phone>
sms config --home <name>
```

first for this option to work.

</details>

## Report an Issue

Did something went wrong? Copy and paste the information from

```cli
sms log --list
```

to file a new bug report.
