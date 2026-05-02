from pathlib import Path
from urllib.parse import urlparse

from scrapy.spiders import SitemapSpider


class TBankHelpSpider(SitemapSpider):
    name = "tbank_help"
    allowed_domains = ["tbank.ru"]

    sitemap_urls = ["https://www.tbank.ru/help/sitemap.xml"]

    # Custom settings to be polite and efficient
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # noqa: E501
        "DOWNLOAD_DELAY": 1,  # Be respectful: 1 second delay between requests
        "CONCURRENT_REQUESTS": 8,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def sitemap_filter(self, entries):
        for entry in entries:
            if "/mobile-operator/" not in entry["loc"]:
                yield entry

    # Rules for extracting and following links
    sitemap_rules = ((r".*", "parse_help_page"),)

    def parse_help_page(self, response):
        """
        Parse each help page and save raw HTML
        """
        # Generate a safe filename from the URL path
        parsed_url = urlparse(response.url)
        path = parsed_url.path.strip("/")

        if not path:
            filename = "index.html"
        else:
            # Replace slashes with underscores for filesystem safety
            filename = f"{path.replace('/', '_')}.html"

        # Create output directory if it doesn't exist
        output_dir = "data/raw/tbank_help_pages"
        Path(output_dir).mkdir(exist_ok=True, parents=True)

        # Save raw HTML to file
        filepath = Path(output_dir / filename)
        with Path.open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Also yield the data as an item for further processing
        yield {
            "url": response.url,
            "title": response.css("title::text").get(),
            "filepath": filepath,
            "status_code": response.status,
        }

        # Optional: Log progress
        self.logger.info(f"Saved: {response.url} -> {filepath}")
