import sqlite3
from Data.DataSaver import DB_PATH
from Embeddings.EmbeddingsGenerator import (
    IMAGE_IDEX_PATH,
    TEXT_INDEX_PATH,
    save_embeddingds,
)


def main():
    image_path = IMAGE_IDEX_PATH
    text_path = TEXT_INDEX_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    texts = cursor.execute("SELECT id, content FROM articles").fetchall()
    images = cursor.execute("SELECT id, summary FROM images").fetchall()

    save_embeddingds(
        [text[1] for text in texts], [text[0] for text in texts], text_path
    )
    save_embeddingds(
        [image[1] for image in images], [image[0] for image in images], image_path
    )


if __name__ == "__main__":
    main()
