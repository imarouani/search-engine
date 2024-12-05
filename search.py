from flask import Flask, request, render_template
from crwl import crawl, search

app = Flask(__name__)

# Ensure the index is built
print("Starting crawl...")
crawl()
print("Crawling completed!")

@app.route("/")
def home():
    """Home page with a search form."""
    return render_template("index.html")

@app.route("/search")
def search_page():
    """Process the search query and return results."""
    query = request.args.get("q", "").strip()  # Get the query parameter from the URL
    if not query:
        return render_template("index.html", error="Please enter a search query.")

    results = search(query)  # Use the search function from crawler.py
    return render_template("results.html", query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True)
