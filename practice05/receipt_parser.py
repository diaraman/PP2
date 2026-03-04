import json
import re
from pathlib import Path


AMOUNT_PATTERN = r"\d{1,3}(?: \d{3})*,\d{2}"


def money_to_float(value):
    value = value.replace(" ", "")
    value = value.replace(",", ".")
    return float(value)


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_all_prices(text):
    prices = []
    for m in re.finditer(AMOUNT_PATTERN, text):
        value = m.group(0)

        # Skip partial match like "2,00" from "2,000"
        if m.end() < len(text) and text[m.end()].isdigit():
            continue

        # Skip quantity in "1,000 x 154,00"
        tail = text[m.end():].lstrip()
        if tail.startswith("x"):
            continue

        prices.append(money_to_float(value))
    return prices


def extract_products(text):
    # Example block:
    # 1.
    # Product name
    # 2,000 x 154,00
    # 308,00
    pattern = re.compile(
        r"(?ms)^\s*(\d+)\.\s*\n"                # item number
        r"(.+?)\n"                              # product name
        r"\s*(\d+,\d{3})\s*x\s*(" + AMOUNT_PATTERN + r")\s*\n"  # qty x unit
        r"\s*(" + AMOUNT_PATTERN + r")\s*$"     # line total
    )

    matches = pattern.findall(text)
    products = []
    for m in matches:
        number = int(m[0])
        name = clean_text(m[1])
        quantity = float(m[2].replace(",", "."))
        unit_price = money_to_float(m[3])
        line_total = money_to_float(m[4])

        product = {
            "item_no": number,
            "name": name,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": line_total
        }
        products.append(product)

    return products


def extract_total(text):
    m = re.search(r"ИТОГО:\s*\n\s*(" + AMOUNT_PATTERN + r")", text)
    if m:
        return money_to_float(m.group(1))
    return None


def extract_date_time(text):
    m = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})", text)
    if m:
        return {"date": m.group(1), "time": m.group(2)}
    return {"date": None, "time": None}


def extract_payment_method(text):
    m = re.search(r"^(Банковская карта|Наличные|Карта):", text, re.MULTILINE)
    if m:
        return m.group(1)
    return None


def parse_receipt(text):
    products = extract_products(text)
    all_prices = extract_all_prices(text)
    receipt_total = extract_total(text)
    payment_method = extract_payment_method(text)
    date_time = extract_date_time(text)

    computed_total = 0
    for p in products:
        computed_total += p["line_total"]
    computed_total = round(computed_total, 2)

    product_names = []
    for p in products:
        product_names.append(p["name"])

    return {
        "payment_method": payment_method,
        "datetime": date_time,
        "products": products,
        "product_names": product_names,
        "all_prices": all_prices,
        "computed_total": computed_total,
        "receipt_total": receipt_total,
        "total_matches": receipt_total == computed_total if receipt_total is not None else None
    }


def main():
    raw_path = Path(__file__).with_name("raw.txt")
    text = raw_path.read_text(encoding="utf-8")
    parsed = parse_receipt(text)
    print(json.dumps(parsed, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
