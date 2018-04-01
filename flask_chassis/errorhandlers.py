from flask import Blueprint, request, jsonify

error_handlers = Blueprint('error_handlers', __name__)


@error_handlers.app_errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@error_handlers.app_errorhandler(400)
def external_error(error=None):
    message = {
            'status': 400,
            'message': error.description,
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp

@error_handlers.app_errorhandler(500)
def internal_error(error=None):
    message = {
            'status': 500,
            'message': 'Internal error: ' + error.description,
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp
