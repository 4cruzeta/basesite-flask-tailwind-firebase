# TODO: Construção do WBA Blueprint

Este documento delineia os passos para a construção do módulo de integração com a API Oficial do WhatsApp (`WBA Blueprint`), conforme a estratégia definida no `CHAPTER.md`.

- [ ] **1. Estrutura do Blueprint:**
    - [ ] Criar o diretório `edcat_root/whatsapp`.
    - [ ] Dentro do diretório, criar os arquivos iniciais: `__init__.py`, `routes.py`, e `services.py`.

- [ ] **2. Serviço de Acesso aos Segredos:**
    - [ ] Em `services.py`, criar uma função (`get_whatsapp_credentials`) que utiliza a biblioteca do Google Cloud para buscar os segredos (`WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`) do Secret Manager.

- [ ] **3. Serviço de Envio de Mensagens:**
    - [ ] Em `services.py`, criar uma função (`send_test_message`) que utiliza as credenciais obtidas para fazer uma chamada `POST` para a API da Meta, enviando uma mensagem de teste.

- [ ] **4. Endpoint do Webhook (Recebimento):**
    - [ ] Em `routes.py`, criar o `Blueprint` (`whatsapp_bp`).
    - [ ] Definir a rota `/webhooks/whatsapp` que aceita métodos `GET` e `POST`.
    - [ ] Implementar a lógica para `GET`: Verificação do webhook com a Meta, comparando o `hub.verify_token` com nosso `WHATSAPP_VERIFY_TOKEN`.
    - [ ] Implementar a lógica para `POST`: Receber o corpo da mensagem, registrar (log) o payload e retornar um status `200 OK`.

- [ ] **5. Rota de Teste (Envio):**
    - [ ] Em `routes.py`, criar uma rota de teste (ex: `/test/send`) que chama o serviço `send_test_message` para disparar uma mensagem.

- [ ] **6. Registro do Blueprint:**
    - [ ] No arquivo principal da aplicação (`main.py`), importar e registrar o `whatsapp_bp`, adicionando um prefixo de URL (ex: `/whatsapp`).
