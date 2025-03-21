import faiss
from Embeddings.EmbeddingsGenerator import IMAGE_INDEX_PATH, TEXT_INDEX_PATH
from RAG.ResponseGenerator import get_context, respond_to_query


def main():
    text_index = faiss.read_index(TEXT_INDEX_PATH)
    image_index = faiss.read_index(IMAGE_INDEX_PATH)
    query = "What advancements did Google make in AI"
    text_ids, image_ids = get_context(query, text_index, image_index)
    response = respond_to_query(query, text_ids)
    print(response)
    print("Articles: ", text_ids)
    print("Images: ", image_ids)


if __name__ == "__main__":
    main()
