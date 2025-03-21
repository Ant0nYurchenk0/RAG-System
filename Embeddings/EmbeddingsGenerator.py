from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from openai import OpenAI

API_KEY_PATH = "openai_key.txt"


def _read_api_key(filepath):
    with open(filepath, "r") as file:
        return file.read().strip()


def save_embeddingds(texts, ids, path):

    model = SentenceTransformer("all-MiniLM-L6-v2")

    embeddings = model.encode(texts, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index_with_ids = faiss.IndexIDMap(index)

    embedding_ids = np.array(ids).astype("int64")
    index_with_ids.add_with_ids(embeddings, embedding_ids)

    faiss.write_index(index_with_ids, path)


def get_image_summary(url, context):
    api_key = _read_api_key(API_KEY_PATH)

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
                        "text": "You are a data annotator, who generates short one-sentence summaries of images based on the context they appear in for later being used in vector search, so it is important to capture the core meaning of the picture",
                    },
                    {
                        "type": "text",
                        "text": f"What is depicted on this image given it was in this article:{context}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url,
                        },
                    },
                ],
            }
        ],
    )

    return completion.choices[0].message.content
