from flask import Flask, request, jsonify
import os
import json
import re

app = Flask(__name__)

# Enable CORS manually
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Amazon Ads Automation API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'generate': '/api/generate (POST)'
        }
    })

@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'API is running on Vercel'
    })

@app.route('/api/retrieve', methods=['POST', 'OPTIONS'])
def retrieve_segments():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json() or {}
        campaign_brief = data.get('campaign_brief', '').strip()
        
        if not campaign_brief:
            return jsonify({'error': 'Campaign brief is required'}), 400
        
        if len(campaign_brief) < 10:
            return jsonify({'error': 'Campaign brief must be at least 10 characters'}), 400
        
        return jsonify({
            'message': 'Segment retrieval requires backend with faiss support',
            'note': 'Use local deployment or Railway/Render for full vector search',
            'segments': [],
            'total_found': 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate_segments():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json() or {}
        campaign_brief = data.get('campaign_brief', '').strip()
        
        if not campaign_brief:
            return jsonify({'error': 'Campaign brief is required'}), 400
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'OPENAI_API_KEY not configured in Vercel environment'}), 500
        
        try:
            from openai import OpenAI
        except ImportError as e:
            return jsonify({'error': f'OpenAI import failed: {str(e)}'}), 500
        
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
        
        return jsonify({
            'segments': [],
            'generated_segments': segments,
            'total_found': len(segments)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel expects the app to be named 'app' for automatic detection
# or we can use a handler function