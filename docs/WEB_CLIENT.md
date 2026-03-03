# Estruturando o Módulo Web Client em Flask

Ao desenvolver uma aplicação Flask complexa, a organização do código é crucial. Uma das maiores dificuldades encontradas foi determinar a maneira correta de modularizar a aplicação, especificamente ao criar um novo "módulo" ou "pacote" para o cliente web (`web_client`).

## A Dificuldade: Blueprints, Rotas e o Padrão de Fábrica

A intuição inicial, baseada em outras arquiteturas, era que cada subdiretório (como `pages`, `api`, `web_client`) deveria conter seu próprio arquivo `routes.py`. A expectativa era que a aplicação principal, de alguma forma, "descobriria" e registraria esses `Blueprints` automaticamente.

Essa abordagem falhou. A investigação da estrutura, passando por `main.py` e depois `edcat_root/__init__.py`, revelou que a aplicação utiliza o padrão **Application Factory**. Não há nenhuma mágica de autodescoberta; todas as rotas e Blueprints são registrados explicitamente em um local central.

## A Solução: Registro Explícito no Centro de Comando

A arquitetura do projeto concentra a configuração no arquivo `edcat_root/__init__.py`, dentro da função `create_app()`. Este é o verdadeiro "centro de comando".

A solução correta envolveu os seguintes passos:

1.  **Criação do Blueprint Dedicado:** Foi criado um novo arquivo, `edcat_root/web_client/routes.py`. Dentro dele, um `Blueprint` chamado `web_client_bp` foi definido. Foi crucial especificar seu próprio `template_folder` para que ele procurasse os templates em seu próprio diretório, e não no diretório padrão da aplicação.

    ```python
    # edcat_root/web_client/routes.py
    from flask import Blueprint, render_template
    from ..views import login_required, admin_required

    web_client_bp = Blueprint(
        'web_client_bp',
        __name__,
        template_folder='templates' # Aponta para a pasta 'templates' dentro de 'web_client'
    )

    @web_client_bp.route("/chat")
    @login_required
    @admin_required
    def chat():
        return render_template("chat.html")
    ```

2.  **Registro Explícito na Fábrica:** O novo `web_client_bp` foi importado e registrado **explicitamente** dentro da função `create_app` em `edcat_root/__init__.py`.

    ```python
    # edcat_root/__init__.py

    def create_app():
        # ... (outras configurações)
        with app.app_context():
            # ... (outros imports)
            from .web_client.routes import web_client_bp # 1. IMPORTAR

            # ... (outros registros)
            # 2. REGISTRAR com um prefixo de URL
            app.register_blueprint(web_client_bp, url_prefix='/<lang_code>/client')

        return app
    ```

Essa abordagem centralizada, embora menos automática, é mais explícita, clara e manutenível, garantindo que todos os componentes da aplicação sejam carregados de forma previsível.
