from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)

# Définition des fichiers et des catégories
CATEGORIES = {
    "external.ExternalTexts": "badges",
    "external.BadgeTexts": "badges",
    "external.UITexts": "badges",
    "furnituredata": "furnis",
    "avatar.figuremap": "clothes",
    "avatar.effectmap": "effects"
}

BASE_DIR = "stock_retro"  # Modifier selon ton chemin de fichiers


def search_in_files(search_term):
    results = {}

    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            category = CATEGORIES.get(file, None)

            if category:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = re.findall(re.escape(search_term), content, re.IGNORECASE)

                    if matches:
                        if category not in results:
                            results[category] = []
                        results[category].append({"file": file_path, "matches": matches})

    return results


@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    search_term = ""

    if request.method == "POST":
        search_term = request.form["search"]
        results = search_in_files(search_term)

    return render_template("index.html", results=results, search_term=search_term)


if __name__ == "__main__":
    app.run(debug=True)
