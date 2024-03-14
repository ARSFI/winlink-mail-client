import json
import logging
from http import HTTPStatus
from json import JSONDecodeError
from types import SimpleNamespace
from typing import List, Dict
import httpx


class ApiResult:
    """
    The result of the API request
    """

    def __init__(self, error_code: str = "", error_message: str = "", data: List[Dict] = None):
        """
        The results returned from low-level CmsApiAdapter
        :param error_code: code for error, if any
        :param error_message: descriptive error message or blank
        :param data: List of Dictionaries
        """
        self.error_code = error_code
        self.error_message = error_message
        self.data = data if data else []


class CmsApiError(Exception):
    pass


class WebServiceResponse:
    def __init__(self, result: ApiResult):
        self.error_code = result.error_code
        self.error_message = result.error_message
        self.has_error = self.error_code != ""
        if self.has_error:
            raise CmsApiError(f"{self.error_code}: {self.error_message}")


# Internal class
class ResponseStatus:
    """
    The ResponseStatus class is returned with all CMS API responses. It contains the result
    of the request. An empty error_code indicates success. Used internally.
    """

    def __init__(self, data: Dict):
        self.api_error_code = data["ErrorCode"] if data else ''
        self.api_error_message = data["Message"] if data else ''


class CmsApiAdapter:

    def __init__(self, api_key: str, hostname: str = 'api.winlink.org', logger: logging.Logger = None):
        """
        Constructor for RestAdapter
        :param api_key: Web service access key
        :param hostname: Normally, api.winlink.org
        :param logger: (optional)
        """

        self.api_key = api_key
        self.url = f"https://{hostname}/"
        self._logger = logger or logging.getLogger(__name__)

    async def _do(self, http_method: str, endpoint: str, ep_params: Dict = None, data: Dict = None) -> ApiResult:
        """
        Private method for get(), post(), etc. methods
        :param http_method: GET, POST, DELETE, etc.
        :param endpoint: URL Endpoint as a string
        :param ep_params: Dictionary of Endpoint parameters (Optional)
        :param data: Dictionary of data to pass to TheCatApi (Optional)
        :return: a Result object
        """
        full_url = self.url + endpoint
        # Create dictionary for params if not supplied.
        if ep_params is None:
            ep_params = {}
        ep_params["key"] = self.api_key
        ep_params["format"] = "json"
        log_line_pre = f"method={http_method}, url={full_url}, params={ep_params}"

        # Log HTTP params and perform an HTTP request, catching and re-raising any exceptions.
        try:
            self._logger.debug(msg=log_line_pre)

            async with httpx.AsyncClient(verify=False) as client:
                response = await client.request(method=http_method, url=full_url, params=ep_params, json=data)

        except httpx.RequestError as e:
            self._logger.error(msg=(str(e)))
            raise Exception("Request failed") from e

        is_success = 299 >= response.status_code >= 200  # 200 to 299 is OK
        log_line = ', '.join((log_line_pre, f"success={is_success}, status_code={response.status_code}"))

        # If status_code in 200-299 range, return API result status and data, otherwise raise exception
        if is_success:
            # Get JSON result, or return failed result on exception.
            try:
                data_out = response.json()
            except (ValueError, JSONDecodeError) as e:
                log_line = ', '.join((log_line_pre, f"success={False}, status_code={None}, message={e}"))
                self._logger.error(msg=log_line)
                raise Exception("Bad JSON in response") from e

            # Unpack response status returned from API call.
            response_status = ResponseStatus(data_out["ResponseStatus"])
            # Remove response status from data list -- data_out will just be the requested information.
            del data_out["ResponseStatus"]

            return ApiResult(response_status.api_error_code, response_status.api_error_message, data=data_out)
        elif response.status_code == 400:
            """
            API validation error - extract the response status object
            """
            jo = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            # Return validation error status
            return ApiResult(jo.ResponseStatus.ErrorCode, jo.ResponseStatus.Message)

        # Try to find the expanded HTTP error text.
        try:
            reason = HTTPStatus(response.status_code).phrase
        except ValueError:
            reason = f"Unknown HTTP status code: {response.status_code}"

        # Some other error - log it
        self._logger.error(msg=log_line)
        raise Exception(str(response.status_code), reason)

    async def get(self, endpoint: str, params: Dict = None) -> ApiResult:
        """
        Make an HTTP GET request
        """
        return await self._do(http_method='GET', endpoint=endpoint, ep_params=params)

    async def post(self, endpoint: str, params: Dict = None, data: Dict = None) -> ApiResult:
        """
        Make an HTTP POST request
        """
        return await self._do(http_method='POST', endpoint=endpoint, ep_params=params, data=data)

    # Could also do PUT and DELETE, but the CMS API doesn't support those HTTP verbs
