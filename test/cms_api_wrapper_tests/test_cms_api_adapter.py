from unittest import TestCase, mock
import os

from dotenv import load_dotenv

from src.cms_api_wrapper.cms_api_adapter import *

# TODO: Resolve test warnings and verify that tests are working properly


class TestCmsApiAdapter(TestCase):
    def setUp(self):
        load_dotenv()
        api_key = os.getenv("API_KEY")
        hostname = "cms-z.winlink.org"
        self.api_adapter = CmsApiAdapter(api_key, hostname)
        self.response = httpx.Response(200)

    def tearDown(self) -> None:
        pass

    async def test__do_good_request_returns_result(self):
        self.response.status_code = 200
        self.response._content = '{"ResponseStatus":{}}'.encode()
        with mock.patch("httpx.request", return_value=self.response):
            result = await self.api_adapter._do('GET', '')
            self.assertIsInstance(result, ApiResult)

    async def test__do_300_or_higher_raises_cns_api_exception(self):
        self.response.status_code = 300
        self.response._content = '{"ResponseStatus":{}}'.encode()
        with mock.patch("httpx.request", return_value=self.response):
            with self.assertRaises(Exception):
                await self.api_adapter._do('GET', '')

    async def test__do_199_or_lower_raises_cms_api_exception(self):
        self.response.status_code = 199
        self.response._content = '{"ResponseStatus":{}}'.encode()
        with mock.patch("httpx.request", return_value=self.response):
            with self.assertRaises(Exception):
                await self.api_adapter._do('GET', '')

    async def test__do_bad_json_raises_type_error_exception(self):
        bad_json = '{"some bad json": '
        self.response._content = bad_json
        with mock.patch("httpx.request", return_value=self.response):
            with self.assertRaises(TypeError):
                await self.api_adapter._do('GET', '')

    async def test_get_good_request_returns_result(self):
        self.response.status_code = 200
        self.response._content = '{"ResponseStatus":{}}'.encode()
        with mock.patch("httpx.request", return_value=self.response):
            result = await self.api_adapter.get("")
            self.assertIsInstance(result, ApiResult)

    async def test_post_good_request_returns_result(self):
        self.response.status_code = 200
        self.response._content = '{"ResponseStatus":{}}'.encode()
        with mock.patch("httpx.request", return_value=self.response):
            result = await self.api_adapter.post("fake/endpoint/")
            self.assertIsInstance(result, ApiResult)
