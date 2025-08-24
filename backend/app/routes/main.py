from flask import jsonify, request
from . import api_bp

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@api_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from Flask backend!'})

@api_bp.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({'echo': data})