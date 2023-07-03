from src.cms_api_wrapper.models.account import *
from src.cms_api_wrapper.models.sysop import *
from src.cms_api_wrapper.models.inquiries import *

import asyncio
# import logging
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

    # if the test was already run today might have to manually delete the account
    # for this first action to succeed. The test db is refreshed daily.
    print(f"Adding account {callsign2}")
    result = await account.add_callsign_account(callsign2, password)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")

    # this one should fail once the new api version is pushed
    print(f"Adding account {callsign2}")
    result = await account.add_callsign_account(callsign2, password)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")

    result = await account.validate_password(callsign, password)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"Password check for: {callsign}/{password} is valid: {result.is_valid}")
    result = await account.validate_password(callsign, "BadPass")
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"Password check for: {callsign}/BadPass is valid: {result.is_valid}")

    #
    result = await account.account_exists(callsign)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"Account '{callsign}' exists: {result.exists}")
    result = await account.account_exists("DU0MMY")
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
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
    #

    result = await account.set_password_recovery_email_address(callsign, password, "lee@iqed.net")
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    result = await account.send_password(callsign)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"Requested that password for {callsign} be sent to  the recovery address.")

    # Should get an error if no recovery address is set
    await account.set_password_recovery_email_address(callsign, password, "")
    result = await account.send_password(callsign)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"Requested that password for {callsign} be sent to  the recovery address.")

    test_callsign = "AA7NG"
    result = await account.get_locked_out(test_callsign)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"Account {test_callsign} is locked out: {result.is_locked_out} -- Reason: {result.lockout_reason}")

    await account.set_max_message_size(callsign, 105)
    result = await account.get_max_message_size(callsign)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"Max message size: {result.max_message_size}")
    await account.set_max_message_size(callsign, 120)

    inquiries = Inquires(api_key, hostname)
    result = await inquiries.catalog_get()
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"{len(result.inquiries)} items in the inquiry list")

    sysop = Sysop(api_key, hostname)
    result = await sysop.sysop_add(callsign, password, "Ham Tester", "DM78QX", "account.email@home.com")
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")

    result = await sysop.sysop_get(callsign, password)
    if result.has_error:
        print(f"Error: {result.error_code}/{result.error_message}")
    else:
        print(f"Sysop: {result.sysop_record.sysop_name}")

asyncio.run(main())
