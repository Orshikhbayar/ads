import os
import sys
import json
import re

from flask import Flask, request, jsonify

app = Flask(__name__)

# Simple CORS handling without flask_cors
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def index():
    # Simple HTML
    html_content = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
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
    <button onclick="testGenerate()">検索</button>
    <div id="results" class="results"></div>
  </div>
  
  <script>
    async function testGenerate() {
      const brief = document.getElementById('campaign-brief').value;
      const resultsDiv = document.getElementById('results');
      
      if (!brief.trim()) {
        resultsDiv.innerHTML = 'キャンペーン詳細を入力してください';
        return;
      }
      
      try {
        resultsDiv.innerHTML = '処理中...';
        
        const response = await fetch('/api/generate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            campaign_brief: brief,
            top_k: 10,
            keyword_weight: 0.5,
            enable_keywords: true
          })
        });
        
        const data = await response.json();
        
        if (data.segments) {
          let html = '<h3>検索結果:</h3><ul>';
          data.segments.forEach(seg => {
            html += `<li>${seg.name} - ${seg.match_percent.toFixed(1)}%</li>`;
          });
          html += '</ul>';
          
          if (data.generated_segments && data.generated_segments.length > 0) {
            html += '<h3>提案セグメント:</h3>';
            data.generated_segments.forEach(seg => {
              html += `<div style="border:1px solid #ccc; margin:10px 0; padding:10px;">`;
              html += `<h4>${seg.name}</h4>`;
              html += `<p><strong>理由:</strong> ${seg.why_fits || 'なし'}</p>`;
              html += `<p><strong>キーワード:</strong> ${(seg.keywords || []).join(', ')}</p>`;
              html += `<p><strong>説明:</strong> ${seg.description || 'なし'}</p>`;
              html += `</div>`;
            });
          }
          
          // Add debug info
          if (data.debug) {
            html += '<details><summary>デバッグ情報</summary>';
            html += `<pre>${JSON.stringify(data.debug, null, 2)}</pre>`;
            html += '</details>';
          }
          
          resultsDiv.innerHTML = html;
        } else {
          resultsDiv.innerHTML = 'エラー: ' + (data.error || '不明なエラー');
        }
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
    return jsonify({'status': 'ok', 'message': 'Working version is running'})

@app.route('/api/generate', methods=['POST'])
def generate_segments():
    try:
        data = request.json or {}
        campaign_brief = data.get('campaign_brief', '').strip()
        
        if not campaign_brief:
            return jsonify({'error': 'Campaign brief is required'}), 400
        
        # Try to run 12.py
        import subprocess
        
        script_path = os.path.join(os.path.dirname(__file__), '..', '12.py')
        cmd = [
            sys.executable, script_path,
            '--brief', campaign_brief,
            '--kw-weight', '0.5'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90,  # Increased for better reliability
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': f'Script failed: {result.stderr}',
                'debug': {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                }
            }), 500
        
        # Check for API key issues in the output
        if 'API key' in result.stderr or 'authentication' in result.stderr.lower():
            return jsonify({
                'error': 'OpenAI API key issue - check if key is valid and has model access',
                'debug': {'stderr': result.stderr}
            }), 500
        
        # Parse segments from output
        segments = []
        generated_segments = []
        lines = result.stdout.split('\n')
        
        # Look for retrieval results
        for i, line in enumerate(lines):
            # Match pattern like "1) メンズマネークリップ"
            match = re.match(r'(\d+)\)\s+(.+)', line.strip())
            if match:
                segment_name = match.group(2)
                
                # Look for the next line with match percentage
                if i + 1 < len(lines):
                    score_line = lines[i + 1]
                    score_match = re.search(r'match:\s*([\d.]+)%', score_line)
                    if score_match:
                        match_percent = float(score_match.group(1))
                        segments.append({
                            'name': segment_name,
                            'match_percent': match_percent
                        })
        
        # Look for generated segments (after "💡 Proposed Target Segments")
        output_parts = result.stdout.split('💡 Proposed Target Segments')
        if len(output_parts) > 1:
            generated_part = output_parts[1]
            # Simple parsing for generated segments
            segment_blocks = re.split(r'\*\*Segment \d+:', generated_part)
            
            for block in segment_blocks[1:]:  # Skip first empty part
                segment = {}
                lines = block.strip().split('\n')
                
                if lines:
                    # First line is the segment name
                    name_line = lines[0].strip().replace('**', '').strip()
                    if name_line:
                        segment['name'] = name_line
                
                # Extract why it fits
                why_match = re.search(r'\*\*Why it fits:\*\*\s*([^\*]+?)(?=\*\*|$)', block, re.DOTALL)
                if why_match:
                    segment['why_fits'] = why_match.group(1).strip()
                
                # Extract keywords
                keywords_match = re.search(r'\*\*Keywords:\*\*\s*([^\*]+?)(?=\*\*|$)', block, re.DOTALL)
                if keywords_match:
                    keywords_text = keywords_match.group(1).strip()
                    keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
                    segment['keywords'] = keywords[:10]
                
                # Extract description
                desc_match = re.search(r'\*\*Description:\*\*\s*([^\*]+?)(?=\*\*|$)', block, re.DOTALL)
                if desc_match:
                    segment['description'] = desc_match.group(1).strip()
                elif segment.get('why_fits'):
                    segment['description'] = segment['why_fits'][:150]
                
                if segment.get('name'):
                    generated_segments.append(segment)
        
        return jsonify({
            'segments': segments,
            'generated_segments': generated_segments,
            'total_found': len(segments),
            'debug': {
                'stdout_preview': result.stdout[:1000],
                'command': ' '.join(cmd),
                'found_segments': len(segments),
                'found_generated': len(generated_segments)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Export for Vercel
app = app