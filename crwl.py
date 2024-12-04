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
index = {}  # Dictionary to store word-to-URL mappings


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
    """Extract words from the page and update the index."""
    if soup is None:
        return

    # Extract text content
    text = soup.get_text(strip=True)
    words = re.findall(r'\w+', text.lower())  # Split text into words, convert to lowercase

    for word in words:
        if word not in index:
            index[word] = []
        if url not in index[word]:
            index[word].append(url)


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
    """Search the index for pages containing all query words."""
    words = query.lower().split()
    if not words:
        return []

    # Find URLs containing all words
    result = set(index.get(words[0], []))
    for word in words[1:]:
        result &= set(index.get(word, []))

    return list(result)


if __name__ == "__main__":
    # Start crawling
    print("Starting crawl...")
    crawl()
    print("Crawling completed!")

    # Display search results
    while True:
        query = input("Enter search query (or type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        results = search(query)
        print(f"Results for '{query}': {results}")
