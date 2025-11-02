import os
from flask import Flask, request, g, redirect, url_for
from flask_babel import Babel, gettext as _
from views import views

# --- App Initialization and Configuration ---
app = Flask(__name__, template_folder='pages/templates', static_folder='static')
app.config['SECRET_KEY'] = 'dev_secret_key_for_session_stability'
# Define supported languages in a dictionary for easy access
app.config['LANGUAGES'] = {
    'en_US': 'English',
    'pt_BR': 'Português'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'pt_BR'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')


# --- Babel Initialization and Locale Selection ---
def get_locale():
    """
    Seleciona o idioma para a requisição, com base na sua ideia.
    1. A partir do `lang_code` na URL (ex: /pt_BR/).
    2. Se não houver, usa a preferência do navegador.
    """
    # Se um idioma válido estiver na URL (armazenado no objeto 'g'), use-o.
    if g.get('lang_code') and g.lang_code in app.config['LANGUAGES']:
        return g.lang_code
    # Caso contrário, volte para o método antigo de verificar o navegador.
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

babel = Babel(app, locale_selector=get_locale)


# --- Request Handlers for Language Code ---

@app.before_request
def set_lang_code():
    """
    Extrai o `lang_code` da URL antes de cada requisição e o armazena em 'g'.
    O objeto 'g' do Flask é um espaço temporário para dados da requisição atual.
    """
    if 'lang_code' in request.view_args and request.view_args['lang_code'] in app.config['LANGUAGES']:
        g.lang_code = request.view_args['lang_code']
    else:
        g.lang_code = None # Nenhum idioma válido encontrado na URL

@app.route('/')
def root_redirect():
    """
    Esta é a implementação central da sua ideia.
    Redireciona o usuário da raiz (/) para a URL com seu idioma preferido.
    Ex: `seusite.com/` -> `seusite.com/pt_BR/home`
    """
    # Determina o melhor idioma a partir do cabeçalho do navegador
    lang_code = request.accept_languages.best_match(app.config['LANGUAGES'].keys())
    
    # Se não encontrar, usa o nosso padrão.
    if lang_code is None:
        lang_code = app.config['BABEL_DEFAULT_LOCALE']

    # Redireciona para a view 'home' (página inicial), passando o código do idioma.
    # ASSUMINDO que sua view principal se chama 'home'.
    return redirect(url_for('views.home', lang_code=lang_code))


# --- Register Blueprints with the Language Prefix ---
# Agora, todas as rotas em 'views.py' serão prefixadas com /<lang_code>/.
app.register_blueprint(views, url_prefix='/<lang_code>')


# --- Template Context Processor ---
@app.context_processor
def inject_gettext():
    """Passa a função de tradução para os templates."""
    return dict(_=_)

# O hook 'after_request' para forçar 'no-cache' não é mais necessário.
# A sua abordagem de URL é naturalmente amigável ao cache e resolve o problema
# na raiz. Removê-lo permite que o Firebase faça seu trabalho corretamente.

# --- Main Execution ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)