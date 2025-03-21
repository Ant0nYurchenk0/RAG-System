# Multimodal RAG System for News Retrieval from The Batch

This project implements a **Multimodal Retrieval-Augmented Generation (RAG)** system that retrieves relevant articles from [The Batch](https://www.deeplearning.ai/the-batch/), incorporating both **textual** and **visual data**. Users can input queries to search for news, and the system retrieves related articles along with associated images using a hybrid vector-based retrieval mechanism and language generation models.

---

## Features

- **Multimodal Search**: Retrieves relevant articles using both text and image embeddings.
- **Retrieval-Augmented Generation**: Uses retrieved content to generate contextual, query-aware responses.
- **Image & Text Linking**: Articles are paired with images and descriptions.
- **Embeddings with FAISS**: Fast vector search for text and images. It uses LLM that generates summaries for images based on images itself as well as the article it was used in
- **Relational DB + Vector DB**: SQLite for data storage, FAISS for similarity search.

---

## Architecture

            +---------------------------+
            |       User Query          |
            +------------+--------------+
                         |
          +--------------v---------------+
          |     Text & Image Embedding   |
          +--------------+---------------+
                         |
         +--------------v----------------+
         |  Vector DB (FAISS) Retrieval  |
         +-------+------------+----------+
                 |            |
    +------------v-----+  +---v---------------+
    | Top Text Matches |  | Top Image Matches |
    +--------+---------+  +--------+----------+
             |                     |
     +-------v---------------------v------+
     |     Fetch full records from DB     |
     +-------------+----------------------+
                   |
           +-------v--------+
           |    LLM (RAG)   |
           +-------+--------+
                   |
           +-------v---------+
           |  Final Response |
           +-----------------+


---

## Install Dependencies
For this project I use a range of dependencies that are stored in the ```requirements.txt``` file
```bash
pip install -r requirements.txt

```

You will also need an OpenAI API key. Create an "openai_key.txt" file, put a key in there and save the file to project root directory.

---

## Run The App
Each module is contained within it's corresponding folder and should be launched separately. For this use 
```bash
python -m <module-name>
```
The list of modules:
- ```Data.collect_data```
- ```Embeddings.generate_embeddings```
- ```RAG.respond_to_query```
- ```UI.web_app```

**Important: these scripts should be run as modules from the root folder of the project**

---

## The Flow
The complete flow of the apllication is as follows:
1. First, we need to scrape data from the Deeplearning.AI website. For this run the ```Data.collect_data``` script. It collects data from articles on the website, extracts exact topics and images, and stores it in an SQLite database/
2. Then, we want to create a FAISS indexes for embedding vector search. For this launch the ```Embeddings.generate_embeddings``` script

The files generated in the first two steps are crucial for application to work. If you do not want to generate them yourself (as it is a lengthy process) you can download them from this [google drive folder](https://drive.google.com/drive/folders/1UUKSq_tJT2R5oYm9KZ7jjiauTQL19aND?usp=sharing). Put these files into the root folder.

3. Run the ```UI.web_app``` script to start a demo web application.


