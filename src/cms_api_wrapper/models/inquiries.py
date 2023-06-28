from src.cms_api_wrapper.cms_api_adapter import *


class InquiryRecord:
    def __init__(self, category, inquiry_id, subject, size_estimate):
        self.category: str = category
        self.inquiry_id: str = inquiry_id
        self.description: str = subject
        self.size_estimate: int = size_estimate


class InquiresCatalogGetResponse(WebServiceResponse):
    def __init__(self, result: ApiResult):
        """
        Deconstructs the response to expose the 'catalog properties'.
        :param result: The result of the API request
        """
        super().__init__(result)

        # TODO: Find better way to do this
        self.inquiries = []
        inquiry_list = result.data["Inquiries"]
        for rec in inquiry_list:
            self.inquiries.append(InquiryRecord(
                rec["Category"],
                rec["InquiryId"],
                rec["Subject"],
                rec["SizeEstimate"],
            ))


class Inquires:
    """
    Provides methods and classes relating winlink inquires
    """
    def __init__(self, api_key: str, hostname: str = 'api.winlink.org', logger: logging.Logger = None):
        self.cms_api = CmsApiAdapter(api_key, hostname, logger)

    async def catalog_get(self):
        """
        Returns a list of winlink catalog items
        """
        result = await self.cms_api.get("inquiries/catalog/")
        return InquiresCatalogGetResponse(result)
