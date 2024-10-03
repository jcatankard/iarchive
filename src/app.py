import streamlit.components.v1 as components
from proxy_request import ProxyRequest
from bs4 import BeautifulSoup
from typing import Optional
import streamlit as st
import time


SLEEP_SECONDS = 3
URL_PREFIX = "https://archive.ph/"
TITLE = "Judit's iArchive"
MAX_RETRIES = 5


@st.cache_data
def fetch_page(url: str) -> Optional[str]:
    """Caching to avoid pinging the same url each time the dashboard is re-run."""
    pr = ProxyRequest()
    count = 0
    while count < MAX_RETRIES:
        response, error = pr.request(url)
        if error is None:
            st.success("Success")
            return response
        else:
            st.warning(f"Retrying with new proxy in {SLEEP_SECONDS} seconds: {count + 1}.")
            time.sleep(SLEEP_SECONDS)
            count += 1
    st.warning("Max retries made. Try a new URL.")
    return None


if __name__ == "__main__":
    st.set_page_config(page_icon=":mag:", page_title=TITLE, layout="centered")
    st.title(TITLE)

    link = st.text_input("Webpage to lookup", placeholder="Add link here...")
    if len(link) == 0:
        st.stop()

    archive_url = URL_PREFIX + link
    r = fetch_page(archive_url)
    if r is None:
        st.stop()

    soup = BeautifulSoup(r, "html.parser")
    block = soup.find("div", class_="THUMBS-BLOCK")
    if block is None:
        st.warning("Your search returned no results.")
        st.stop()

    search = block.find_all("a")
    results = {s.find_all("div")[-1].text: s.get("href") for s in search}

    date = st.selectbox("Select datetime", options=results.keys(), index=len(results) - 1)
    st.link_button("Open page in new tab", results[date], type="primary")

    components.iframe(results[date], scrolling=True, height=1500)
