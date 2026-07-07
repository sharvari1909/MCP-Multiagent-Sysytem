import re
from email.utils import parseaddr

from mcp.inventory_server.tools import get_all_products


NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

TEXT_QUOTATION_PATTERNS = [
    r"\btext\s+(quotation|qotation|quote)\b",
    r"\b(quotation|qotation|quote)\s+in\s+text\b",
    r"\bwritten\s+(quotation|qotation|quote)\b",
    r"\bplain\s+text\s+(quotation|qotation|quote)\b",
    r"\b(quotation|qotation|quote)\s+as\s+text\b",
    r"\btext\s+format\b",
    r"\bwritten\s+format\b",
    r"\bonly\s+text\b",
    r"\bno\s+pdf\b",
    r"\bdo\s+not\s+send\s+(a\s+)?pdf\b",
    r"\bdon't\s+send\s+(a\s+)?pdf\b",
]


def extract_email_address(value: str):
    return parseaddr(value or "")[1] or value


def wants_text_quotation(email_data: dict):
    text = f"{email_data.get('subject', '')} {email_data.get('body', '')}".lower()
    return any(re.search(pattern, text) for pattern in TEXT_QUOTATION_PATTERNS)


def parse_invoice_request(email_data: dict):
    text = f"{email_data.get('subject', '')} {email_data.get('body', '')}".lower()
    products = get_all_products()

    for product in products:
        names = {
            product["name"].lower(),
            product["name"].lower().rstrip("s"),
            product["sku"].lower(),
        }

        if any(name and name in text for name in names):
            quantity = _extract_quantity(text, product["name"])
            return {
                "product": product,
                "sku": product["sku"],
                "quantity": quantity,
            }

    return None


def _extract_quantity(text: str, product_name: str):
    product_pattern = re.escape(product_name.lower().rstrip("s"))
    digit_match = re.search(rf"\b(\d+)\b\s+{product_pattern}s?\b", text)

    if digit_match:
        return max(1, int(digit_match.group(1)))

    for word, value in NUMBER_WORDS.items():
        if re.search(rf"\b{word}\b\s+{product_pattern}s?\b", text):
            return value

    any_digit = re.search(r"\b(\d+)\b", text)
    if any_digit:
        return max(1, int(any_digit.group(1)))

    return 1
