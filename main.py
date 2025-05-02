import os
import re
import sys
import pandas as pd
from loguru import logger
from services.openai_client import openai_client_authentication
from services.sheets_client import google_client_authentication

# Loading environment variables
openai_key = os.getenv("OPENAI_API_KEY")
google_credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
sheet_id = os.getenv("SHEET_ID")

if not all([openai_key, google_credentials_path, sheet_id]):
    logger.error("Missing environment variables.")
    sys.exit(1)

logger.info("Authenticating with OpenAI and Google Sheets.")
openai_client = openai_client_authentication(openai_key)
spreadsheet = google_client_authentication(google_credentials_path, sheet_id)

logger.success("Authentication successful.")

# Sheets
sheet_raw = spreadsheet.worksheet("Dados Brutos")
sheet_processed = spreadsheet.worksheet("Pedidos Processados")

raw_data = sheet_raw.get_all_values()
logger.info(f"Loaded raw data: {len(raw_data)-1} rows.")

df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

processed_ids = set(sheet_processed.col_values(3)[1:])
logger.info(f"Processed IDs: {len(processed_ids)}")

new_data = df[~df["ID do Pedido Yampi"].isin(processed_ids)]
logger.info(f"New orders to process: {len(new_data)}")

new_data_cleaned = new_data.drop_duplicates(subset=["ID do Pedido Yampi"], keep="first")
duplicates_removed = len(new_data) - len(new_data_cleaned)
if duplicates_removed > 0:
    logger.warning(f"{duplicates_removed} duplicates removed.")
new_data = new_data_cleaned

valid_products = [
    "Urocianina Gotas", "Insufree Gotas", "L-Nicotinina", "Evo Prost Gotas",
    "Fortisol", "Urocianina", "Insufree", "Lutrazina", "Viriforte",
    "Condroczol", "Revert Vision", "Next Vision", "Prostatina", "Prostzol",
    "Gliconix", "Maxprost", "Antocionidinol", "Glicofree"
]

manager_acronym_regex = re.compile(r"-\s*([A-Z]{2})\s*$")
fallback_regex = re.compile(r"-\s*([A-Z]{2})\s*")
quantity_regex = re.compile(r"(\d+)\s*(frasco|pote|unidade)", re.I)
light_regex = re.compile(r"Leve\s*(\d+)", re.I)

# Extract product name from description with improved matching
def extract_product_name(description: str) -> str | None:
    prompt = f"""
    Dado o texto abaixo, extraia apenas o nome do produto com base nessa lista:
    {", ".join(valid_products)}.
    Texto: \"{description}\".
    Retorne apenas o nome EXATO da lista, o mais próximo possível.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        result = response.choices[0].message.content.strip()

        for product in valid_products:
            if product.lower() in result.lower() or result.lower() in product.lower():
                return product
        return None
    except Exception as e:
        logger.error(f"Error extracting product name: {e}")
        return None

# Parsing product info and generating order details
def parse_product_info(product: str, quantity_raw: str):
    manager_match = manager_acronym_regex.search(product) or fallback_regex.search(product)
    manager = manager_match.group(1) if manager_match else "XX"

    sale_type = (
        "Callcenter" if "CALL" in product else
        "Recuperation" if "REC" in product else
        "Upsell" if "upsell" in product.lower() else
        "Normal"
    )

    quantity = 1
    match_leve = light_regex.findall(product)
    match_generic = quantity_regex.findall(product)

    if match_leve:
        quantity = int(match_leve[0])
    elif match_generic:
        quantity = int(match_generic[0][0])

    order_bump = "Yes" if "|" in product and int(quantity_raw) >= 2 else "No"
    if order_bump == "Yes":
        quantity += 1
    if sale_type in ["Callcenter", "Recuperation"]:
        order_bump = "No"

    product_name = extract_product_name(product)
    if not product_name:
        logger.error(f"Invalid product name: {product}")
        return None, None, None, None, None

    return manager, sale_type, product_name, quantity, order_bump

processed_rows = []
logger.info(f"Processing {len(new_data)} new rows.")

for _, row in new_data.iterrows():
    try:
        manager, sale_type, product_name, quantity, order_bump = parse_product_info(row["Produto"], row["Quantidade"])

        if product_name is None:
            continue

        upsell = "Yes" if sale_type == "Upsell" and order_bump == "No" else "No"

        processed_rows.append([
            row["Data de Criação"],
            row["Data de Pagamento"],
            row["ID do Pedido Yampi"],
            manager,
            sale_type,
            upsell,
            order_bump,
            row["Cliente"],
            row["Email"],
            row["Produto"],
            product_name,
            quantity,
            row["Valor Total"]
        ])

    except Exception as e:
        logger.error(f"Error processing row {row['ID do Pedido Yampi']}: {e}")

# Update processed sheet with new order data
logger.info(f"Updating {len(processed_rows)} rows in the processed sheet.")
sheet_processed.append_rows(processed_rows)

logger.success("Process completed successfully.")
