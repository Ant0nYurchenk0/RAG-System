import re
import sqlite3
import os
from Embeddings import EmbeddingsGenerator as eg

ARTICLE_DIR_NAME = "articles"
IMAGE_DIR_NAME = "images"
DB_PATH = "batch_articles.db"

EXCLUDE_TITLES = {
    "a_message_fromdeeplearningai",
    "subscribe_to_the_batch",
    "ai_courses_and_specializations",
    "stay_up_to_date_on_the_latest_news_courses_and_ai_events",
}


def safe_filename(title):
    cleaned = re.sub(r"\W+", "", title.replace(" ", "_").lower())
    return cleaned


def save_sections_to_files(sections, articles_path, images_path):
    for title, images, content, _ in sections[1:]:  # Skip the main "News" heading
        filename_base = safe_filename(title)
        if filename_base in EXCLUDE_TITLES:
            continue

        article_file = os.path.join(articles_path, f"{filename_base}.txt")
        with open(article_file, "w", encoding="utf-8") as f:
            f.write(title + "\n\n" + "\n".join(content))

        if images:
            image_file = os.path.join(images_path, f"{filename_base}.txt")
            with open(image_file, "w", encoding="utf-8") as f:
                f.write("\n".join(images))


def ensure_directories(base_path):
    articles_path = os.path.join(base_path, ARTICLE_DIR_NAME)
    images_path = os.path.join(base_path, IMAGE_DIR_NAME)
    os.makedirs(articles_path, exist_ok=True)
    os.makedirs(images_path, exist_ok=True)
    return articles_path, images_path


def save_sections_to_db(sections, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            url TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,            
            summary TEXT
        );
        """
    )
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM images")

    text_data = [
        (title, " ".join(content), url)
        for title, _, content, url in sections[1:]
        if safe_filename(title) not in EXCLUDE_TITLES
    ]
    cursor.executemany(
        "INSERT INTO articles (title, content, url) VALUES (?, ?, ?)", text_data
    )
    image_data = [
        (
            images[0],
            eg.get_image_summary(images[0], " .".join([title, " ".join(content)])),
        )
        for title, images, content, _ in sections[1:]
        if safe_filename(title) not in EXCLUDE_TITLES and images
    ]
    cursor.executemany("INSERT INTO images (url, summary) VALUES (?, ?)", image_data)

    conn.commit()
    conn.close()
