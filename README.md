Script único em Python que:

Busca na Amazon Brasil pelos termos de palavra‑chave.

Pega os melhores preços (menor preço por produto retornado).

Gera um arquivo CSV.

Envia esse CSV por e‑mail para rodrigoleaocolares@hotmail.com.

Vou usar:

Amazon Product Advertising API (PAAPI 5) via wrapper Python (gratuito, mas você precisa criar credenciais de afiliado).

SMTP para envio de e‑mail (por exemplo, Gmail ou outro provedor).

Você só precisa preencher as credenciais nos lugares marcados.

com Python instalado, rode no terminal:
pip install amazon-paapi
Obs: se esse pacote der problema, você pode usar o amazon-paapi5 ou outro wrapper similar, mas vou usar o mais direto aqui. A lógica do código continua a mesma.

Criar credenciais da Amazon
Você vai precisar de:

AWS_ACCESS_KEY

AWS_SECRET_KEY

ASSOCIATE_TAG (tag de afiliado)

Marketplace: BR (Brasil)

Isso vem da sua conta de Amazon Afiliados / Product Advertising API.
