import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# Base URL of the website to crawl
base_url = "https://vm009.rz.uos.de/crawl/index.html"
prefix = "https://vm009.rz.uos.de/crawl/"  # Only follow links within this domain

# Initialize structures
agenda = [base_url]  # Queue of URLs to visit
visited_urls = set()  # Keep track of visited URLs to avoid duplicates
index = {}  # Dictionary to store URL-to-content mappings


def fetch_page(url):
    """Fetch a page and return the BeautifulSoup object."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def index_page(url, soup):
    """Extract the full text content of a page and store it in the index."""
    if soup is None:
        return

    # Extract text content
    text = soup.get_text(separator=" ", strip=True)  # Get all text content as a single string
    index[url] = text  # Map the URL to its full text content


def is_valid_link(link):
    """Check if a link is valid and within the same domain."""
    return (
        link.startswith(prefix) and  # Internal links only
        not link.endswith(('.jpg', '.png', '.pdf', '.css', '.js'))  # Skip non-HTML files
    )


def crawl():
    """Crawl the website starting from the base URL."""
    while agenda:
        url = agenda.pop()
        if url in visited_urls:
            continue

        print(f"Fetching: {url}")
        visited_urls.add(url)

        # Fetch and parse the page
        soup = fetch_page(url)
        if soup is None:
            continue

        # Index the page content
        index_page(url, soup)

        # Find and queue new links
        for link_tag in soup.find_all('a', href=True):
            absolute_link = urljoin(url, link_tag['href'])
            if is_valid_link(absolute_link) and absolute_link not in visited_urls:
                agenda.append(absolute_link)


def search(query):
    """Search the index for pages containing any query words and identify missing words."""
    query = query.lower().strip()
    words = query.split()  # Split the query into individual words
    results = []

    for url, content in index.items():
        content_lower = content.lower()

        # Find matching and missing words
        matching_words = [word for word in words if word in content_lower]
        missing_words = [word for word in words if word not in content_lower]

        # Include the result if at least one word matches
        if matching_words:
            try:
                soup = fetch_page(url)
                title = soup.title.string.strip() if soup and soup.title else "No Title"
                results.append({
                    "url": url,
                    "title": title,
                    "missing_words": missing_words  # Include missing words in the result
                })
            except Exception as e:
                print(f"Error fetching title for {url}: {e}")
                results.append({
                    "url": url,
                    "title": "No Title",
                    "missing_words": missing_words
                })

    return results
