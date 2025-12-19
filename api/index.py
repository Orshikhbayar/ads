from http.server import BaseHTTPRequestHandler
import json
import os
import re
import traceback
import numpy as np

# ------------------------------------
# Load pre-computed embeddings and data
# ------------------------------------
_embeddings = None
_keywords = None
_docs = None
_japan_map = None

def _load_search_data():
    """Load embeddings and document data for vector search"""
    global _embeddings, _keywords, _docs, _japan_map
    
    if _embeddings is not None:
        return True
    
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Load embeddings
        emb_path = os.path.join(base_dir, 'Data', 'embeddings.npz')
        if os.path.exists(emb_path):
            data = np.load(emb_path)
            _embeddings = data['embeddings'].astype('float32')
            # Normalize embeddings for cosine similarity
            norms = np.linalg.norm(_embeddings, axis=1, keepdims=True) + 1e-12
            _embeddings = _embeddings / norms
        else:
            return False
        
        # Load keywords/segment names
        kw_path = os.path.join(base_dir, 'Data', 'keywords.json')
        if os.path.exists(kw_path):
            with open(kw_path, 'r', encoding='utf-8') as f:
                _keywords = json.load(f)
        
        # Load docs for text content
        docs_path = os.path.join(base_dir, 'Data', 'docs.jsonl')
        if os.path.exists(docs_path):
            _docs = []
            with open(docs_path, 'r', encoding='utf-8') as f:
                for line in f:
                    _docs.append(json.loads(line))
        
        # Load Japanese name mapping
        japan_path = os.path.join(base_dir, 'Data', 'japan.json')
        if os.path.exists(japan_path):
            with open(japan_path, 'r', encoding='utf-8') as f:
                _japan_map = json.load(f)
        else:
            _japan_map = {}
        
        return True
    except Exception as e:
        print(f"Error loading search data: {e}")
        return False

def _get_embedding_openai(text, client, model="text-embedding-3-small"):
    """Get embedding for query text using OpenAI"""
    try:
        response = client.embeddings.create(model=model, input=[text])
        emb = np.array(response.data[0].embedding, dtype='float32')
        # Normalize
        emb = emb / (np.linalg.norm(emb) + 1e-12)
        return emb
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def _search_segments(query_embedding, top_k=10):
    """Search for similar segments using numpy cosine similarity"""
    global _embeddings, _keywords, _docs, _japan_map
    
    if _embeddings is None or query_embedding is None:
        return []
    
    # Compute cosine similarities (embeddings are already normalized)
    similarities = np.dot(_embeddings, query_embedding)
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        cosine = float(similarities[idx])
        # Convert cosine (-1 to 1) to match percentage (0 to 100)
        match_pct = round(max(0, min(1, (cosine + 1) / 2)) * 100, 1)
        
        keyword = _keywords[idx] if _keywords and idx < len(_keywords) else f"segment_{idx}"
        jp_name = _japan_map.get(keyword, keyword) if _japan_map else keyword
        
        results.append({
            'name': jp_name,
            'match_percent': match_pct,
            'keyword': keyword,
            'text': _docs[idx].get('text', '') if _docs and idx < len(_docs) else ''
        })
    
    return results

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
            
            # --- Vector Search for real match percentages ---
            segments_with_score = []
            if _load_search_data():
                # Get query embedding
                query_emb = _get_embedding_openai(campaign_brief, client)
                if query_emb is not None:
                    segments_with_score = _search_segments(query_emb, top_k)
            
            # --- LLM Generation for segment details ---
            # Build context from retrieved segments
            segment_context = ""
            if segments_with_score:
                for i, seg in enumerate(segments_with_score[:5], 1):  # Use top 5 for context
                    segment_context += f"{i}. {seg['name']} ({seg['match_percent']:.1f}%)\n"
            
            prompt = f"""Based on the following campaign brief and retrieved segments, provide details for {top_k} target audience segments for Amazon Ads.

Campaign Brief: {campaign_brief}

Retrieved Segments:
{segment_context if segment_context else "(No segments retrieved)"}

For each segment, provide:
- segment_name: Use names from retrieved segments when applicable, or create descriptive names in Japanese
- why_it_fits: 1-2 sentences explaining the fit (in Japanese)  
- keywords: 10 relevant advertising keywords (in Japanese)

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
                raw_segments = json.loads(json_match.group(0))
                # Transform to match frontend expectations
                generated_segments = []
                
                for i, seg in enumerate(raw_segments):
                    name = seg.get('segment_name', '名前なしセグメント')
                    
                    generated_segments.append({
                        'name': name,
                        'why_fits': seg.get('why_it_fits', '説明がありません'),
                        'keywords': seg.get('keywords', [])
                    })
            else:
                generated_segments = []
            
            return {
                'segments': segments_with_score,  # Real scores from vector search
                'generated_segments': generated_segments,
                'total_found': len(segments_with_score)
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
