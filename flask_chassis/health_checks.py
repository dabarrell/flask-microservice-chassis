import datetime
import subprocess
from flask import Blueprint, jsonify, current_app as app

health_check = Blueprint('health_check', __name__)


@health_check.route('/ping')
def ping():
    rtn = {
        'pong': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify(rtn)


@health_check.route('/status')
def status():
    rtn = {
        'name': app.config['SERVICE_NAME'],
        'commit': get_git_revision_hash()
    }
    return jsonify(rtn)


def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()