import sqlite3
import faiss
from flask import Flask, redirect, render_template_string, request, session, url_for
from Data.DataSaver import DB_PATH
from Embeddings.EmbeddingsGenerator import IMAGE_INDEX_PATH, TEXT_INDEX_PATH
from RAG.ResponseGenerator import get_context, respond_to_query

app = Flask(__name__)
app.secret_key = "supersecret"
text_index = faiss.read_index(TEXT_INDEX_PATH)
image_index = faiss.read_index(IMAGE_INDEX_PATH)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Query Processor with Articles and Images</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h3 class="card-title text-center mb-4">RAG with Deeplearning.AI's The Batch and ChatGPT</h3>
                    <form method="POST" onsubmit="showSpinner()">
                        <div class="mb-3">
                            <input type="text" name="user_query" class="form-control" placeholder="{%if user_query%}{{user_query}}{%else%}Enter your query...{%endif%}" required>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Submit</button>
                        </div>
                        <div class="text-center mt-3" id="spinner" style="display: none;">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2">Processing...</p>
                        </div>
                    </form>
                    {% if result %}
                        <hr>
                        <h5 class="mt-4">Processed Result:</h5>
                        <div class="alert alert-success">{{ result }}</div>
                    {% endif %}

                    {% if articles %}
                        <hr>
                        <h5>Related Articles</h5>
                        {% for article in articles %}
                            <h6>{{ article[0] }}</h6>
                            <p>{{ article[1] }}</p>
                            <a href="{{article[2]}}" class="btn btn-primary">Explore</a>
                        {% endfor %}
                    {% endif %}

                    {% if images %}
                        <hr>
                        <h5>Related Images</h5>
                        <div class="row">
                            {% for image in images %}
                                <div class="col-6 mb-3">
                                    <img src="{{ image[0] }}" class="img-fluid rounded shadow-sm" />
                                </div>
                            {% endfor %}
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    function showSpinner() {
        document.getElementById("spinner").style.display = "block";
    }
</script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    user_query = None
    response = None
    articles = None
    images = None

    if request.method == "POST":
        user_query = request.form["user_query"]
        text_ids, image_ids = get_context(user_query, text_index, image_index)
        response = respond_to_query(user_query, text_ids, image_ids)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        joined_article_ids = ",".join([str(id) for id in text_ids])
        sql_article = f"SELECT title, content, url FROM articles WHERE id IN ({joined_article_ids})"
        articles = cursor.execute(sql_article).fetchall()

        joined_image_ids = ",".join([str(id) for id in image_ids])
        sql_images = f"SELECT url FROM images WHERE id IN ({joined_image_ids})"
        images = cursor.execute(sql_images).fetchall()

    return render_template_string(
        HTML, result=response, articles=articles, images=images, user_query=user_query
    )


if __name__ == "__main__":
    app.run(debug=True)
