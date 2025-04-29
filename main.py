import os
import re
import sys
import pandas as pd
from loguru import logger
from services.openai_client import openai_client_authentication
from services.sheets_client import google_client_authentication

openai_key = os.getenv("OPENAI_API_KEY")
google_credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
sheet_id = os.getenv("SHEET_ID")

if not all([openai_key, google_credentials_path, sheet_id]):
    logger.error("Variáveis de ambiente ausentes.")
    sys.exit(1)

logger.info("Authenticating with OpenAI and Google Sheets.")
openai_client = openai_client_authentication(openai_key)
spreadsheet = google_client_authentication(google_credentials_path, sheet_id)

sheet_raw = spreadsheet.worksheet("Dados Brutos")
sheet_processed = spreadsheet.worksheet("Pedidos Processados")

raw_data = sheet_raw.get_all_values()
df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

processed_ids = set(sheet_processed.col_values(3)[1:])
new_data = df[~df["ID do Pedido Yampi"].isin(processed_ids)]

gestor_matches = df["Produto"].str.extractall(r"(?:[\(-]|\s-\s*)([A-Z]{2})(?:[\)-]|\s|$)")
unique_managers = gestor_matches[0].dropna().unique()

if len(unique_managers) == 0:
    logger.warning("Nenhum gestor detectado. Regex vazio, fallback ativado.")
    unique_managers = ["XX"]

manager_regex = re.compile(r"(?:[\(-]|\s-\s*)(" + "|".join(map(re.escape, unique_managers)) + r")", re.I)
quantity_regex = re.compile(r"(\d+)\s*(frasco|pote|unidade)", re.I)
light_regex = re.compile(r"Leve\s*(\d+)", re.I)

valid_products = [
    "Urocianina Gotas", "Insufree Gotas", "L-Nicotinina", "Evo Prost Gotas",
    "Fortisol", "Urocianina", "Insufree", "Lutrazina", "Viriforte",
    "Condroczol", "Revert Vision", "Next Vision", "Prostatina", "Prostzol",
    "Gliconix", "Maxprost", "Antocionidinol", "Glicofree"
]

def extract_product_name(description: str) -> str:
    prompt = f"""
    Extraia APENAS o nome correto do produto dentre os seguintes:
    {", ".join(valid_products)}.
    Descrição: \"{description}\".
    Retorne somente o nome do produto.
    """
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0,
        max_tokens=10
    )
    return response.choices[0].message.content.strip()

def parse_product_info(product: str, quantity_raw: str):
    manager_match = manager_regex.findall(product)
    manager = manager_match[-1] if manager_match else "Desconhecido"

    sale_type = (
        "Callcenter" if "CALL" in product else
        "Recuperação" if "REC" in product else
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

    order_bump = "Sim" if "|" in product and int(quantity_raw) >= 2 else "Não"
    if order_bump == "Sim":
        quantity += 1
    if sale_type in ["Callcenter", "Recuperação"]:
        order_bump = "Não"

    product_name = extract_product_name(product)

    return manager, sale_type, product_name, quantity, order_bump

processed_rows = []
logger.info(f"Processing {len(new_data)} new rows.")

for _, row in new_data.iterrows():
    manager, sale_type, product_name, quantity, order_bump = parse_product_info(row["Produto"], row["Quantidade"])
    upsell = "Sim" if sale_type == "Upsell" and order_bump == "Não" else "Não"

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
        row["Valor Total"],
        row["Status"],
        row["Método de Pagamento"]
    ])

if processed_rows:
    last_row = len(sheet_processed.col_values(1))
    logger.info(f"Updating {len(processed_rows)} rows in processed sheet.")
    sheet_processed.update(processed_rows, range_name=f"A{last_row+1}")

logger.success("Process completed successfully.")
