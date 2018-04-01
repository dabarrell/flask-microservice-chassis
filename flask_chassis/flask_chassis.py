import os
import logging
import sys
from flask import current_app, Flask

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from .health_checks import health_check
from .errorhandlers import error_handlers


class FlaskChassis(object):
    """
    TODO: Chassis configuration - flags for whether redis/sql etc is used, whether \
    to register error handlers
    """

    external_config_checked: bool = False
    config_finalised: bool = False
    _redis_pool = None
    _db = None

    def __init__(self, app: Flask = None, check_external: bool = False):
        """
        :param app: A flask application
        """
        self.app = app

        # Register this extension with the flask app now (if it is provided)
        if app is not None:
            self.init_app(app, check_external)


    def init_app(self, app: Flask, check_external: bool = False):
        """Initialises extension on app
        
        Args:
            app (Flask): Flask app
            check_external (bool, optional): Defaults to False. Whether or not to check external config file on init.
        """


        # Set default configuration
        self._set_default_config(app)
        self._register_functions(app)
        self._add_blueprints(app)

        if check_external:
            self.load_external_config()

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
        # if hasattr(ctx, 'sqlite3_db'):
        #     ctx.sqlite3_db.close()


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
        app.config.setdefault('STDOUT_LOGGING_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    
    def _register_functions(self, app: Flask):
        """
        Registers callbacks used by this extension
        """
        @app.before_first_request
        def check_configuration():
            if not self.external_config_checked:
                app.logger.warn('External configuration file not checked. ' +
                'Please ensure you run FlaskChassis.load_external_config(), ' +
                'or set check_external=True in constructor.')
            
            if not self.config_finalised:
                app.logger.warn('Configuration not finalised. ' +
                'Please ensure you run FlaskChassis.finalise_config().')

            # This list contains all the config variables that must be present
            required_config_variables = [
                'SERVICE_NAME', 'DEBUG'
            ]

            missing_vars = [v for v in required_config_variables if v not in app.config]
            if len(missing_vars) > 0:
                msg = 'The following config variables required by chassis are missing: ' + str(missing_vars)
                app.logger.error(msg)
                raise Exception(msg)
            else:
                app.logger.debug('All config variables required by chassis present')

    
    @staticmethod
    def _configure_logging(app: Flask):
        # Std out
        # remove existing stream handlers
        app.logger.handlers = [h for h in app.logger.handlers if not isinstance(h, logging.StreamHandler)]
        handler = logging.StreamHandler(stream=sys.stdout)

        if app.config['DEBUG']:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)

        formatter = logging.Formatter(app.config['STDOUT_LOGGING_FORMAT'])
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)


    def finalise_config(self):
        """
        Finalises config to be run after service-specific config. This ensures
        that configurations common to all services are not over-ridden.
        """
        if not self.external_config_checked:
            self.load_external_config()
        
        self._configure_logging(self.app)
        self.config_finalised = True


    def load_external_config(self):
        """
        Loads external config file if path supplied by environmental variable.
        Call this after loading config in microservice to give precendence to
        file at 'EXT_CONFIG_PATH'.
        """
        config_path = os.getenv('EXT_CONFIG_PATH')
        if config_path is not None:
            self.app.config.from_pyfile(config_path, silent=False)

        self.external_config_checked = True
    

    @property
    def redis_pool(self):
        if self._redis_pool is None:
            from redis import ConnectionPool
            host = self.app.config['REDIS_HOSTNAME']
            port = self.app.config['REDIS_PORT']
            db_num = self.app.config['REDIS_DB']
            self._redis_pool = ConnectionPool(host=host, port=port, db=db_num)

        return self._redis_pool
    
    @property
    def db(self):
        if self._db is None:
            from flask_sqlalchemy import SQLAlchemy
            self._db = SQLAlchemy(self.app)
        return self._db


