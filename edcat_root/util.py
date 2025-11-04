
from flask import url_for, request
from flask_babel import gettext as _

def inject_context_processors(app):
    """
    Injects context processors into the Flask app.
    These functions are available in all templates.
    """

    @app.context_processor
    def inject_language_switcher():
        """
        Creates a function `change_lang_url` that generates a URL for the current
        page in a different language, preserving the current endpoint and arguments.
        """
        def change_lang_url(lang_code):
            if request.endpoint:
                view_args = request.view_args.copy()
                view_args['lang_code'] = lang_code
                try:
                    return url_for(request.endpoint, **view_args)
                except Exception:
                    # Fallback if URL building fails
                    return url_for('views.home', lang_code=lang_code)
            # Fallback for pages without a clear endpoint (like 404)
            return url_for('views.home', lang_code=lang_code)

        return dict(change_lang_url=change_lang_url)

    @app.context_processor
    def inject_gettext():
        """Injects the gettext function `_` for translations into templates."""
        return dict(_=_)
