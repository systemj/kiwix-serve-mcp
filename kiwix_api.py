import logging
import requests
import xmltodict

logger = logging.getLogger()

class KiwixAPI():
    def __init__(self, kiwix_server: str) -> object:
        self.kiwix_server = kiwix_server

    def _api_request(self, method: str = "GET", path: str = "", params: dict = {}) -> str:
        url = f"{self.kiwix_server}{path}"
        try:
            response = requests.request(method=method, url=url, params=params)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error("request failed:", e)

    def list_books(self) -> dict:
        response = self._api_request(path = "/catalog/v2/entries")
        return xmltodict.parse(response)

    def search(self, uuid: str = "", pattern: str = "") -> dict:
        params = {
            "format": "xml",
            "books.uuid": uuid,
            "pattern": pattern
        }
        response = self._api_request(path="/search", params=params)
        return xmltodict.parse(response)

    def get_content(self, link: str = "") -> str:
        return self._api_request(path=link)
