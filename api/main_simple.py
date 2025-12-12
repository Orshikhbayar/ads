import os
import sys
import json

from flask import Flask, request, jsonify

app = Flask(__name__)

# Simple CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def index():
    # Simple HTML without complex styling
    html_content = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Amazon Ads アシスタント</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .container { max-width: 800px; margin: 0 auto; }
    textarea { width: 100%; height: 100px; margin: 10px 0; }
    button { padding: 10px 20px; background: #007cba; color: white; border: none; cursor: pointer; }
    .results { margin-top: 20px; padding: 10px; background: #f5f5f5; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Amazon Ads アシスタント</h1>
    <textarea id="campaign-brief" placeholder="ターゲットオーディエンスについて詳細を入力してください..."></textarea>
    <button onclick="testAPI()">テスト実行</button>
    <div id="results" class="results"></div>
  </div>
  
  <script>
    async function testAPI() {
      const brief = document.getElementById('campaign-brief').value;
      const resultsDiv = document.getElementById('results');
      
      if (!brief.trim()) {
        resultsDiv.innerHTML = 'キャンペーン詳細を入力してください';
        return;
      }
      
      try {
        resultsDiv.innerHTML = '処理中...';
        
        const response = await fetch('/api/test-generate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({campaign_brief: brief})
        });
        
        const data = await response.json();
        resultsDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
      } catch (error) {
        resultsDiv.innerHTML = 'エラー: ' + error.message;
      }
    }
  </script>
</body>
</html>'''
    return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/health')
def health():
    base_path = os.path.join(os.path.dirname(__file__), '..')
    return jsonify({
        'status': 'ok',
        'message': 'Simple app is running',
        'files_exist': {
            'docs.jsonl': os.path.exists(os.path.join(base_path, 'Data', 'docs.jsonl')),
            'faiss.index': os.path.exists(os.path.join(base_path, 'Data', 'faiss.index')),
            '12.py': os.path.exists(os.path.join(base_path, '12.py'))
        },
        'environment_vars': {
            'OPENAI_API_KEY': 'set' if os.getenv('OPENAI_API_KEY') else 'not set',
            'EMBEDDING_BACKEND': os.getenv('EMBEDDING_BACKEND', 'not set'),
            'EMBEDDING_MODEL': os.getenv('EMBEDDING_MODEL', 'not set')
        }
    })

@app.route('/api/test-generate', methods=['POST'])
def test_generate():
    try:
        data = request.json or {}
        campaign_brief = data.get('campaign_brief', '').strip()
        
        if not campaign_brief:
            return jsonify({'error': 'Campaign brief is required'}), 400
        
        # Try to run 12.py with minimal parameters
        import subprocess
        
        script_path = os.path.join(os.path.dirname(__file__), '..', '12.py')
        cmd = [
            sys.executable, script_path,
            '--brief', campaign_brief,
            '--kw-weight', '0.5'  # Back to 0.5 as requested
        ]
        
        # Run with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90,  # 90 second timeout for 10 segments
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        
        return jsonify({
            'status': 'success',
            'return_code': result.returncode,
            'stdout_length': len(result.stdout),
            'stderr_length': len(result.stderr),
            'stdout_preview': result.stdout[:1000] if result.stdout else 'No output',
            'stderr_preview': result.stderr[:500] if result.stderr else 'No errors',
            'command': ' '.join(cmd)
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Script execution timed out after 30 seconds'}), 500
    except Exception as e:
        return jsonify({'error': f'Execution failed: {str(e)}'}), 500

# Export for Vercel
app = app