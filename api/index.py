from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    try:
        return send_from_directory('public', 'index.html')
    except:
        return jsonify({
            'message': 'Amazon Ads Automation API',
            'status': 'running',
            'endpoints': ['/api/health', '/api/generate']
        })

@app.route('/api/health')
@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'API is running on Vercel'
    })

@app.route('/api/retrieve', methods=['POST'])
def retrieve_segments():
    """Retrieve segments based on campaign brief"""
    try:
        data = request.json or {}
        campaign_brief = data.get('campaign_brief', '').strip()
        
        if not campaign_brief:
            return jsonify({'error': 'Campaign brief is required'}), 400
        
        if len(campaign_brief) < 10:
            return jsonify({'error': 'Campaign brief must be at least 10 characters'}), 400
        
        # For now, return a placeholder response
        # The heavy processing with faiss should be done on a different backend
        return jsonify({
            'message': 'Segment retrieval requires backend with faiss support',
            'note': 'Please use a local deployment or Railway/Render for full functionality',
            'segments': [],
            'total_found': 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_segments():
    """Generate segments using OpenAI API"""
    try:
        data = request.json or {}
        campaign_brief = data.get('campaign_brief', '').strip()
        
        if not campaign_brief:
            return jsonify({'error': 'Campaign brief is required'}), 400
        
        # Import OpenAI only when needed
        try:
            from openai import OpenAI
            import httpx
        except ImportError:
            return jsonify({'error': 'OpenAI package not available'}), 500
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'OPENAI_API_KEY not configured'}), 500
        
        client = OpenAI(api_key=api_key)
        model = os.getenv('OPENAI_GEN_MODEL', 'gpt-4o-mini')
        
        # Generate segments using OpenAI
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
        
        import json
        content = response.choices[0].message.content.strip()
        
        # Parse JSON from response
        import re
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

# For Vercel, we need to export the app
# The handler is automatically detected by Vercel for Flask apps