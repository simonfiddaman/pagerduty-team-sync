# add_users_to_groups

Supplying a source email address and target email address(es), copy all Team memberships from the user identified by source email address to each user identified by target email address.

## Overview

This script (`add_users_to_groups`):

* uses the [PagerDuty Python REST API Sessions library](https://pagerduty.github.io/pdpyras/)
* identifies the source user by email address
* identifies the target user(s) by email address
* adds the target user(s) to all Teams the source user is a member of

You may use a PagerDuty API User token.

## Requirements

1. This script uses Python 3.4+ and Python-Requests version 2.12+ and PDPYRAS version 2.4.1+
2. PagerDuty personal API token (My Profile -> User Settings -> API Access).

## Configuration

1. Copy `../secrets.json.example` to `../secrets.json`
2. Add your configuration items:
    ```JSON
    {
      "pagerduty":{
        "key":"your-personal-API-key"
      }
    }
    ```

## Instructions

```bash
usage: add_users_to_groups.py [-h] [--secrets path] [--config path]
                              [--source source] [--target target]

optional arguments:
  -h, --help       show this help message and exit
  --secrets path   Full path to secrets file.
  --config path    Full path to config file.
  --source source  Email address of an existing user from whom to copy Team
                   memberships.
  --target target  Email address(es) of the user(s) to apply the copied Team
                   memberships to.
```

## Example Outputs

On the console:

```bash
python3 add_users_to_groups.py --source s.user@example.com --target t1.user@example.com --target t2.user@example.com
INFO - Found source user Source User (s.user@example.com) with 24 Teams
INFO - Found target user Target One User (t1.user@example.com) with 0 Teams
INFO - User Target One User (t1.user@example.com) added to Team PXXXXXX: Team One
[...]
INFO - Found target user Target Two User (t1.user@example.com) with 0 Teams
INFO - User Target Two User (t2.user@example.com) added to Team PXXXXXX: Team One
[...]
```
