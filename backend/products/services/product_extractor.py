import re
import socket
import logging
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}

REQUEST_TIMEOUT = 15
MAX_URL_LENGTH = 2048

BLOCKED_NETWORKS = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "127.0.0.0/8",
    "169.254.0.0/16",
    "::1/128",
    "fc00::/7",
]


def _is_private_ip(ip: str) -> bool:
    import ipaddress
    try:
        addr = ipaddress.ip_address(ip)
        for net in BLOCKED_NETWORKS:
            if addr in ipaddress.ip_network(net, strict=False):
                return True
    except ValueError:
        return True
    return False


def _validate_url_safety(url: str) -> str:
    if len(url) > MAX_URL_LENGTH:
        raise ValueError(f"URL exceeds maximum length of {MAX_URL_LENGTH} characters")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are supported")

    if "\x00" in url:
        raise ValueError("URL contains invalid characters")

    try:
        ip = socket.gethostbyname(parsed.hostname)
    except (socket.gaierror, TypeError):
        raise ValueError("Could not resolve hostname")

    if _is_private_ip(ip):
        raise ValueError("URL resolves to a private/internal network address")

    return ip


class ExtractionError(Exception):
    pass


class ProductExtractor:
    """Extracts product information from e-commerce URLs using HTTP requests and HTML parsing."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def extract(self, url: str, platform: str) -> dict:
        try:
            _validate_url_safety(url)
        except ValueError as e:
            raise ExtractionError(str(e))

        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=False)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise ExtractionError("Request timed out. The website may be slow or blocking automated access.")
        except requests.exceptions.ConnectionError:
            raise ExtractionError("Could not connect to the website. Please check the URL and try again.")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            if status == 403:
                raise ExtractionError("Access denied. The website may be blocking automated requests.")
            elif status == 404:
                raise ExtractionError("Product page not found. The URL may be invalid or the product may have been removed.")
            elif status == 503:
                raise ExtractionError("Service temporarily unavailable. Please try again later.")
            raise ExtractionError(f"HTTP error {status} while fetching the page.")

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        extractors = {
            "Amazon": self._extract_amazon,
            "Flipkart": self._extract_flipkart,
            "Myntra": self._extract_myntra,
            "AJIO": self._extract_ajio,
            "Meesho": self._extract_meesho,
            "Croma": self._extract_croma,
            "Reliance Digital": self._extract_reliance,
            "Tata CLiQ": self._extract_tatacliq,
        }

        extractor_fn = extractors.get(platform)
        if not extractor_fn:
            raise ExtractionError(f"Extraction not implemented for {platform}.")

        try:
            result = extractor_fn(soup, url)
        except ExtractionError:
            raise
        except Exception as e:
            logger.exception("Extraction failed for %s: %s", url, e)
            raise ExtractionError(f"Could not extract product information from this page.")

        if not result.get("title") and not result.get("price"):
            raise ExtractionError(
                "Product information could not be extracted from this page. "
                "Please try another supported product URL."
            )

        result["source_url"] = url
        result["platform"] = platform
        return result

    def _extract_amazon(self, soup: BeautifulSoup, url: str) -> dict:
        data = {}
        title_el = soup.select_one("#productTitle")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        price_el = soup.select_one(".a-price .a-offscreen") or soup.select_one("#priceblock_ourprice") or soup.select_one("#priceblock_dealprice")
        if price_el:
            data["price"] = self._parse_price(price_el.get_text(strip=True))

        mrp_el = soup.select_one(".a-price.a-text-price .a-offscreen") or soup.select_one("#priceblock_listprice")
        if mrp_el:
            data["mrp"] = self._parse_price(mrp_el.get_text(strip=True))

        rating_el = soup.select_one("#acrPopover .a-icon-alt") or soup.select_one("#acrCustomerReviewText")
        if rating_el:
            text = rating_el.get_text(strip=True)
            match = re.search(r"([\d.]+)\s*out of", text)
            if match:
                data["rating"] = float(match.group(1))

        reviews_el = soup.select_one("#acrCustomerReviewText")
        if reviews_el:
            match = re.search(r"([\d,]+)", reviews_el.get_text(strip=True))
            if match:
                data["review_count"] = int(match.group(1).replace(",", ""))

        img_el = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront")
        if img_el:
            data["image_url"] = img_el.get("src", "")

        brand_el = soup.select_one("#bylineInfo") or soup.select_one(".po-brand .a-size-base")
        if brand_el:
            brand_text = brand_el.get_text(strip=True)
            brand_text = re.sub(r"^(Visit the |Brand:\s*)", "", brand_text)
            brand_text = brand_text.replace(" Store", "").strip()
            data["brand"] = brand_text

        avail_el = soup.select_one("#availability") or soup.select_one("#outOfStock")
        if avail_el:
            data["availability"] = avail_el.get_text(strip=True)
        else:
            data["availability"] = "In Stock"

        desc_el = soup.select_one("#productDescription") or soup.select_one("#feature-bullets")
        if desc_el:
            data["description"] = desc_el.get_text(strip=True)[:1000]

        data["specifications"] = self._extract_amazon_specs(soup)
        return data

    def _extract_amazon_specs(self, soup: BeautifulSoup) -> dict:
        specs = {}
        table = soup.select_one("#productDetails_techSpec_section_1") or soup.select_one("#technicalSpecifications_section_1")
        if table:
            for row in table.select("tr"):
                key = row.select_one("th")
                val = row.select_one("td")
                if key and val:
                    specs[key.get_text(strip=True)] = val.get_text(strip=True)
        detail_bullets = soup.select("#detailBullets_feature_div li, #prodDetails .prodDetTable tr")
        for item in detail_bullets[:15]:
            spans = item.select("span")
            if len(spans) >= 2:
                k = spans[0].get_text(strip=True).rstrip(":")
                v = spans[1].get_text(strip=True)
                if k and v:
                    specs[k] = v
        return specs

    def _extract_flipkart(self, soup: BeautifulSoup, url: str) -> dict:
        data = {}
        title_el = soup.select_one("span.VU-ZEz") or soup.select_one("h1.yhB1nd")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        price_el = soup.select_one("div.Nx9bqj._4b5DiR") or soup.select_one("div._30jeq3._16Jk6d")
        if price_el:
            data["price"] = self._parse_price(price_el.get_text(strip=True))

        mrp_el = soup.select_one("div.yRaY8j.Z3DfBu") or soup.select_one("div._3I9_wc.Z3DfBu")
        if mrp_el:
            data["mrp"] = self._parse_price(mrp_el.get_text(strip=True))

        rating_el = soup.select_one("div.XQDdHH._1QuN7K") or soup.select_one("div._3LWZlK._1BLPMq")
        if rating_el:
            match = re.search(r"([\d.]+)", rating_el.get_text(strip=True))
            if match:
                data["rating"] = float(match.group(1))

        reviews_el = soup.select_one("span.Wphh3N") or soup.select_one("span._13vcmD")
        if reviews_el:
            match = re.search(r"([\d,]+)", reviews_el.get_text(strip=True))
            if match:
                data["review_count"] = int(match.group(1).replace(",", ""))

        img_el = soup.select_one("img._396cs4._3n0Glp") or soup.select_one("img._2r_T1I")
        if img_el:
            data["image_url"] = img_el.get("src", "")

        brand_el = soup.select_one("span.BWIKRJ._10LaC2") or soup.select_one("span._2WkVRV")
        if brand_el:
            data["brand"] = brand_el.get_text(strip=True)

        avail_el = soup.select_one("div._16FRkq")
        if avail_el:
            data["availability"] = avail_el.get_text(strip=True)
        else:
            data["availability"] = "In Stock"

        desc_el = soup.select_one("div._1m3Rg7") or soup.select_one("div._11pzQk")
        if desc_el:
            data["description"] = desc_el.get_text(strip=True)[:1000]

        data["specifications"] = self._extract_flipkart_specs(soup)
        return data

    def _extract_flipkart_specs(self, soup: BeautifulSoup) -> dict:
        specs = {}
        rows = soup.select("div._14cfVK tr, table._14cfVK tr")
        for row in rows:
            cells = row.select("td")
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if key and val:
                    specs[key] = val
        return specs

    def _extract_myntra(self, soup: BeautifulSoup, url: str) -> dict:
        data = {}
        title_el = soup.select_one("h1.pdp-title") or soup.select_one("h1")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        price_el = soup.select_one("span.pdp-price-strong") or soup.select_one("span.price-per-piece")
        if price_el:
            data["price"] = self._parse_price(price_el.get_text(strip=True))

        img_el = soup.select_one("img.picture-picture") or soup.select_one("img.jCqzTN")
        if img_el:
            data["image_url"] = img_el.get("src", "")

        return data

    def _extract_ajio(self, soup: BeautifulSoup, url: str) -> dict:
        data = {}
        title_el = soup.select_one("div.item-name") or soup.select_one("h1")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        price_el = soup.select_one("div.price strong") or soup.select_one("span.price")
        if price_el:
            data["price"] = self._parse_price(price_el.get_text(strip=True))

        img_el = soup.select_one("img.rilrtl-products-img__img")
        if img_el:
            data["image_url"] = img_el.get("src", "")

        return data

    def _extract_meesho(self, soup: BeautifulSoup, url: str) -> dict:
        data = {}
        title_el = soup.select_one("h1") or soup.select_one("div[class*='ProductName']")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        price_el = soup.select_one("span[class*='Price']") or soup.select_one("div[class*='Price']")
        if price_el:
            data["price"] = self._parse_price(price_el.get_text(strip=True))

        return data

    def _extract_croma(self, soup: BeautifulSoup, url: str) -> dict:
        data = {}
        title_el = soup.select_one("h1.pdp-title") or soup.select_one("h1")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        price_el = soup.select_one("span.amount") or soup.select_one("div.pdp-price")
        if price_el:
            data["price"] = self._parse_price(price_el.get_text(strip=True))

        img_el = soup.select_one("img.product-image") or soup.select_one("img[alt]")
        if img_el:
            data["image_url"] = img_el.get("src", "")

        return data

    def _extract_reliance(self, soup: BeautifulSoup, url: str) -> dict:
        data = {}
        title_el = soup.select_one("h1.pdp-title") or soup.select_one("h1")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        price_el = soup.select_one("span.amount") or soup.select_one("div.price")
        if price_el:
            data["price"] = self._parse_price(price_el.get_text(strip=True))

        return data

    def _extract_tatacliq(self, soup: BeautifulSoup, url: str) -> dict:
        data = {}
        title_el = soup.select_one("h1.ProductName") or soup.select_one("h1")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        price_el = soup.select_one("span.ProductPrice") or soup.select_one("span.amount")
        if price_el:
            data["price"] = self._parse_price(price_el.get_text(strip=True))

        img_el = soup.select_one("img.product-hero-img")
        if img_el:
            data["image_url"] = img_el.get("src", "")

        return data

    @staticmethod
    def _parse_price(text: str) -> float:
        if not text:
            return 0.0
        cleaned = re.sub(r"[^\d.]", "", text)
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
