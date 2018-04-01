from flask import current_app, Flask

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from .health_checks import health_check
from .errorhandlers import error_handlers


class FlaskChassis(object):
    def __init__(self, app: Flask = None):
        """
        :param app: A flask application
        """
        self.app = app

        # Register this extension with the flask app now (if it is provided)
        if app is not None:
            self.init_app(app)


    def init_app(self, app: Flask):
        # Set default configuration
        self._set_default_config(app)
        self._add_blueprints(app)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['flask-chassis'] = self
        
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)


    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'sqlite3_db'):
            ctx.sqlite3_db.close()


    def _add_blueprints(self, app: Flask):
        """
        Adds common blueprints to app
        """
        app.register_blueprint(health_check, url_prefix='/health')
        app.register_blueprint(error_handlers)


    @staticmethod
    def _set_default_config(app: Flask):
        """
        Sets the default configuration
        """
        # app.config.setdefault('EXAMPLE', 'value')
        pass
