import streamlit.components.v1 as components
from bs4 import BeautifulSoup
import streamlit as st
import requests
import string
import random


URL_PREFIX = "https://archive.ph/"
TITLE = "Judit's iArchive"


@st.cache_data
def cache_request(url: str) -> bytes:
    """Avoid pinging the same url each time the dashboard is re-run."""
    agent = "".join(random.choices(string.ascii_letters, k=7))
    page = requests.get(url, headers={"User-agent": agent})
    return page.content


if __name__ == "__main__":
    st.set_page_config(
        page_icon=":mag:",
        page_title=TITLE,
        layout="centered"
    )
    st.title(TITLE)
    link = st.text_input("Webpage to lookup", placeholder="Add link here...")
    if len(link) == 0:
        st.stop()

    archive_url = URL_PREFIX + link
    r = cache_request(archive_url)

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
