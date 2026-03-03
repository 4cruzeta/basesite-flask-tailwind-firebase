# Missão: Plataforma de Assistente de IA (Web Client)

**Status:** Em Andamento

**Objetivo:** Construir uma interface web própria para o nosso `rag_agent`, superando as limitações de custo e memória da API do WhatsApp. A interface será similar a clientes de LLM modernos, com histórico de conversas e interação em tempo real.

---

## Plano de Batalha Detalhado

### Frente 1: A Interface (Frontend)

*   **Objetivo:** Criar a estrutura visual e interativa do nosso cliente de chat.
*   **Tarefas:**
    -   [ ] **1.1: Estrutura Flask:** Criar um novo Blueprint (`web_client_bp`) para servir a interface web.
    -   [ ] **1.2: Esqueleto HTML:** Desenvolver o arquivo `index.html` com a estrutura principal:
        -   Um contêiner para a lista de conversas (menu lateral).
        -   Um contêiner para a janela de chat ativa (perguntas e respostas).
        -   Um formulário de input para o usuário digitar a mensagem.
    -   [ ] **1.3: Estilização Inicial (CSS):** Aplicar CSS básico para organizar o layout de duas colunas e garantir a usabilidade inicial.
    -   [ ] **1.4: Lógica do Cliente (JavaScript):** Implementar o script para:
        -   Capturar o envio do formulário de mensagem.
        -   Enviar a mensagem do usuário para o backend via API (`fetch`).
        -   Receber a resposta da IA e adicioná-la à janela de chat.
        -   Limpar o campo de input após o envio.

### Frente 2: A Ponte (Backend API)

*   **Objetivo:** Criar um canal de comunicação entre o frontend e o nosso cérebro de IA.
*   **Tarefas:**
    -   [ ] **2.1: Endpoint da API:** No `web_client_bp`, criar a rota `/api/chat` (método `POST`).
    -   [ ] **2.2: Integração com o Agente:** Fazer com que o endpoint `/api/chat` receba o JSON do frontend, extraia a mensagem do usuário e a passe para a função `rag_agent.generate_response()`.
    -   [ ] **2.3: Formato da Resposta:** Garantir que o endpoint retorne a resposta do agente em um formato JSON claro (ex: `{"response": "texto da IA"}`).

### Frente 3: A Memória (MVP de Armazenamento)

*   **Objetivo:** Implementar um sistema simples para persistir e recuperar o histórico das conversas.
*   **Tarefas:**
    -   [ ] **3.1: Design da Persistência:** Decidir sobre o método de armazenamento para o MVP (ex: arquivos JSON no servidor, um para cada conversa).
    -   [ ] **3.2: Lógica de Armazenamento:** Implementar funções para:
        -   Criar um novo arquivo de conversa.
        -   Anexar novas trocas (pergunta do usuário + resposta da IA) ao arquivo de uma conversa existente.
    -   [ ] **3.3: Lógica de Recuperação:** Implementar funções no backend para:
        -   Listar todas as conversas existentes para popular o menu lateral.
        -   Carregar o histórico completo de uma conversa específica quando o usuário a seleciona.

