# EdCat - Seu Editor de Catálogos Online

## 1. Visão Geral

EdCat é uma aplicação web construída com Flask, projetada para ser um editor de catálogos de produtos simples e eficiente. A aplicação utiliza Tailwind CSS para a estilização e Flask-Babel para internacionalização (i18n), com traduções para Português do Brasil (pt_BR) e Inglês (en_US).

Este `README.md` serve como um diário de bordo e um guia de desenvolvimento, documentando os desafios encontrados e as soluções implementadas durante a jornada de configuração do ambiente de desenvolvimento e deploy no Firebase.

## 2. Estrutura do Projeto

```
.
├── .idx/              # Configuração do ambiente de desenvolvimento IDX
│   └── dev.nix        # Arquivo Nix para definir pacotes e configurações
├── devserver.sh       # Script para iniciar o servidor de desenvolvimento local
├── edcat_root/        # Raiz da aplicação Flask
│   ├── main.py        # Ponto de entrada da aplicação, configuração do Flask e Babel
│   ├── views.py       # Definição das rotas (Blueprints) da aplicação
│   ├── babel.cfg      # Configuração para extração de textos do Flask-Babel
│   ├── requirements.txt # Dependências Python
│   ├── static/        # Arquivos estáticos (CSS, JS, imagens)
│   └── translations/  # Arquivos de tradução gerados pelo Babel
├── Dockerfile         # Define o contêiner de produção para o Firebase
├── firebase.json      # Configuração do Firebase Hosting
└── ...
```

## 3. A Saga do Deploy no Firebase

Nosso objetivo era fazer o deploy da aplicação, mas o caminho se mostrou mais complexo do que o esperado. Aqui está a história de como superamos os desafios.

#### O Desafio do Tailwind 4 e o Docker

A solução foi adotar uma abordagem de **build multi-estágio (multi-stage build)** no nosso `Dockerfile` para gerar o CSS e manter a imagem final leve e segura.

#### A Solução do "Mísero Ponto"

O impasse entre o ambiente local e o de produção foi resolvido ajustando o script `devserver.sh`, permitindo que a importação absoluta `from views import views` funcionasse em ambos os lugares.

## 4. Arquitetura de Roteamento no Firebase

Nossa configuração de `rewrites` no `firebase.json` representa a **Filosofia Monolítica**: o Firebase Hosting encaminha **100% das requisições** para o nosso contêiner no Cloud Run, que é o cérebro da operação.

Outro ponto vital é a seção `headers`, que instrui o cache do Firebase a criar versões diferentes da página para cada idioma, resolvendo o problema de traduções que não funcionavam em produção.

## 5. Traduções

Os comandos para gerenciar as traduções com o Flask-Babel são:

```bash
# Extrair, inicializar e compilar traduções
pybabel extract -F babel.cfg -o edcat_root/translations/messages.pot .
pybabel init -i edcat_root/translations/messages.pot -d edcat_root/translations -l pt_BR
pybabel compile -d edcat_root/translations
```

## 6. Notas de Desenvolvimento

#### O Garçom, o Cozinheiro e as Traduções (Mistério Resolvido)

O problema de o site aparecer em inglês no ambiente de produção foi resolvido com duas ações:

1.  **No Código (`main.py`):** Garantimos um idioma padrão explícito com a linha `return request.accept_languages.best_match(['pt_BR', 'en_US']) or 'pt_BR'`.
2.  **Na Configuração (`firebase.json`):** Adicionamos o cabeçalho `Vary: Accept-Language` para garantir que o cache do Firebase sirva a versão correta da página para cada idioma.

## 7. Próximos Passos (TODO)

A batalha foi longa e o cansaço é justificado. O último deploy não funcionou como esperado, e a razão está no log de deploy:

`i deploying hosting`

Isso indica que, apesar do comando `firebase deploy`, apenas a parte do "Hosting" foi atualizada. A nossa aplicação no Cloud Run (o "cozinheiro") **não foi atualizada** com o `main.py` corrigido. A causa mais provável é uma falha de autenticação silenciosa que impediu o CLI de gerenciar o Cloud Run.

**Plano para amanhã:**

1.  **Renovar a Autenticação:** A primeira ação será garantir que estamos totalmente autenticados com o Google Cloud. Executaremos o seguinte comando no terminal:
    ```bash
    gcloud auth login --update-adc
    ```
2.  **Deploy Completo e Verificado:** Com a autenticação garantida, executaremos o comando de deploy completo novamente:
    ```bash
    firebase deploy
    ```
    Vamos inspecionar o log de saída para confirmar que ele está, de fato, criando e enviando a nova imagem do contêiner para o Cloud Run.
3.  **Verificação Final:** Testaremos o site em produção, em uma janela anônima, para confirmar que o idioma é carregado corretamente em português.

A solução está implementada e o plano está traçado. Amanhã, a vitória é certa.
