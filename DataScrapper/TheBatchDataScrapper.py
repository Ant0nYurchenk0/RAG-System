import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import re
import time


BASE_URL = "https://www.deeplearning.ai/"

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_article_links():
    articles_urls = []
    counter = 1

    response = requests.get(f"{BASE_URL}the-batch/")
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("article", {"data-sentry-component": "PostCard"})
    while len(articles) > 0:
        for article in articles:
            article_links = article.find_all("a")
            article_url = article_links[-1].attrs["href"]
            articles_urls.append(article_url)
        counter += 1
        response = requests.get(f"{BASE_URL}the-batch/page/{counter}/")
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("article", {"data-sentry-component": "PostCard"})
    return articles_urls


def split_articles(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    sections = []
    current_title = None
    current_content = []
    current_images = []
    next_images = []

    for tag in soup.find_all(["figure", "h1", "h2", "p", "ul", "ol"]):
        if tag.name == "figure":
            img = tag.find("img")

            if img and not tag.find("a"):  # Skip if inside <a>
                img_url = img.get("src")
                if img_url:
                    next_images.append(img_url)

        elif tag.name == "h1" or tag.name == "h2":
            if current_title and len(current_content) > 0:  # Save the previous section
                sections.append((current_title, current_images, current_content))
            current_title = tag.get_text(strip=True)
            current_images = next_images
            next_images = []
            current_content = []  # Start a new section
        else:
            current_content.append(tag.get_text(strip=True))

    if current_title and len(current_content) > 0:
        sections.append((current_title, current_images, current_content))

    return sections


def write_to_file(sections):
    article_output_dir = os.path.join(os.path.dirname(__file__), "articles")
    images_output_dir = os.path.join(os.path.dirname(__file__), "images")

    for idx, (title, images, content) in enumerate(sections[1:], start=1):
        file_title = re.sub(r"\W+", "", title.replace(" ", "_").lower())
        if (
            file_title == "a_message_fromdeeplearningai"
            or file_title == "subscribe_to_the_batch"
        ):
            continue
        filename = os.path.join(article_output_dir, f"{file_title}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(title + "\n\n" + "\n".join(content))

        if images:
            image_filename = os.path.join(images_output_dir, f"{file_title}.txt")
            with open(image_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(images))


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    articles_dir = os.path.join(base_dir, "articles")
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(articles_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    article_links = get_article_links()
    for article_link in article_links:
        print(article_link)
        response = requests.get(urljoin(BASE_URL, article_link), headers=HEADERS)
        response.content
        article_sections = split_articles(response.content)
        write_to_file(article_sections)


if __name__ == "__main__":
    main()
