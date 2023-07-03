from src.cms_api_wrapper.cms_api_adapter import *
from src.cms_api_wrapper.models.constants import *


class SysopRecord:
    def __init__(self, result: ApiResult):
        sysop_rec = result.data["Sysop"]
        self.callsign: str = sysop_rec["Callsign"]
        self.grid_square: str = sysop_rec["GridSquare"]
        self.sysop_name: str = sysop_rec["SysopName"]
        self.street_address_1: str = sysop_rec["StreetAddress1"]
        self.street_address_2: str = sysop_rec["StreetAddress2"]
        self.city: str = sysop_rec["City"]
        self.state: str = sysop_rec["State"]
        self.country: str = sysop_rec["Country"]
        self.postal_code: str = sysop_rec["PostalCode"]
        self.email: str = sysop_rec["Email"]
        self.phones: str = sysop_rec["Phones"]
        self.website: str = sysop_rec["Website"]
        self.comments: str = sysop_rec["Comments"]


class SysopGetResponse(WebServiceResponse):
    def __init__(self, result: ApiResult):
        """
        Deconstructs the response to expose the sysop information.
        :param result: The result of the API request
        """
        super().__init__(result)
        self.sysop_record = SysopRecord(result)


class Sysop:
    """
    Provides methods and classes relating to a sysop settings
    """

    def __init__(self, api_key: str, hostname: str = CMS_API_HOSTNAME, logger: logging.Logger = None):
        self.cms_api = CmsApiAdapter(api_key, hostname, logger)

    async def sysop_add(self, callsign: str, password: str, sysop_name: str, grid_square: str, email: str,
                        address1: str = "", address2: str = "", city: str = "", state: str = "",
                        country: str = "", postal_code: str = "", phones: str = "", website: str = "",
                        comments: str = "") -> WebServiceResponse:
        """
        Add sysop information to the callsign account.
        """
        params = {"Callsign": callsign, "Password": password, "SysopName": sysop_name, "GridSquare": grid_square,
                  "Email": email, "StreetAddress1": address1, "StreetAddress2": address2, "City": city,
                  "State": state, "Country": country, "PostalCode": postal_code, "Phones": phones,
                  "Website": website, "Comments": comments}
        result = await self.cms_api.get("sysop/add/", params)
        return WebServiceResponse(result)

    async def sysop_get(self, callsign: str, password: str) -> SysopGetResponse:
        """
        Get sysop information for this account.
        """
        params = {"Callsign": callsign, "Password": password}
        result = await self.cms_api.get("sysop2/get", params)
        return SysopGetResponse(result)
