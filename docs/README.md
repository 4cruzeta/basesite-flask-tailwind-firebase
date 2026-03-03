
# EdCat - Roteiro de Instalação no Firebase

Este guia descreve o processo para configurar e implantar a aplicação EdCat do zero em um novo projeto do Google Cloud e Firebase.

## Pré-requisitos

- **Conta do Google Cloud:** Com um projeto criado e faturamento ativado.
- **Ferramentas de Linha de Comando:**
  - `gcloud` (Google Cloud SDK)
  - `firebase` (Firebase CLI)
- **Git:** Para clonar o repositório.

---

## Passo 1: Configuração do Projeto Google Cloud & Firebase

1.  **Crie um Projeto:**
    - Acesse o [Console do Google Cloud](https://console.cloud.google.com/) e crie um novo projeto (ex: `meu-novo-edcat`). Anote o **Project ID**.

2.  **Ative as APIs Essenciais:**
    - No console do seu projeto, ative as seguintes APIs:
      - **Cloud Build API** (para construir o contêiner)
      - **Cloud Run Admin API** (para implantar o serviço)
      - **Secret Manager API** (para gerenciar segredos)
      - **Identity and Access Management (IAM) API**

3.  **Vincule o Firebase ao Projeto:**
    - Acesse o [Console do Firebase](https://console.firebase.google.com/).
    - Clique em "Adicionar projeto" e selecione seu projeto Google Cloud existente.

4.  **Configure os Serviços do Firebase:**
    - **Authentication:**
      - Vá para a seção "Authentication" -> "Sign-in method".
      - Ative o provedor "E-mail/senha".
    - **Firestore:**
      - Vá para a seção "Firestore Database".
      - Crie um banco de dados em modo de **Produção**.

---

## Passo 2: Clonar e Configurar o Repositório Local

1.  **Clone o projeto:**
    ```bash
    git clone <URL_DO_SEU_REPOSITÓRIO>
    cd <NOME_DO_REPOSITÓRIO>
    ```

2.  **Inicialize o Firebase no projeto local:**
    - Faça login no Firebase:
      ```bash
      firebase login
      ```
    - Configure o projeto para usar o seu Project ID:
      ```bash
      firebase use SEU_PROJECT_ID
      ```

3.  **Faça login no gcloud:**
    - Autentique a CLI `gcloud` para interagir com os serviços do Google Cloud.
      ```bash
      gcloud auth login
      gcloud auth application-default login
      ```

---

## Passo 3: Gerenciamento de Segredos (Secret Manager)

A aplicação requer que os seguintes segredos sejam criados no Google Secret Manager. Substitua `SEU_PROJECT_ID` nos comandos.

1.  **`SECRET_KEY` do Flask:**
    - Gere uma chave segura (ex: `openssl rand -hex 32`).
    - Crie o segredo:
      ```bash
      echo "SUA_CHAVE_SEGURA_AQUI" | gcloud secrets create SECRET_KEY --project=SEU_PROJECT_ID --data-file=-
      ```

2.  **`ADMIN_USERS`:**
    - Lista de e-mails de administradores, separados por vírgula.
      ```bash
      echo "admin1@email.com,admin2@email.com" | gcloud secrets create ADMIN_USERS --project=SEU_PROJECT_ID --data-file=-
      ```

3.  **`firebase-client-config`:**
    - No Console do Firebase, vá para "Configurações do Projeto" (ícone de engrenagem).
    - Em "Seus apps", crie um novo **App da Web**.
    - Copie o objeto de configuração `firebaseConfig` (formato JSON).
    - Crie o segredo (o JSON deve estar em uma única linha):
      ```bash
      echo '{"apiKey": "...", "authDomain": "...", ...}' | gcloud secrets create firebase-client-config --project=SEU_PROJECT_ID --data-file=-
      ```

4.  **`firebase-server-config` (Conta de Serviço):**
    - No Console do Firebase, vá para "Configurações do Projeto" -> "Contas de serviço".
    - Clique em "Gerar nova chave privada". Isso fará o download de um arquivo JSON.
    - Crie o segredo a partir do arquivo baixado:
      ```bash
      gcloud secrets create firebase-server-config --project=SEU_PROJECT_ID --data-file="/caminho/para/o/arquivo-baixado.json"
      ```

---

## Passo 4: Deploy em Produção

1.  **Atualize o `service.yaml`:**
    - Abra o arquivo `service.yaml`.
    - No campo `spec.template.spec.containers[0].env`, altere o `value` de `GOOGLE_CLOUD_PROJECT` para o seu **Project ID**.

2.  **Construa e Envie a Imagem do Contêiner:**
    - Este comando usa o `Dockerfile` para construir a imagem e a envia para o Google Container Registry.
      ```bash
      gcloud builds submit --tag gcr.io/SEU_PROJECT_ID/edcat-container
      ```

3.  **Implante o Serviço no Cloud Run:**
    - Este comando usa o `service.yaml` para configurar e implantar o contêiner no Cloud Run.
      ```bash
      gcloud run services replace service.yaml --region us-east4
      ```

4.  **Configure o Firebase Hosting (`firebase.json`):**
    - Certifique-se de que o `firebase.json` está configurado para redirecionar o tráfego para o seu serviço do Cloud Run. O `serviceId` deve ser o nome definido em `service.yaml` (`edcat-container`).

5.  **Implante no Firebase Hosting:**
    - Finalmente, implante as regras de hospedagem.
      ```bash
      firebase deploy --only hosting
      ```

Seu aplicativo agora está no ar, com o front-end servido pelo Firebase Hosting e o back-end executando de forma segura no Cloud Run.
