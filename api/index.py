from http.server import BaseHTTPRequestHandler
import json
import os
import re
import traceback

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        # Serve the HTML UI for root path
        if self.path == '/':
            try:
                # Look for index.html in the parent directory (root) or current directory
                html_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
                if not os.path.exists(html_path):
                    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
                
                # Fallback to hardcoded HTML if file doesn't exist
                if os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                else:
                    html_content = self._get_fallback_html()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
                return
            except Exception as e:
                # Fall through to JSON error if HTML serving fails
                print(f"Error serving HTML: {e}")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        if self.path == '/api/health' or self.path == '/health':
            response = {'status': 'ok', 'message': 'API is running on Vercel'}
        else:
            # Check if OPENAI_API_KEY is set
            has_key = bool(os.environ.get('OPENAI_API_KEY'))
            response = {
                'message': 'Amazon Ads Automation API',
                'status': 'running',
                'openai_key_configured': has_key,
                'endpoints': {
                    'ui': 'GET /',
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
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_detail = {
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(error_detail).encode())
    
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
        try:
            campaign_brief = data.get('campaign_brief', '').strip()
            
            if not campaign_brief:
                return {'error': 'Campaign brief is required'}
            
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return {
                    'error': 'OPENAI_API_KEY not configured',
                    'help': 'Go to Vercel Dashboard > Project > Settings > Environment Variables > Add OPENAI_API_KEY'
                }
            
            # Import OpenAI
            try:
                from openai import OpenAI
            except ImportError as e:
                return {'error': f'OpenAI import failed: {str(e)}'}
            
            client = OpenAI(api_key=api_key)
            model = os.environ.get('OPENAI_GEN_MODEL', 'gpt-4o-mini')
            top_k = int(data.get('top_k', 10))
            
            prompt = f"""Based on the following campaign brief, suggest {top_k} target audience segments for Amazon Ads.
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
            
            # Parse JSON from response
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
            
        except Exception as e:
            return {
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }

    def _get_fallback_html(self):
        return """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Amazon Ads アシスタント (Fallback)</title>
  <style>body{font-family:sans-serif;padding:2rem;text-align:center}</style>
</head>
<body>
  <h1>Amazon Ads アシスタント</h1>
  <p>Loading UI...</p>
  <script>location.reload();</script>
</body>
</html>"""
