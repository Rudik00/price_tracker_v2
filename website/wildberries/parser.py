import re
import logging

from typing import Optional
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

WB_DANGER_CLASS = (
    "mo-typography mo-typography_variant_title2 "
    "mo-typography_variable-weight_title2 "
    "mo-typography_variable mo-typography_color_danger "
    "priceBlockFinalPrice--iToZR"
)

WB_PRIMARY_CLASS = (
    "mo-typography mo-typography_variant_title2 "
    "mo-typography_variable-weight_title2 "
    "mo-typography_variable mo-typography_color_primary "
    "priceBlockFinalPrice--iToZR"
)


def _parse_price_from_html(html: str) -> Optional[float]:
    """Извлечение цены из HTML с помощью BeautifulSoup."""

    soup = BeautifulSoup(html, "html.parser")
    price_elem = (
        soup.find(
            "ins",
            class_=WB_DANGER_CLASS,
        )
        or soup.find(
            "ins",
            class_=WB_PRIMARY_CLASS,
        )
    )

    if not price_elem:
        logger.warning("priceBlockFinalPrice element not found")
        return None

    price_text = price_elem.get_text(strip=True)
    logger.info("Raw WB price text extracted: %s", price_text)

    price = round(float(
        re.sub(r"[^\d,\.]", "", price_text).replace(",", ".")
    ), 2)
    logger.info("Parsed WB price float: %s", price)
    return price
