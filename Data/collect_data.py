import os
import time
import requests
from tqdm import tqdm
from urllib.parse import urljoin
from Data.TheBatchDataProcessor import (
    fetch_article_links,
    parse_article_sections,
    BASE_URL,
    HEADERS,
)
from Data.DataSaver import (
    save_sections_to_db,
    ensure_directories,
    save_sections_to_files,
)


def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    articles_path, images_path = ensure_directories(base_path)
    print("Fetching article links...")
    links = fetch_article_links()
    print("Storing data in database...")
    for url in tqdm(links):
        full_url = urljoin(BASE_URL, url)
        response = requests.get(full_url, headers=HEADERS)

        sections = parse_article_sections(response.content, full_url)
        save_sections_to_db(sections)
        save_sections_to_files(sections, articles_path, images_path)
        time.sleep(1)


if __name__ == "__main__":
    main()
