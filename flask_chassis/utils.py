# pylint: disable=E0401

from flask import current_app as app


def _get_chassis():
    try:
        return app.extensions['flask-chassis']
    except KeyError:
        raise RuntimeError("You must initialize the chassis with this flask "
                           "application before using this method")


def get_redis():
    # Imported here to allow services that don't require redis to avoid installing
    # redis package
    from redis import StrictRedis
    return StrictRedis(connection_pool=_get_chassis().redis_pool)


def get_db():
    return _get_chassis().db