from requests.exceptions import ProxyError
from bs4 import BeautifulSoup, Tag
import requests
import random
import string
import time


SLEEP_SECONDS = 1
PROXY_RESOURCE = "https://free-proxy-list.net/"


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

        self.protocol = "https" if self.https else "http"
        self.proxy = self.ip_address + ":" + self.port
        self.proxies = {self.protocol: self.proxy}
        self.agent = "".join(random.choices(string.ascii_letters, k=7))

    def request(self, url: str) -> bytes:
        page = requests.get(url, headers={"User-agent": self.agent}, proxies=self.proxies)
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
        try:
            return proxy.request(request_url)
        except ProxyError:
            self.remove_proxy(proxy)
            time.sleep(SLEEP_SECONDS)
            return self.request(request_url)
