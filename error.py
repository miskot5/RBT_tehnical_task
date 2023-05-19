import traceback
from flask import Blueprint, jsonify
from marshmallow import ValidationError

error_bp = Blueprint("Errors", __name__)


@error_bp.app_errorhandler(ValueError)
def handle_invalid_data(error):
    # print(traceback.format_exc())
    return jsonify({"message": "Incorrect format data", "additional data": error}), 400


@error_bp.app_errorhandler(ValidationError)
def handle_invalid_data(error):
    print(traceback.format_exc())
    return jsonify({"message": "Incorrect format data", "additional data": error.messages}), 400
