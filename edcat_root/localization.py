from flask import session, request

def get_locale():
    """
    Determines the best language for the user, checking the session,
    then the browser's Accept-Language header, and finally falling back to pt_BR.
    """
    if 'language' in session:
        return session['language']
    
    # Fallback to browser's preferred language or default
    return request.accept_languages.best_match(['pt_BR', 'en_US']) or 'pt_BR'
