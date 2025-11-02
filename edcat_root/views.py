from flask import Blueprint, render_template

views = Blueprint('views', __name__)

# Esta é a sua página principal. Agora ela responde no final do URL com prefixo de idioma.
# Ex: /pt_BR/home
# A função agora aceita o argumento 'lang_code' que o Flask passa a partir da URL.
@views.route('/home')
def home(lang_code):
    return render_template("index.html")

# A rota antiga @views.route('/language/<lang>') foi removida.
# A seleção de idioma agora é feita exclusivamente pelo prefixo na URL,
# uma abordagem mais limpa e robusta que resolve os problemas de cache.
