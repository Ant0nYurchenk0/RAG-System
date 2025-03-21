import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from Data.DataSaver import save_sections_to_db, ensure_directories


BASE_URL = "https://www.deeplearning.ai/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_article_links():
    links = []
    page = 1

    while True:
        url = f"{BASE_URL}the-batch/page/{page}/"
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")

        articles = soup.find_all("article", {"data-sentry-component": "PostCard"})
        if not articles:
            break

        for article in articles:
            a_tags = article.find_all("a")
            if a_tags:

                links.append(a_tags[-1].get("href"))

        page += 1

    return links


def parse_article_sections(html, full_url):
    soup = BeautifulSoup(html, "html.parser")
    sections = []

    current_title = None
    current_content = []
    current_images = []
    next_images = []

    for tag in soup.find_all(["figure", "h1", "h2", "p", "ul", "ol"]):
        if tag.name == "figure":
            img = tag.find("img")
            if img and not tag.find("a"):
                src = img.get("src")
                if src and not src.endswith(".gif"):
                    next_images.append(src)

        elif tag.name in ("h1", "h2"):
            if current_title and current_content:
                sections.append(
                    (current_title, current_images, current_content, full_url)
                )

            current_title = tag.get_text(strip=True)
            current_images = next_images
            next_images = []
            current_content = []

        else:
            current_content.append(tag.get_text(strip=True))

    if current_title and current_content:
        sections.append((current_title, current_images, current_content, full_url))

    return sections
