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
    # faiss.normalize_L2(text_embedding)
    k = 3

    text_distances, text_ids = text_index.search(text_embedding, k)
    # if text_distances[0][0] > 1.5:
    #     return None, None

    image_distances, image_ids = image_index.search(text_embedding, k)
    # if image_distances[0][0] > 1.5:
    #     return text_distances, None

    return text_ids[0], image_ids[0]


def respond_to_query(query, text_ids):
    if text_ids is None:
        return "Sorry, I couldn't find any relevant articles"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    joined_ids = ",".join([str(id) for id in text_ids])
    sql = f"SELECT content FROM articles WHERE id IN ({joined_ids})"
    articles = cursor.execute(sql).fetchall()

    joined_articles = "\n--------\n".join([article[0] for article in articles])
    api_key = read_api_key(API_KEY_PATH)

    client = OpenAI(
        api_key=api_key,
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are being used in a RAG system that retrieves an answer to a query based solely on the relevant articles provided",
                    },
                    {
                        "type": "text",
                        "text": f"The relevant articles are: {joined_articles}",
                    },
                    {
                        "type": "text",
                        "text": f"The user asks for an answer to the query: {query}",
                    },
                ],
            }
        ],
    )
    return completion.choices[0].message.content
