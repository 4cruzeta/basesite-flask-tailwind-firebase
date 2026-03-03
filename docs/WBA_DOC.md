# WBA - Guia de Implementação do WhatsApp Business API

Este documento serve como o guia técnico central para a integração do nosso sistema com a API Oficial do WhatsApp Business (WBA). Ele detalha a arquitetura, os fluxos de dados e as lições aprendidas durante a implementação.

---

## 1. Arquitetura Geral

A integração é composta por dois fluxos principais:

1.  **Recebimento de Eventos (Inbound):** A Meta (Facebook) nos envia eventos através de um endpoint de webhook que nós expomos. O principal evento é o `messages`, que indica uma nova mensagem de um usuário.
2.  **Envio de Mensagens (Outbound):** Nós enviamos mensagens para os usuários fazendo chamadas diretas à API Graph da Meta.

Os arquivos-chave para esta integração são:
-   `edcat_root/whatsapp/routes.py`: Controla o endpoint do webhook, recebendo e processando todos os eventos da Meta.
-   `edcat_root/whatsapp/services.py`: Contém a lógica para enviar mensagens para a API da Meta.

## 2. Autenticação e Credenciais

Todas as credenciais são gerenciadas de forma segura através do **Google Secret Manager**. Isso evita que segredos sejam expostos no código-fonte.

-   `WHATSAPP_ACCESS_TOKEN`: Token de acesso à API Graph. Usado para autorizar nossas chamadas de envio de mensagens.
-   `WHATSAPP_VERIFY_TOKEN`: Um token secreto que nós definimos. A Meta o utiliza na verificação do webhook para garantir que ela está se comunicando com o nosso servidor.
-   `WHATSAPP_PHONE_NUMBER_ID`: O ID do número de telefone da empresa registrado na plataforma da Meta.

## 3. Fluxo de Recebimento de Eventos (Webhook)

Nosso endpoint em `/webhooks/whatsapp` lida com duas operações distintas, diferenciadas pelo método HTTP.

### 3.1. Verificação do Webhook (GET)

Este é um aperto de mão (handshake) que ocorre uma única vez, quando configuramos o endpoint no painel da Meta.

1.  A Meta envia uma requisição `GET` para o nosso endpoint.
2.  Essa requisição contém os query parameters: `hub.mode`, `hub.verify_token`, e `hub.challenge`.
3.  Nosso código verifica se `hub.mode` é `subscribe` e se o `hub.verify_token` corresponde ao nosso `WHATSAPP_VERIFY_TOKEN`.
4.  Se a verificação for bem-sucedida, retornamos o valor de `hub.challenge` com um status `200 OK`. Isso confirma o endpoint para a Meta.

### 3.2. Recebimento de Eventos (POST)

Após a verificação, a Meta envia todas as notificações de eventos (como novas mensagens) via requisições `POST`.

-   **Estrutura do Payload:** O corpo da requisição é um JSON com uma estrutura aninhada: `entry` -> `changes` -> `value`.
-   **Tipos de Evento:** Dentro do objeto `value`, podemos identificar o tipo de evento.
    -   `value.messages`: Indica uma nova mensagem de um usuário. Este é o evento principal para a nossa lógica de negócios.
    -   `value.message_echoes`: Indica uma confirmação de que uma mensagem enviada *por nós* foi entregue. (Ver Lições Aprendidas).

-   **Processamento:** Nosso código verifica a existência de `messages`, extrai o corpo da mensagem (`text.body`) e o número do remetente (`from`), e então passa essa informação para o nosso Agente de IA (`rag_agent`) para gerar uma resposta.

## 4. Fluxo de Envio de Mensagens

A função `send_whatsapp_message` em `services.py` encapsula essa lógica.

1.  **Endpoint:** `https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages`
2.  **Autorização:** A requisição inclui o cabeçalho `Authorization: Bearer {ACCESS_TOKEN}`.
3.  **Payload:** O corpo da requisição é um JSON que especifica o destinatário e o conteúdo da mensagem.
    ```json
    {
      "messaging_product": "whatsapp",
      "to": "USER_PHONE_NUMBER",
      "type": "text",
      "text": { "body": "Hello from the agent!" }
    }
    ```

## 5. Lições Aprendidas: A Saga do `message_echoes`

A subscrição ao evento `message_echoes` através do painel da Meta falhou repetidamente. A requisição de subscrição nem chegava ao nosso servidor.

-   **Diagnóstico:** Implementamos uma "armadilha" no código para registrar qualquer tentativa de comunicação. Descobrimos que, ao clicar em "Testar", a Meta não envia um desafio de verificação, mas um **exemplo de payload** do evento `message_echoes`.
-   **Solução Parcial:** Adaptamos o código para ser "bilíngue", ou seja, para entender tanto o payload de `messages` quanto o de `message_echoes`.
-   **Problema na Plataforma:** Mesmo com o código correto, a subscrição via interface do usuário continuou falhando, indicando um problema na plataforma da Meta.
-   **Decisão Estratégica:** O evento `message_echoes` é um "nice-to-have" para confirmação de entrega, mas não é essencial para a funcionalidade principal do nosso chatbot (receber e responder). Decidimos abandonar a perseguição a este evento e focar na lógica de negócios principal, que depende exclusivamente do evento `messages`.
