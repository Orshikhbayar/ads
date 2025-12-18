from http.server import BaseHTTPRequestHandler
import json
import os
import re

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        if self.path == '/api/health' or self.path == '/health':
            response = {'status': 'ok', 'message': 'API is running on Vercel'}
        else:
            response = {
                'message': 'Amazon Ads Automation API',
                'status': 'running',
                'endpoints': {
                    'health': 'GET /api/health',
                    'generate': 'POST /api/generate'
                }
            }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            if '/api/generate' in self.path:
                response = self._handle_generate(data)
            elif '/api/retrieve' in self.path:
                response = self._handle_retrieve(data)
            else:
                response = {'error': 'Unknown endpoint'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    
    def _handle_retrieve(self, data):
        campaign_brief = data.get('campaign_brief', '').strip()
        
        if not campaign_brief:
            return {'error': 'Campaign brief is required'}
        
        if len(campaign_brief) < 10:
            return {'error': 'Campaign brief must be at least 10 characters'}
        
        return {
            'message': 'Segment retrieval requires faiss backend',
            'note': 'Use local deployment for full vector search',
            'segments': [],
            'total_found': 0
        }
    
    def _handle_generate(self, data):
        campaign_brief = data.get('campaign_brief', '').strip()
        
        if not campaign_brief:
            return {'error': 'Campaign brief is required'}
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return {'error': 'OPENAI_API_KEY not configured in Vercel environment variables'}
        
        try:
            from openai import OpenAI
        except ImportError as e:
            return {'error': f'OpenAI import failed: {str(e)}'}
        
        client = OpenAI(api_key=api_key)
        model = os.environ.get('OPENAI_GEN_MODEL', 'gpt-4o-mini')
        
        prompt = f"""Based on the following campaign brief, suggest 5 target audience segments for Amazon Ads.
For each segment, provide:
- segment_name: A descriptive name in Japanese
- why_it_fits: 1-2 sentences explaining the fit (in Japanese)  
- keywords: 10 relevant advertising keywords (in Japanese)

Campaign Brief: {campaign_brief}

Respond ONLY with a JSON array of segment objects."""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an Amazon Ads strategist. Respond entirely in Japanese with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            segments = json.loads(json_match.group(0))
        else:
            segments = []
        
        return {
            'segments': [],
            'generated_segments': segments,
            'total_found': len(segments)
        }