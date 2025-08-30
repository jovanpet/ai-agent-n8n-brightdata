from flask import jsonify, request
import requests
from . import api_bp
from ..utils.data_formatter import create_n8n_payload, validate_article_data, sanitize_input_data


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})


@api_bp.route('/hello', methods=['GET'])
def hello():
    """Simple hello endpoint"""
    return jsonify({'message': 'Hello from Flask backend!'})


@api_bp.route('/echo', methods=['POST'])
def echo():
    """Echo endpoint for testing"""
    data = request.get_json()
    return jsonify({'echo': data})


@api_bp.route('/process-article', methods=['POST'])
def process_article():
    """
    Process article data and prepare it for n8n consumption
    
    Expected JSON payload:
    {
        "companyDomain": "example.com",
        "articleTitle": "Sample Article",
        "article": "Full article content..."
    }
    """
    try:
        data = request.get_json()
        
        # Handle JSON parsing errors
        if data is None and request.data:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        # Validate input data
        is_valid, error_message = validate_article_data(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Sanitize and extract data
        clean_data = sanitize_input_data(data)
        
        # Create processed payload
        processed_data = create_n8n_payload(
            clean_data['company_domain'],
            clean_data['article_title'],
            clean_data['article']
        )
        
        # Send to n8n webhook
        n8n_webhook_url = "https://cloutboi.app.n8n.cloud/webhook-test/590a34c2-2b79-4650-953b-a2267c392e2a"
        
        try:
            response = requests.post(
                n8n_webhook_url,
                json=processed_data["payload"],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'message': 'Article processed and sent to n8n successfully',
                    'n8n_response': response.json() if response.content else None,
                    'processed_data': processed_data
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': f'n8n webhook failed with status {response.status_code}',
                    'processed_data': processed_data
                }), 200
                
        except requests.exceptions.RequestException as e:
            return jsonify({
                'success': False,
                'message': f'Failed to send to n8n: {str(e)}',
                'processed_data': processed_data
            }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500