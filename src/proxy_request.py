from requests.exceptions import ProxyError, ConnectionError
from bs4 import BeautifulSoup, Tag
import requests
import random
import string
import time


SLEEP_SECONDS = 1
PROXY_RESOURCE = "https://free-proxy-list.net/"
TIMEOUT_SECONDS = 3
USER_AGENTS = [
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]


class Proxy:

    def __init__(self, headers: list[str], data: list[Tag]) -> None:
        data = [d.text for d in data]
        dct = dict(zip(headers, data))
        self.ip_address = dct["IP Address"]
        self.port = str(dct["Port"])
        self.code = dct["Code"]
        self.country = dct["Country"]
        self.anonymity = dct["Anonymity"]
        self.google = dct["Google"] == "yes"
        self.https = dct["Https"] == "yes"
        self.dict = dct

        self.protocol = "https" if self.https else "http"
        self.proxy = self.ip_address + ":" + self.port
        self.proxies = {self.protocol: self.proxy}
        self.agent = USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)]

    def request(self, url: str) -> bytes:
        try:
            page = requests.get(url, headers={"User-Agent": self.agent}, proxies=self.proxies, timeout=TIMEOUT_SECONDS)
            print(page.headers)
        except ConnectionError:
            raise ProxyError
        if page.status_code != 200:
            raise ProxyError(f"Status code: {page.status_code}")
        return page.content


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

    def request(self, request_url: str) -> bytes:
        if len(self.proxies) == 0:
            raise ValueError("There are no proxies to try")
        proxy = self.choose_proxy()
        print(proxy.dict)
        try:
            return proxy.request(request_url)
        except ProxyError:
            self.remove_proxy(proxy)
            time.sleep(SLEEP_SECONDS)
            return self.request(request_url)
