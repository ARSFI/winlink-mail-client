from src.cms_api_wrapper.models.account import *
from src.cms_api_wrapper.models.inquiries import *

import asyncio
# import logging
import json
import os
from dotenv import load_dotenv


# Get the API key
load_dotenv()
api_key = os.getenv("API_KEY")
hostname = "cms-z.winlink.org"

# logging.basicConfig(level=logging.DEBUG)

callsign = "ZZ0TST"
callsign2 = "ZZ2TST"
password = "CTCH22"


async def main():
    account = Account(api_key, hostname)

    # might have to manually delete the account for this first action to succeed
    # if the test was already run today. The test db is refreshed daily
    result = await account.add_callsign_account(callsign2, password)
    print(f"Add account {callsign2} Has error: {result.has_error} -- Error: {result.error_code}")

    # this one should fail once the new api version is pushed
    print(f"Adding account {callsign2}")
    result = await account.add_callsign_account(callsign2, password)
    print(f"Add account {callsign2} Has error: {result.has_error} -- Error: {result.error_code}")

    result = await account.validate_password(callsign, password)
    print(f"Password check for: {callsign}/{password} is valid: {result.is_valid}")
    result = await account.validate_password(callsign, "BadPass")
    print(f"Password check for: {callsign}/BadPass is valid: {result.is_valid}")

    #
    result = await account.account_exists(callsign)
    print(f"Account '{callsign}' exists: {result.exists}")
    result = await account.account_exists("DU0MMY")
    print(f"Account 'DU0MMY' exists: {result.exists}")

    #
    # await account.change_account_password(callsign, password, "ABC123")
    # result = await account.change_account_password(callsign, "ABC123", password)
    # print(json.dumps(result.__dict__))
    #
    # result = await account.set_forwarding_email_address(callsign, password, "lee@iqed.net")
    # print(json.dumps(result.__dict__))
    #
    # result = await account.get_forwarding_email_address(callsign, password)
    # print(result.forwarding_address)
    #
    # result = await account.set_password_recovery_email_address(callsign, password, "sam@iam.net")
    # print(json.dumps(result.__dict__))
    # result = await account.get_password_recovery_email_address(callsign, password)
    # print(result.recovery_address)
    # result = await account.set_password_recovery_email_address(callsign, password, "lee@iqed.net")
    # print(json.dumps(result.__dict__))
    #
    # result = await account.get_locked_out(callsign)
    # print(json.dumps(result.__dict__))
    #

    test_callsign = "AA7NG"
    result = await account.get_locked_out(test_callsign)
    print(f"Account {test_callsign} is locked out: {result.is_locked_out} -- Reason: {result.reason}")

    inquiries= Inquires(api_key, hostname)
    result = await inquiries.catalog_get()
    print(f"{len(result.inquiries)} items in the inquiry list")

asyncio.run(main())
