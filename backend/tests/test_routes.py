"""
Tests for API routes
"""
import pytest
import json
from app import create_app


@pytest.fixture
def app():
    """Create and configure a test app"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'message' in data


class TestHelloEndpoint:
    """Test hello endpoint"""
    
    def test_hello(self, client):
        response = client.get('/api/hello')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data


class TestEchoEndpoint:
    """Test echo endpoint"""
    
    def test_echo_post(self, client):
        test_data = {'test': 'data', 'number': 123}
        response = client.post('/api/echo', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['echo'] == test_data
    
    def test_echo_no_data(self, client):
        response = client.post('/api/echo',
                              data='null',
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['echo'] is None


class TestProcessArticleEndpoint:
    """Test article processing endpoint"""
    
    def test_process_article_valid_data(self, client):
        article_data = {
            'companyDomain': 'example.com',
            'articleTitle': 'AI Technology Trends',
            'article': '''
                Artificial intelligence is rapidly transforming industries across the globe. 
                Machine learning algorithms are becoming more sophisticated and capable of 
                handling complex tasks. Companies are investing heavily in AI research and 
                development to stay competitive. Natural language processing has enabled 
                better human-computer interactions. The future of technology will be 
                heavily influenced by artificial intelligence advancements.
            '''
        }
        
        response = client.post('/api/process-article',
                              data=json.dumps(article_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Check main structure
        assert 'metadata' in data
        assert 'content' in data
        assert 'n8n_payload' in data
        
        # Check metadata
        metadata = data['metadata']
        assert metadata['company_domain'] == 'example.com'
        assert metadata['article_title'] == 'AI Technology Trends'
        assert 'processed_at' in metadata
        assert 'article_length' in metadata
        assert 'word_count' in metadata
        
        # Check content processing
        content = data['content']
        assert content['title'] == 'AI Technology Trends'
        assert len(content['body']) > 0
        assert 'summary' in content
        assert isinstance(content['keywords'], list)
        assert isinstance(content['phrases'], list)
        
        # Check n8n payload
        n8n_payload = data['n8n_payload']
        assert 'webhook_data' in n8n_payload
        webhook_data = n8n_payload['webhook_data']
        assert webhook_data['domain'] == 'example.com'
        assert webhook_data['title'] == 'AI Technology Trends'
    
    def test_process_article_missing_fields(self, client):
        incomplete_data = {
            'companyDomain': 'example.com',
            'articleTitle': 'Title'
            # Missing article field
        }
        
        response = client.post('/api/process-article',
                              data=json.dumps(incomplete_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required fields' in data['error']
    
    def test_process_article_empty_fields(self, client):
        empty_data = {
            'companyDomain': '',
            'articleTitle': '   ',
            'article': 'Valid content with sufficient length for processing tests'
        }
        
        response = client.post('/api/process-article',
                              data=json.dumps(empty_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_process_article_short_content(self, client):
        short_data = {
            'companyDomain': 'example.com',
            'articleTitle': 'Short Article',
            'article': 'Too short'
        }
        
        response = client.post('/api/process-article',
                              data=json.dumps(short_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'too short' in data['error'].lower()
    
    def test_process_article_no_json(self, client):
        response = client.post('/api/process-article',
                              data='not json',
                              content_type='application/json')
        
        # Flask returns 400 or 500 for malformed JSON - both are acceptable
        assert response.status_code in [400, 500]
    
    def test_process_article_no_data(self, client):
        response = client.post('/api/process-article',
                              data='null',
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_process_article_malformed_json(self, client):
        response = client.post('/api/process-article',
                              data='{"invalid": json}',
                              content_type='application/json')
        
        # Flask returns 400 or 500 for malformed JSON - both are acceptable  
        assert response.status_code in [400, 500]


class TestAPIIntegration:
    """Integration tests for the entire API"""
    
    def test_full_workflow(self, client):
        """Test a complete workflow from health check to article processing"""
        
        # 1. Check API health
        health_response = client.get('/api/health')
        assert health_response.status_code == 200
        
        # 2. Test echo functionality
        echo_data = {'test': 'integration'}
        echo_response = client.post('/api/echo',
                                   data=json.dumps(echo_data),
                                   content_type='application/json')
        assert echo_response.status_code == 200
        
        # 3. Process a real article
        article_data = {
            'companyDomain': 'techcorp.com',
            'articleTitle': 'The Future of Artificial Intelligence',
            'article': '''
                The field of artificial intelligence has seen remarkable growth in recent years. 
                Machine learning algorithms are now capable of processing vast amounts of data 
                and identifying complex patterns. Deep learning networks have revolutionized 
                image recognition and natural language processing. Companies across industries 
                are adopting AI technologies to improve efficiency and drive innovation. 
                As we look to the future, artificial intelligence will continue to transform 
                how we work, communicate, and solve complex problems.
            '''
        }
        
        process_response = client.post('/api/process-article',
                                      data=json.dumps(article_data),
                                      content_type='application/json')
        
        assert process_response.status_code == 200
        
        processed_data = json.loads(process_response.data)
        
        # Verify the processed data contains AI-related keywords
        keywords = processed_data['content']['keywords']
        phrases = processed_data['content']['phrases']
        
        # Should contain AI-related terms
        ai_terms_found = any(
            term in ' '.join(keywords + phrases).lower() 
            for term in ['artificial', 'intelligence', 'machine', 'learning', 'deep']
        )
        assert ai_terms_found
        
        # Verify n8n payload structure
        n8n_data = processed_data['n8n_payload']['webhook_data']
        assert n8n_data['domain'] == 'techcorp.com'
        assert len(n8n_data['keywords']) > 0
        assert len(n8n_data['phrases']) > 0
    
    def test_error_handling_integration(self, client):
        """Test error handling across different endpoints"""
        
        # Test various error conditions
        error_cases = [
            # Missing data
            {},
            # Invalid domain
            {'companyDomain': 'x', 'articleTitle': 'Title', 'article': 'Content'},
            # Short article
            {'companyDomain': 'test.com', 'articleTitle': 'Title', 'article': 'Short'},
        ]
        
        for error_case in error_cases:
            response = client.post('/api/process-article',
                                  data=json.dumps(error_case),
                                  content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert len(data['error']) > 0