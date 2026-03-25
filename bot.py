from dotenv import load_dotenv
import requests
import logging
import time
import json
import os
import sys


# -- Caminhos API
load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TRELLO_KEY          = os.getenv("TRELLO_KEY")
TRELLO_TOKEN        = os.getenv("TRELLO_TOKEN")
LISTA_ALVO_ID       = os.getenv("LISTA_ALVO_ID")
ARQUIVO_ESTADO      = "cartoes_vistos.json"

def validar_configuracao():
    variaveis = {
        "DISCORD_WEBHOOK_URL": DISCORD_WEBHOOK_URL,
        "TRELLO_KEY": TRELLO_KEY,
        "TRELLO_TOKEN": TRELLO_TOKEN,
        "LISTA_ALVO_ID": LISTA_ALVO_ID
    }
    faltando = [k for k, v in variaveis.items() if not v]
    if faltando:
        logging.error(f"Variáveis de ambiente não configuradas: {', '.join(faltando)}")
        sys.exit(1)


# -- Cofinguração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def carregar_cartoes_vistos():
    """Carrega o set de IDs de cartões do arquivo de estado."""
    if not os.path.exists(ARQUIVO_ESTADO):
        return set() 
    try:
        with open(ARQUIVO_ESTADO, 'r') as f:
            data = json.load(f)
            return set(data.get('vistos', []))
    except json.JSONDecodeError:
        logging.error(f"Erro ao ler arquivo de estado.")
        return set()

def salvar_cartoes_vistos(ids_cartoes):
    """Salva o set de IDs de cartões no arquivo de estado."""
    try:
        with open(ARQUIVO_ESTADO, 'w') as f:
            json.dump({'vistos': list(ids_cartoes)}, f)
    except Exception as e:
        logging.error(f"Erro ao salvar Arquivo_Estado: {e}")

def extrair_nome_usuario(card_name, member_creator):
    """Extrai o nome do usuário do título do cartão, ou usa o criador."""
    if not card_name:
        card_name = ""
    partes = card_name.rsplit('–', 1) 
    if len(partes) < 2:
        partes = card_name.rsplit('-', 1) 
    if len(partes) == 2 and len(partes[1].strip()) > 0:
        return partes[1].strip().title()
    else:
        return member_creator

def enviar_discord(mensagem):
    """Envia a mensagem formatada para o Discord."""
    try:
        payload_discord = {"content": mensagem}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload_discord)
        response.raise_for_status() # Verifica se houve erro HTTP
        logging.info(f"Mensagem enviada para o Discord!")
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem para o discord: {e}")

def verificar_trello():
    """Função principal que verifica novos cartões."""
    logging.info(f"Verificando novos cards no Trello... (Lista: {LISTA_ALVO_ID})")
    url_trello = f"https://api.trello.com/1/lists/{LISTA_ALVO_ID}/cards"

    query_params = {
        'key': TRELLO_KEY,
        'token': TRELLO_TOKEN,
        'members': 'true', 
        'member_fields': 'fullName' 
    }

    try:
        response = requests.get(url_trello, params=query_params)
        response.raise_for_status()
        cartoes_na_lista = response.json()
        cartoes_vistos = carregar_cartoes_vistos()
        novos_cartoes_encontrados = False
        
        # -- Processa Cards
        for cartao in cartoes_na_lista:
            card_id = cartao.get('id')
            
            #  -- Verifica se é novo 
            if card_id not in cartoes_vistos:
                logging.info(f" Novo cartão encontrado: {card_id} ---")
                novos_cartoes_encontrados = True
                card_name = cartao.get('name', "")
                list_name = "Suportes a fazer" 
                
                # -- Acha o nome do solicitante
                creator_name = "Usuário Desconhecido"
                if cartao.get('members') and len(cartao['members']) > 0:
                    creator_name = cartao['members'][0].get('fullName', creator_name)
                
                member_name = extrair_nome_usuario(card_name, creator_name)
                
                # -- Mensagem que será exibida no discord
                mensagem = (
                    f"🚨 **Novo Suporte na Fila!** 🚨\n\n"
                    f"**Usuário:** {member_name}\n"
                    f"**Lista:** {list_name}\n"
                    f"**Cartão:** `{card_name}`"
                )
                enviar_discord(mensagem)
                cartoes_vistos.add(card_id)

        if novos_cartoes_encontrados:
            salvar_cartoes_vistos(cartoes_vistos)
            logging.info(f" Lista de cartões vistos foi atualizada.")
        else:
            logging.info(f" Nenhum cartão novo encontrado.")

    except Exception as e:
        logging.error(f" Erro na verificação: {e}")

# -- Main
if __name__ == "__main__":
    validar_configuracao()
    logging.info("Iniciando bot...")
    while True:
        try:
            verificar_trello()
            logging.info("Próxima verificação em 5 segundos...")
            time.sleep(5)
        except KeyboardInterrupt:
            logging.warning(f"\n Desativado por solicitação!")
            sys.exit()
        except Exception as e:
            logging.error(f"Erro no loop: {e}")
            time.sleep(30)