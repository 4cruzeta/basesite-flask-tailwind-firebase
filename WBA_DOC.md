# WBA_DOC.md: Diário de Bordo e Roteiro Estratégico da API do WhatsApp

## 1. Visão Geral da Missão (O Objetivo Final)

Conforme delineado no `EPIC.md`, a missão final é a fusão sinérgica entre a API de Negócios do WhatsApp (WBA) e um agente de IA customizado (RAG/DB). O objetivo é criar uma experiência de suporte ao cliente instantânea e sem atrito, permitindo que usuários finais conversem com um assistente virtual diretamente pelo WhatsApp para suporte técnico, reservas, e outras consultas.

## 2. Diário de Combate: A Saga da Conexão Inicial

O caminho para estabelecer uma conexão funcional com a API da Meta provou-se um campo minado de regras não documentadas e desafios técnicos.

*   **Batalha 1: A Muralha da Versão (`v19.0` vs `v24.0`)**
    *   **Problema:** O código inicial, baseado na `v19.0` da API, falhava silenciosamente ao receber webhooks.
    *   **Inteligência:** A análise do payload real da Meta revelou uma estrutura de dados diferente, pertencente à `v24.0`.
    *   **Ação:** O código foi refatorado em `routes.py` (para interpretar o novo payload) e `services.py` (para enviar mensagens usando a versão correta), tornando o sistema resiliente a diferentes tipos de notificação.

*   **Batalha 2: O Fantasma da Quebra de Linha (`Error 400`)**
    *   **Problema:** Mesmo com o código atualizado, as mensagens de "Eco" falhavam com um erro `400 Client Error: Bad Request`.
    *   **Inteligência:** O log de erro revelou um caractere de quebra de linha (`%0A`) na URL da API, corrompendo a requisição. A causa raiz era um segredo mal copiado no Secret Manager.
    *   **Ação:** O código foi blindado. A função `_access_secret_version` em `services.py` foi modificada para usar `.strip()`, limpando automaticamente quaisquer espaços em branco ou quebras de linha de todos os segredos recuperados.

*   **Batalha 3: A Barreira Burocrática Final (`Error #131030`)**
    *   **Problema:** Com o código tecnicamente perfeito, a API ainda retornava o erro `(#131030) Recipient phone number not in allowed list`.
    *   **Inteligência:** Após uma análise profunda, o Comandante identificou a verdadeira causa: o erro não se referia à lista de *números de teste*, mas à falta de uma *verificação de negócios* (CNPJ) na conta da Meta.
    *   **Conclusão:** A verificação de negócios não é um passo administrativo opcional, mas um **bloqueador funcional crítico** para qualquer funcionalidade além dos testes mais básicos.

## 3. O Pivô Estratégico (Plano de Ação Atual)

Dado que a verificação de negócios é um processo externo, um pivô estratégico foi decidido para evitar a paralisação do desenvolvimento.

*   **Frente 1: WhatsApp (WBA) - Em Espera Tática**
    *   **Status:** O código neste branch está **completo, estável e pronto para produção**.
    *   **Próxima Ação:** Aguardar a aprovação da verificação de negócios (CNPJ) pela Meta.

*   **Frente 2: Agente de IA (RAG/DB) - Iniciar Ofensiva**
    *   **Status:** Desenvolvimento a ser iniciado.
    *   **Próxima Ação:** Construir o agente de IA como um componente desacoplado.

## 4. Roteiro para a Fase de Desenvolvimento Desacoplado

*   **Passo 1: Criar o Cérebro (O Agente RAG/DB)**
    *   Desenvolver a lógica principal do agente de IA, capaz de receber uma string de texto (a pergunta do usuário) e, através de RAG, consultar uma base de dados (DB) para formular uma resposta coerente.

*   **Passo 2: Construir a Ponte (Interface Web Temporária)**
    *   Criar um novo `Blueprint` no Flask.
    *   Desenvolver uma página web simples (ex: `/rag-test`) que contenha um campo de formulário.
    *   O formulário enviará a pergunta do usuário para o agente RAG e exibirá a resposta na mesma página.
    *   **Objetivo:** Permitir o teste, depuração e refinamento contínuo do agente de IA de forma completamente independente do WhatsApp.

## 5. Roteiro para a Fusão Final (Pós-Verificação da Meta)

*   **Gatilho:** A Meta aprova a verificação de negócios da empresa.

*   **Ação:**
    1.  Navegar para `edcat_root/whatsapp/routes.py`.
    2.  Localizar a seção `--- ECHO LOGIC ---`.
    3.  Substituir a linha `response_text = f"Eco: {message_body}"` por uma chamada à função do agente RAG já construído e testado. Ex: `response_text = rag_agent.generate_response(message_body)`.
    4.  Realizar o deploy da versão atualizada.

*   **Resultado Final:** A sinergia RAG + WBA é alcançada, completando a missão original. O WhatsApp se torna a interface de conversação para o poderoso agente de IA.
