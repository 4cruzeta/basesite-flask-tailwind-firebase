# Projeto Base: Flask com Tailwind CSS

Este é um projeto inicial que utiliza Flask para o back-end e Tailwind CSS para o front-end. O objetivo é criar uma base sólida e bem documentada para futuros desenvolvimentos.

## Roteiro de Criação do Projeto

Este documento serve como um guia passo a passo de como este projeto foi configurado desde o início.

### 1. Configuração do Ambiente (`dev.nix`)

O primeiro passo foi configurar o ambiente de desenvolvimento no arquivo `.idx/dev.nix` para instalar todas as ferramentas necessárias:

```nix
{ pkgs, ... }: {
  packages = [
    pkgs.python3
    pkgs.uv
    pkgs.nodejs_22
    pkgs.gettext
  ];
}
```

### 2. Ambiente Virtual e Dependências

Com o ambiente base pronto, criamos um ambiente virtual Python e instalamos as dependências do projeto.

**Ambiente virtual:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Dependências Python (com `uv`):**
```bash
uv pip install flask
```

**Dependências Node.js (com `npm`):**
```bash
npm install tailwindcss @tailwindcss/cli
```

### 3. Estrutura do Projeto

Adotamos o padrão **"Application Factory"** para organizar o código Flask, tornando-o mais escalável e organizado. A estrutura de diretórios ficou assim:

```
.
├── .gitignore
├── .idx/
│   └── dev.nix
├── README.md
├── edcat_root/
│   ├── __init__.py       # Fábrica que cria a aplicação Flask
│   ├── main.py           # Ponto de entrada que executa a aplicação
│   ├── views.py          # Módulo para as rotas (views)
│   ├── pages/
│   │   └── templates/
│   │       └── index.html  # Templates HTML
│   └── static/
│       └── css/
│           └── output.css  # CSS gerado pelo Tailwind
├── requirements.txt      # Dependências Python
└── tailwind.config.js    # Configuração do Tailwind CSS
```

### 4. A Saga do Deploy: Do Local à Nuvem com Cloud Run

Nosso objetivo era fazer o deploy da aplicação, mas o caminho se mostrou mais complexo do que o esperado. Aqui está a história de como superamos os desafios.

#### O Desafio do Tailwind 4 e o Docker

O primeiro obstáculo foi garantir que nosso processo de build do CSS, usando a versão mais recente do Tailwind CSS 4, funcionasse de forma confiável dentro de um contêiner Docker.

A solução foi adotar uma abordagem de **build multi-estágio (multi-stage build)** no nosso `Dockerfile`:
- **Estágio 1 (Builder):** Criamos um contêiner temporário com Node.js apenas para instalar as dependências de front-end e compilar o CSS.
- **Estágio 2 (Final):** Criamos um contêiner Python limpo e enxuto. A única coisa que trouxemos do primeiro estágio foi o arquivo `style.css` já pronto. O resultado foi uma imagem Docker leve, segura e otimizada para produção.

#### O Mistério do "Service Unavailable" e o Mísero Ponto

Mesmo com o build bem-sucedido, o Cloud Run nos presenteava com um frustrante "Service Unavailable". A aplicação estava sendo construída, mas não iniciava na nuvem. Após uma investigação minuciosa, o culpado foi encontrado em `main.py`: um único ponto.

A linha `from .views import views` (uma importação relativa) funcionava perfeitamente no ambiente de desenvolvimento local, mas quebrava o Gunicorn (o servidor usado em produção). Ao alterá-la para uma importação absoluta (`from views import views`), a aplicação finalmente pôde ser iniciada, resolvendo o mistério e colocando nosso site no ar. Uma lição valiosa: o que funciona em desenvolvimento nem sempre funciona em produção.

### 5. Traduções

```bash
pybabel extract -F babel.cfg -o edcat_root/translations/messages.pot .
pybabel init -i edcat_root/translations/messages.pot -d edcat_root/translations -l en_US
pybabel init -i edcat_root/translations/messages.pot -d edcat_root/translations -l pt_BR
# Efetuar as traduções nos arquivos .po
pybabel compile -d edcat_root/translations
```

### 6. Notas de Desenvolvimento

> O web preview não funciona. Por alguma razão de mal relacionamento entre os garçons e os cozinheiros malvados, você pede lagosta ao ponto, mas eles te entregam sardinha crua.

Carregue o Web preview com Hard Restart e abra o External Website para conseguir ver as alterações em suas páginas.

