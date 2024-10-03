from requests.exceptions import ProxyError
from bs4 import BeautifulSoup, Tag
from typing import Optional
import requests
import random


PROXY_RESOURCE = "https://free-proxy-list.net/"
USER_AGENTS = [
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]


class Proxy:

    def __init__(self, headers: list[str], data: list[Tag]) -> None:
        data = [d.text for d in data]
        self.dct = dict(zip(headers, data))
        self.ip_address = self.dct["IP Address"]
        self.port = str(self.dct["Port"])
        self.code = self.dct["Code"]
        self.country = self.dct["Country"]
        self.anonymity = self.dct["Anonymity"]
        self.google = self.dct["Google"] == "yes"
        self.https = self.dct["Https"] == "yes"

        self.protocol = "https" if self.https else "http"
        self.proxy = f"{self.protocol}://{self.ip_address}:{self.port}"
        self.proxies = {self.protocol: self.proxy}

        self.agent = USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)]

    def request(self, url: str) -> str:
        page = requests.get(url, proxies=self.proxies, headers={"User-agent": self.agent})
        if not page.ok:
            raise ProxyError(f"Status code: {page.status_code}. {page.reason}")
        return page.text


class ProxyRequest:
    """
    proxy request is to change the location our query is made from
    it randomly chooses a proxy each time it is called
    best to initiate once for target market then call query_request_text_from_url for each individual query
    """
    def __init__(self) -> None:
        self.proxies = self.query_proxies()

    @staticmethod
    def query_proxies() -> list[Proxy]:
        """
        :return: dataframe of proxies available for particular market
        """
        text = requests.get(PROXY_RESOURCE).content
        soup = BeautifulSoup(text, "html.parser")
        table = soup.find("table")
        headers = [th.text for th in soup.find_all("th")]

        body = table.find("tbody")
        rows = body.find_all("tr")
        return [Proxy(headers, r.find_all("td")) for r in rows]

    def remove_proxy(self, proxy: Proxy) -> None:
        self.proxies = [p for p in self.proxies if p.ip_address != proxy.ip_address]

    def choose_proxy(self) -> Proxy:
        """
        :return: chooses a random proxy from available proxies
        """
        index = random.randint(0, len(self.proxies) - 1)
        return self.proxies[index]

    def request(self, request_url: str) -> tuple[Optional[str], Optional[str]]:
        if len(self.proxies) == 0:
            raise ValueError("There are no proxies to try")
        proxy = self.choose_proxy()
        print(proxy.dct)
        try:
            return proxy.request(request_url), None
        except ProxyError as e:
            print(e)
            self.remove_proxy(proxy)
            return None, str(e)
