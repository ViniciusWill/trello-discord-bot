# 🤖 Trello Discord Bot

Bot desenvolvido a partir de uma ideia própria para agilizar o andamento do setor de suporte — eliminando a necessidade de ficar verificando manualmente o Trello para saber se um novo chamado havia chegado.

## O que o bot faz

O bot monitora uma lista específica do Trello em intervalos de 5 segundos. Quando um novo cartão é criado nessa lista, ele envia automaticamente uma mensagem de alerta no Discord com as seguintes informações:

- **Usuário:** nome de quem abriu o chamado (extraído do título do cartão ou do membro atribuído)
- **Lista:** nome da lista monitorada
- **Cartão:** título completo do cartão criado

Os cartões já notificados são salvos localmente em `cartoes_vistos.json`, garantindo que o mesmo cartão não gere alertas duplicados.

## Pré-requisitos

- Python 3.8+
- Uma conta no [Trello](https://trello.com) com acesso à API
- Um webhook configurado no Discord

## Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/ViniciusWill/trello-discord-bot.git
cd trello-discord-bot
```

**2. Instale as dependências**
```bash
pip install -r requirements.txt
```

**3. Configure as variáveis de ambiente**

Copie o arquivo de exemplo e preencha com suas credenciais:
```bash
cp .env.example .env
```

Abra o `.env` e preencha os valores — veja a seção abaixo sobre como obter cada um.

**4. Execute o bot**
```bash
python bot.py
```

## Variáveis de ambiente

| Variável | Descrição | Como obter |
|---|---|---|
| `DISCORD_WEBHOOK_URL` | URL do webhook do Discord | No seu servidor Discord: Configurações do canal → Integrações → Webhooks → Novo Webhook → Copiar URL |
| `TRELLO_KEY` | Chave da API do Trello | Acesse [trello.com/power-ups/admin](https://trello.com/power-ups/admin) e crie um Power-Up para obter a chave |
| `TRELLO_TOKEN` | Token de autenticação do Trello | Após obter a chave, acesse `https://trello.com/1/authorize?expiration=never&scope=read&response_type=token&key=SUA_CHAVE` |
| `LISTA_ALVO_ID` | ID da lista do Trello a ser monitorada | Abra o cartão de qualquer card da lista desejada, adicione `.json` ao final da URL e procure pelo campo `idList` |

## Estrutura do projeto

```
trello-discord-bot/
├── bot.py            # Código principal do bot
├── .env              # Suas credenciais (não sobe para o git)
├── .env.example      # Modelo das variáveis necessárias
├── .gitignore        
├── requirements.txt  
└── README.md
```

## Observações

- O arquivo `.env` **nunca** deve ser enviado ao GitHub — ele já está listado no `.gitignore`
- O arquivo `cartoes_vistos.json` é criado automaticamente na primeira execução
- Para rodar o bot em segundo plano em um servidor, considere usar `screen`, `tmux` ou configurá-lo como um serviço do sistema
