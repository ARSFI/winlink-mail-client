from src.cms_api_wrapper.cms_api_adapter import *
from src.cms_api_wrapper.models.constants import *


class AccountExistsResponse(WebServiceResponse):
    def __init__(self, result: ApiResult):
        """
        Deconstructs the response to expose the 'CallsignExists' api result.
        :param result: The result of the API request
        """
        super().__init__(result)
        self.exists: bool = result.data["CallsignExists"]


class ValidatePasswordResponse(WebServiceResponse):
    def __init__(self, result: ApiResult):
        """
        Deconstructs the response to expose the 'IsValid' api result.
        :param result: The result of the API request
        """
        super().__init__(result)
        self.is_valid: bool = result.data["IsValid"]


class ForwardingAddressResponse(WebServiceResponse):
    def __init__(self, result: ApiResult):
        """
        Deconstructs the response to expose the 'AlternateEmailGet' api result.
        :param result: The result of the API request
        """
        super().__init__(result)
        self.forwarding_address: str = result.data["AlternateEmail"]
        # Strip leading 'SMTP:' if it exists
        self.forwarding_address = self.forwarding_address.replace('SMTP:', '')


class PasswordRecoveryResponse(WebServiceResponse):
    def __init__(self, result: ApiResult):
        """
        Deconstructs the response to expose the 'PasswordRecoveryEmailGet' api result.
        :param result: The result of the API request
        """
        super().__init__(result)
        self.recovery_address: str = result.data["RecoveryEmail"]


class MaxMessageSizeResponse(WebServiceResponse):
    def __init__(self, result: ApiResult):
        """
        Deconstructs the response to expose the 'MaxMessageSize' api result.
        :param result: The result of the API request
        """
        super().__init__(result)
        self.max_message_size: str = result.data["MaxMessageSize"]


class LockedOutResponse(WebServiceResponse):
    def __init__(self, result: ApiResult):
        """
        Deconstructs the response to expose the 'LockedOut' api result.
        :param result: The result of the API request
        """
        super().__init__(result)
        self.is_locked_out: bool = result.data["LockedOut"]
        self.lockout_reason = ""


class Account:
    """
    Provides methods and classes relating to a callsign (and sometimes a tactical) account
    """
    def __init__(self, api_key: str, hostname: str = CMS_API_HOSTNAME, logger: logging.Logger = None):
        self.cms_api = CmsApiAdapter(api_key, hostname, logger)

    async def account_exists(self, callsign: str) -> AccountExistsResponse:
        """
        Returns a true response if the account exists and is not blocked, False otherwise.
        """
        params = {"Callsign": callsign}
        result = await self.cms_api.get("account/exists/", params)
        return AccountExistsResponse(result)

    async def add_callsign_account(self, callsign: str, password: str, email_address: str = "") -> WebServiceResponse:
        """
        Adds a new account for the provided callsign.
        Optionally, sets the email address used for password recovery.
        """
        params = {"Callsign": callsign, "Password": password, "RecoveryEmail": email_address}
        result = await self.cms_api.post("account/add/", params)
        return WebServiceResponse(result)

    async def change_account_password(self, callsign: str, old_password: str, new_password: str) -> WebServiceResponse:
        """
        Changes the account password if the old password is verified.
        """
        params = {"Callsign": callsign, "OldPassword": old_password, "NewPassword": new_password}
        result = await self.cms_api.post("account/password/change/", params)
        return WebServiceResponse(result)

    async def validate_password(self, callsign: str, password: str):
        """
        Verifies that the password is valid for this account
        """
        params = {"Callsign": callsign, "Password": password}
        result = await self.cms_api.post("account/password/validate/", params)
        return ValidatePasswordResponse(result)

    async def get_forwarding_email_address(self, callsign: str, password: str):
        """
        Gets the alternate(forwarding) address for the callsign account.
        """
        params = {"Callsign": callsign, "Password": password}
        result = await self.cms_api.get("account/alternateEmail/get", params)
        return ForwardingAddressResponse(result)

    async def set_forwarding_email_address(self, callsign: str, password: str,
                                           email_address: str) -> WebServiceResponse:
        """
        Sets the alternate(forwarding) address for the callsign account. The email address
        must be a standard internet address (no winlink addresses).
        """
        params = {"Callsign": callsign, "Password": password, "AlternateEmail": email_address}
        result = await self.cms_api.post("account/alternateEmail/set", params)
        return WebServiceResponse(result)

    async def send_password(self, callsign: str):
        """
        Requests that the account password be sent to the password recovery email address on record.
        """
        params = {"Callsign": callsign}
        result = await self.cms_api.post("account/password/send", params)
        return WebServiceResponse(result)

    async def get_password_recovery_email_address(self, callsign: str,
                                                  password: str) -> PasswordRecoveryResponse:
        """
        Gets the password recovery address for the callsign account.
        """
        params = {"Callsign": callsign, "Password": password}
        result = await self.cms_api.get("account/password/recovery/email/get", params)
        return PasswordRecoveryResponse(result)

    async def set_password_recovery_email_address(self, callsign: str, password: str,
                                                  email_address: str) -> WebServiceResponse:
        """
        Sets the password recovery address for the callsign account. The email address
        must be a standard internet address (no winlink addresses).
        """
        params = {"Callsign": callsign, "Password": password, "RecoveryEmail": email_address}
        result = await self.cms_api.post("account/password/recovery/email/set", params)
        return WebServiceResponse(result)

    async def get_locked_out(self, callsign: str) -> LockedOutResponse:
        """
        Gets the locked out status for the callsign account. If the account is locked out
        the response will contain the reason for the lockout (if any was recorded).
        """
        params = {"Callsign": callsign}
        result = await self.cms_api.get("account/lockedOut/get", params)
        locked_out_response = LockedOutResponse(result)
        if locked_out_response.is_locked_out:
            # Add the reason for the account being locked out to the response
            result = await self.cms_api.get("account/lockedOutReason/get", params)
            if result.data:
                locked_out_response.lockout_reason = result.data["Reason"]
        return locked_out_response

    async def get_max_message_size(self, callsign: str):
        """
        Gets the message size limit stored for this account
        """
        params = {"Callsign": callsign}
        result = await self.cms_api.get("account/maxMessageSize/get", params)
        return MaxMessageSizeResponse(result)

    async def set_max_message_size(self, callsign: str, max_size: int):
        """
        Sets the message size limit for this account (max is 120K)
        """
        params = {"Callsign": callsign, "MaxMessageSize": max_size}
        result = await self.cms_api.get("account/maxMessageSize/set", params)
        return WebServiceResponse(result)
