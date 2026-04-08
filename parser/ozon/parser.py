import re
import logging

from typing import Optional
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def _parse_price_from_html(html: str) -> Optional[float]:
    """Извлечение цены из HTML с помощью BeautifulSoup."""

    soup = BeautifulSoup(html, "html.parser")
    price_elem = soup.find(
            "span",
            class_="pdp_bj tsHeadline600Large"
    )
    logger.info("Raw Ozon price text extracted: %s", price_elem)

    try:
        img = soup.find("img", elementtiming="lcp_eltiming_webGallery-3311626-default-1")["src"]
        logger.info("Parsed product image url: %s", img)

    except Exception:
        logger.warning("Product image not found in html")
        img = None

    if not price_elem:
        logger.warning("priceBlockFinalPrice element not found")
        return None

    price_text = price_elem.get_text(strip=True)
    logger.info("Raw WB price text extracted: %s", price_text)

    price = round(float(
        re.sub(r"[^\d,\.]", "", price_text).replace(",", ".")
    ), 2)
    currency = re.sub(r"[\d,.\s]", "", price_text)
    logger.info("Parsed WB price float1: %s %s", price, currency)
    return price, currency, img
