import sqlite3
import faiss
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from Data.DataSaver import DB_PATH
from Embeddings.EmbeddingsGenerator import API_KEY_PATH, read_api_key


def get_context(query, text_index, image_index):
    assert text_index is not None and image_index is not None, "Indexes not loaded"

    text_model = SentenceTransformer("paraphrase-mpnet-base-v2")

    text_embedding = text_model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(text_embedding)
    k = 3

    text_distances, text_ids = text_index.search(text_embedding, k)
    texts = [id for id, dist in zip(text_ids[0], text_distances[0]) if dist <= 1.2]

    image_distances, image_ids = image_index.search(text_embedding, k)
    images = [id for id, dist in zip(image_ids[0], image_distances[0]) if dist <= 1.2]

    return texts, images


def respond_to_query(query, text_ids, image_ids):
    if text_ids is None or len(text_ids) == 0:
        return "Sorry, I couldn't find any relevant articles"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    joined_article_ids = ",".join([str(id) for id in text_ids])
    sql_article = f"SELECT content FROM articles WHERE id IN ({joined_article_ids})"
    articles = cursor.execute(sql_article).fetchall()
    joined_articles = "\n--------\n".join([article[0] for article in articles])

    joined_image_ids = ",".join([str(id) for id in image_ids])
    sql_images = f"SELECT url FROM images WHERE id IN ({joined_image_ids})"
    images = cursor.execute(sql_images).fetchall()

    api_key = read_api_key(API_KEY_PATH)
    image_obj = [
        {
            "type": "image_url",
            "image_url": {
                "url": image[0],
            },
        }
        for image in images
    ]

    content = [
        {
            "type": "text",
            "text": "You are being used in a RAG system that retrieves an answer to a query based solely on the relevant articles and images provided. Give only the answer that can be shown to the end user with no text formatting",
        },
        {
            "type": "text",
            "text": f"The relevant articles are: {joined_articles}",
        },
        {
            "type": "text",
            "text": f"The user asks for an answer to the query: {query}",
        },
    ]
    content.extend(image_obj)
    client = OpenAI(
        api_key=api_key,
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )
    return completion.choices[0].message.content
