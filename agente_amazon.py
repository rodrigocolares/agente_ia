import csv
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

from amazon_paapi import AmazonApi


# ==========================
# CONFIGURAÇÕES DO AGENTE
# ==========================

# --- Credenciais da Amazon Product Advertising API (PAAPI) ---
AWS_ACCESS_KEY = "SUA_AWS_ACCESS_KEY"
AWS_SECRET_KEY = "SUA_AWS_SECRET_KEY"
ASSOCIATE_TAG = "SUA_ASSOCIATE_TAG"  # ex: "seutag-20"

# Marketplace Brasil
AMAZON_COUNTRY = "BR"

# --- Configurações de e-mail (SMTP) ---
SMTP_SERVER = "smtp.gmail.com"          # ou outro servidor SMTP
SMTP_PORT = 587                         # 587 (TLS) é comum
EMAIL_SENDER = "email@gmail.com"    # e-mail que vai enviar
EMAIL_PASSWORD = "Senha"  # use app password se for Gmail
EMAIL_RECIPIENT = "email@destino"

# --- Palavras-chave a pesquisar ---
KEYWORDS = [
    "café especial",
    "secante para lava louças",
    "duracell pilhas",
    "detergente para lava louças",
    "smart lampadas da positivo",
]

# Quantidade máxima de itens por palavra-chave
MAX_ITEMS_PER_KEYWORD = 10

# Nome do arquivo CSV de saída
CSV_FILENAME = "melhores_precos_amazon_br.csv"


# ==========================
# FUNÇÃO: INICIALIZAR CLIENTE AMAZON
# ==========================

def create_amazon_client():
    """
    Cria o cliente da Amazon Product Advertising API para o marketplace do Brasil.
    """
    api = AmazonApi(
        AWS_ACCESS_KEY,
        AWS_SECRET_KEY,
        ASSOCIATE_TAG,
        AMAZON_COUNTRY
    )
    return api


# ==========================
# FUNÇÃO: BUSCAR PRODUTOS POR PALAVRA-CHAVE
# ==========================

def search_products_by_keyword(api, keyword, max_items=10):
    """
    Busca produtos na Amazon Brasil por palavra-chave e retorna uma lista de dicionários
    com informações relevantes (título, preço, link, etc.).
    """
    print(f"Buscando produtos para a palavra-chave: {keyword!r}...")

    try:
        items = api.search_items(
            keyword,
            item_count=max_items
        )
    except Exception as e:
        print(f"Erro ao buscar produtos para '{keyword}': {e}")
        return []

    results = []

    for item in items:
        title = getattr(item, "title", None)
        url = getattr(item, "detail_page_url", None)

        # Alguns itens podem não ter preço disponível
        price = None
        currency = None

        try:
            if item.offers and item.offers.listings:
                listing = item.offers.listings[0]
                if listing.price:
                    price = listing.price.amount
                    currency = listing.price.currency
        except Exception:
            pass

        if not title or not url:
            continue

        results.append({
            "keyword": keyword,
            "title": title,
            "price": price,
            "currency": currency,
            "url": url
        })

    return results


# ==========================
# FUNÇÃO: SELECIONAR MELHOR PREÇO POR PALAVRA-CHAVE
# ==========================

def get_best_price_per_keyword(all_results):
    """
    Recebe uma lista de resultados (de várias palavras-chave) e retorna,
    para cada palavra-chave, o item com menor preço disponível.
    """
    best_by_keyword = {}

    for item in all_results:
        keyword = item["keyword"]
        price = item["price"]

        # Ignora itens sem preço
        if price is None:
            continue

        if keyword not in best_by_keyword:
            best_by_keyword[keyword] = item
        else:
            if price < best_by_keyword[keyword]["price"]:
                best_by_keyword[keyword] = item

    # Converte para lista
    return list(best_by_keyword.values())


# ==========================
# FUNÇÃO: GERAR CSV
# ==========================

def generate_csv(data, filename):
    """
    Gera um arquivo CSV com os dados dos melhores preços.
    """
    print(f"Gerando arquivo CSV: {filename}...")

    fieldnames = ["keyword", "title", "price", "currency", "url"]

    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print("CSV gerado com sucesso.")


# ==========================
# FUNÇÃO: ENVIAR E-MAIL COM ANEXO
# ==========================

def send_email_with_attachment(
    smtp_server,
    smtp_port,
    email_sender,
    email_password,
    email_recipient,
    subject,
    body,
    attachment_path
):
    """
    Envia um e-mail com um arquivo em anexo (CSV).
    """
    print(f"Enviando e-mail para {email_recipient} com anexo {attachment_path}...")

    msg = EmailMessage()
    msg["From"] = email_sender
    msg["To"] = email_recipient
    msg["Subject"] = subject
    msg.set_content(body)

    # Lê o arquivo e anexa
    with open(attachment_path, "rb") as f:
        file_data = f.read()
        file_name = attachment_path

    msg.add_attachment(
        file_data,
        maintype="text",
        subtype="csv",
        filename=file_name
    )

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(email_sender, email_password)
        server.send_message(msg)

    print("E-mail enviado com sucesso.")


# ==========================
# FUNÇÃO PRINCIPAL
# ==========================

def main():
    # 1. Criar cliente Amazon
    api = create_amazon_client()

    # 2. Buscar produtos para todas as palavras-chave
    all_results = []
    for kw in KEYWORDS:
        results = search_products_by_keyword(api, kw, MAX_ITEMS_PER_KEYWORD)
        all_results.extend(results)

    if not all_results:
        print("Nenhum produto encontrado. Verifique suas credenciais ou termos de busca.")
        return

    # 3. Selecionar melhor preço por palavra-chave
    best_items = get_best_price_per_keyword(all_results)

    if not best_items:
        print("Nenhum item com preço encontrado.")
        return

    # 4. Gerar CSV
    generate_csv(best_items, CSV_FILENAME)

    # 5. Enviar e-mail com o CSV em anexo
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    subject = f"Melhores preços Amazon BR - {now_str}"
    body = (
        "Olá Rodrigo,\n\n"
        "Segue em anexo o arquivo CSV com os melhores preços encontrados na Amazon Brasil "
        "para as palavras-chave configuradas.\n\n"
        "Gerado automaticamente pelo seu agente de IA.\n"
    )

    send_email_with_attachment(
        SMTP_SERVER,
        SMTP_PORT,
        EMAIL_SENDER,
        EMAIL_PASSWORD,
        EMAIL_RECIPIENT,
        subject,
        body,
        CSV_FILENAME
    )


if __name__ == "__main__":
    main()
