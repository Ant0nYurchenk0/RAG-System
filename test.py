from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# 1. Load text embedding model
model = SentenceTransformer("paraphrase-mpnet-base-v2")

# 2. Define two texts
text1 = "The illustration details the architecture of Aya Vision, a multilingual vision-language model, outlining its components such as the vision encoder and the vision-text connector, along with the multimodal merging process for integrating text and image inputs."
text2 = "multilingual ai models"

# 3. Encode texts to vectors
embedding1 = model.encode([text1], convert_to_numpy=True)
faiss.normalize_L2(embedding1)

embedding2 = model.encode([text2], convert_to_numpy=True)
faiss.normalize_L2(embedding2)

# 4. Create a FAISS index
dimension = embedding1.shape[1]
index = faiss.IndexFlatL2(dimension)  # L2 (Euclidean) distance

# 5. Add one embedding to the index
index.add(embedding1)  # This becomes index 0

# 6. Search the distance from embedding2 to embedding1
distance, index_result = index.search(embedding2, 1)

# 7. Print results
# print(f"Text 1: {text1}")
# print(f"Text 2: {text2}")
print(f"FAISS L2 Distance: {distance[0][0]:.4f}")
