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

### 4. Próximos Passos

- [ ] Continuar o desenvolvimento das funcionalidades.
- [ ] Configurar o deploy no Firebase App Hosting.
- [ ] Detalhar a configuração do Tailwind.

### 5. Traduções:

pybabel extract -F babel.cfg -o edcat_root/translations/messages.pot .

pybabel extract -F babel.cfg -o edcat_root/translations/messages.pot --no-wrap .

pybabel init -i edcat_root/translations/messages.pot -d edcat_root/translations -l en_US

pybabel init -i edcat_root/translations/messages.pot -d edcat_root/translations -l pt_BR

### Efetuar as traduções

### Compilar as traduções
pybabel compile -d edcat_root/translations

export FLASK_APP=edcat_root/main.py && pybabel compile -d edcat_root/translations


### O web preview não funciona. Por alguma razão de mal relacionamento entre os garçons e os cozinheiros malvados, você pede lagosta ao ponto, mas eles te entregam sardinha crua.

Carregue o Web preview com Hard Restart e abra o External Website para conseguir ver as alterações em suas páginas.

