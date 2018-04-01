import datetime
from flask import Blueprint, jsonify

health_check = Blueprint('health_check', __name__)


@health_check.route('/ping')
def ping():
    rtn = {
        "pong": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify(rtn)