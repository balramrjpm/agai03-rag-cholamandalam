import os
import json
import time
import requests

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

BASE_URL = os.getenv(
    "BASE_URL",
    "https://www.cholamandalam.com/"
)

SAVE_DIR = os.getenv(
    "RAW_DIR",
    "data/raw"
)

MAX_DEPTH = int(
    os.getenv("MAX_DEPTH", 3)
)

REQUEST_DELAY = int(
    os.getenv("REQUEST_DELAY", 1)
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", 3)
)

REQUEST_TIMEOUT = int(
    os.getenv("REQUEST_TIMEOUT", 15)
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

visited = set()

os.makedirs(SAVE_DIR, exist_ok=True)

# ============================================================
# ALLOWED PATHS
# ============================================================

ALLOWED_PATHS = [
    "/about-us",
    "/products",
    "/get",
    "/gold-loan",
    "/contact-us",
]

# ============================================================
# BLOCKED FILE TYPES
# ============================================================

BLOCKED_EXTENSIONS = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".svg",
    ".gif",
    ".zip",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
)

# ============================================================
# CLEAN TEXT
# ============================================================


def clean_text(text):

    return " ".join(text.split())

# ============================================================
# EXTRACT TEXT
# ============================================================


def extract_text(soup):

    for tag in soup([
        "script",
        "style",
        "noscript",
        "footer",
        "nav",
        "header",
    ]):
        tag.decompose()

    return clean_text(
        soup.get_text(separator=" ")
    )

# ============================================================
# SAVE PAGE
# ============================================================


def save_page(url, title, content):

    filename = urlparse(url).path.replace("/", "_")

    filename = filename.strip("_")

    # Handle home page
    if filename == "":
        filename = "home"

    path = os.path.join(
        SAVE_DIR,
        f"{filename}.json"
    )

    data = {
        "url": url,
        "title": title,
        "content": content,
    }

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
        )

    print(f"Saved: {filename}.json")

# ============================================================
# VALID URL CHECK
# ============================================================


def is_valid_url(full_url):

    parsed = urlparse(full_url)

    parsed_path = parsed.path.lower()

    # Skip external domains
    if parsed.netloc != urlparse(BASE_URL).netloc:
        return False

    # Skip blocked file types
    if parsed_path.endswith(BLOCKED_EXTENSIONS):
        return False

    # Restrict allowed paths
    if any(
        parsed_path.startswith(path)
        for path in ALLOWED_PATHS
    ):
        return True

    return False

# ============================================================
# GET SEED URLS
# ============================================================


def get_seed_urls():

    return [

        # HOME
        BASE_URL,

        # ABOUT
        urljoin(
            BASE_URL,
            "/about-us"
        ),

        # CONTACT
        urljoin(
            BASE_URL,
            "/contact-us"
        ),

        # PRODUCTS
        urljoin(
            BASE_URL,
            "/products"
        ),

        urljoin(
            BASE_URL,
            "/products/vehicle-finance"
        ),

        # GET PAGES
        urljoin(
            BASE_URL,
            "/get-consumer-small-enterprise-loans"
        ),

        urljoin(
            BASE_URL,
            "/get-home-loans"
        ),

        urljoin(
            BASE_URL,
            "/get-sme-loans"
        ),

        urljoin(
            BASE_URL,
            "/get-loan-against-property"
        ),

        urljoin(
            BASE_URL,
            "/get-two-wheeler-loans"
        ),

        urljoin(
            BASE_URL,
            "/get-tractor-loans"
        ),

        urljoin(
            BASE_URL,
            "/get-three-wheeler-loans"
        ),

        urljoin(
            BASE_URL,
            "/get-construction-equipment-loans"
        ),

        urljoin(
            BASE_URL,
            "/get-secured-term-loan"
        ),

        urljoin(
            BASE_URL,
            "/get-secured-business-loans"
        ),

        # GOLD LOAN
        urljoin(
            BASE_URL,
            "/gold-loan"
        ),
    ]

# ============================================================
# CRAWLER WITH RETRY
# ============================================================


def crawl(url, depth=0):

    # Stop recursion
    if depth > MAX_DEPTH:
        return

    parsed = urlparse(url)

    clean_url = (
        parsed.scheme
        + "://"
        + parsed.netloc
        + parsed.path
    )

    # Skip duplicates
    if clean_url in visited:
        return

    retry_count = 0

    while retry_count < MAX_RETRIES:

        try:

            print(
                f"Scraping: {clean_url} "
                f"(Attempt {retry_count + 1})"
            )

            response = requests.get(
                clean_url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )

            # =================================================
            # SUCCESS
            # =================================================

            if response.status_code == 200:

                visited.add(clean_url)

                soup = BeautifulSoup(
                    response.text,
                    "lxml"
                )

                title = (
                    soup.title.text.strip()
                    if soup.title
                    else "No Title"
                )

                content = extract_text(soup)

                # Skip tiny pages
                if len(content) < 100:

                    print(
                        f"Skipped Empty Page: {clean_url}"
                    )

                    return

                save_page(
                    clean_url,
                    title,
                    content,
                )

                # =============================================
                # FIND LINKS
                # =============================================

                links = soup.find_all(
                    "a",
                    href=True
                )

                for link in links:

                    href = link["href"]

                    full_url = urljoin(
                        BASE_URL,
                        href
                    )

                    parsed_link = urlparse(full_url)

                    normalized_url = (
                        parsed_link.scheme
                        + "://"
                        + parsed_link.netloc
                        + parsed_link.path
                    )

                    if is_valid_url(normalized_url):

                        crawl(
                            normalized_url,
                            depth + 1
                        )

                # Respect server
                time.sleep(REQUEST_DELAY)

                return

            # =================================================
            # RETRYABLE STATUS CODES
            # =================================================

            elif response.status_code in [
                429,
                500,
                502,
                503,
                504,
            ]:

                retry_count += 1

                wait_time = retry_count * 2

                print(
                    f"Retrying: {clean_url} "
                    f"| Status: {response.status_code} "
                    f"| Waiting {wait_time}s"
                )

                time.sleep(wait_time)

            # =================================================
            # NON RETRYABLE
            # =================================================

            else:

                print(
                    f"Failed: {clean_url} "
                    f"| Status: {response.status_code}"
                )

                return

        # =====================================================
        # TIMEOUT
        # =====================================================

        except requests.exceptions.Timeout:

            retry_count += 1

            wait_time = retry_count * 2

            print(
                f"Timeout: {clean_url} "
                f"| Retry {retry_count}/{MAX_RETRIES}"
            )

            time.sleep(wait_time)

        # =====================================================
        # CONNECTION ERROR
        # =====================================================

        except requests.exceptions.ConnectionError:

            retry_count += 1

            wait_time = retry_count * 2

            print(
                f"Connection Error: {clean_url} "
                f"| Retry {retry_count}/{MAX_RETRIES}"
            )

            time.sleep(wait_time)

        # =====================================================
        # OTHER ERRORS
        # =====================================================

        except Exception as e:

            print(f"Error scraping: {clean_url}")
            print(e)

            return

    # =========================================================
    # MAX RETRIES FAILED
    # =========================================================

    print(
        f"Max retries exceeded: {clean_url}"
    )

# ============================================================
# MAIN
# ============================================================


if __name__ == "__main__":

    print("=" * 60)
    print("STARTING CHOLAMANDALAM SCRAPER")
    print("=" * 60)

    # ========================================================
    # LOAD SEED URLS
    # ========================================================

    start_urls = get_seed_urls()

    print(f"Total Seed URLs: {len(start_urls)}")

    # ========================================================
    # START CRAWLING
    # ========================================================

    for start_url in start_urls:

        crawl(start_url)

    print("\n" + "=" * 60)
    print("SCRAPING COMPLETED")
    print(f"Total Pages Scraped: {len(visited)}")
    print("=" * 60)
