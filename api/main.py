import os
import sys
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
    # Embed HTML content directly for Vercel deployment
    html_content = '''<!DOCTYPE html>
<html lang="ja">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Amazon Ads アシスタント</title>
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;600;700&display=swap"
    rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box
    }

    body {
      font-family: 'Noto Sans JP', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #f9fafb;
      color: #0f1419;
      height: 100vh;
      line-height: 1.5;
      overflow: hidden;
    }

    .split-container {
      display: flex;
      height: 100vh;
      width: 100vw
    }

    /* LEFT column */
    .left-panel {
      width: 40%;
      background: #fff;
      padding: 40px;
      box-shadow: 2px 0 10px rgba(0, 0, 0, .05);
      display: flex;
      flex-direction: column;
      gap: 32px;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
    }

    /* RIGHT column (scrollable) */
    .right-panel {
      width: 60%;
      background: #f9fafb;
      padding: 40px;
      display: flex;
      flex-direction: column;
      gap: 24px;
      overflow-y: auto;
      /* whole right side can scroll */
      -webkit-overflow-scrolling: touch;
    }

    .app-title {
      text-align: center;
      margin-bottom: 8px
    }

    .app-title h1 {
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 8px
    }

    .app-title p {
      font-size: 14px;
      color: #6b7280
    }

    .form-section,
    .results-section {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, .1);
      border: 1px solid #e5e7eb
    }

    .section-header {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid #f3f4f6
    }

    .form-group {
      margin-bottom: 24px
    }

    .form-group label {
      display: block;
      font-weight: 600;
      margin-bottom: 12px;
      color: #4c1d95;
      font-size: 15px;
      position: relative;
      padding-left: 20px
    }

    .form-group label::before {
      content: '✨';
      position: absolute;
      left: 0;
      top: 0;
      font-size: 14px
    }

    .text-input {
      width: 100%;
      min-height: 120px;
      padding: 12px 16px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      background: #fff;
      font-family: inherit;
      font-size: 14px;
      transition: .2s;
      resize: vertical
    }

    .text-input:focus {
      outline: none;
      border-color: #0073bb;
      box-shadow: 0 0 0 3px rgba(0, 115, 187, .1)
    }

    .slider-container {
      display: flex;
      flex-direction: column;
      gap: 12px
    }

    .slider-header {
      display: flex;
      justify-content: space-between;
      align-items: center
    }

    .slider-value {
      font-weight: 700;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      font-size: 16px;
      padding: 6px 12px;
      border-radius: 12px;
      background-color: rgba(102, 126, 234, .1);
      border: 1px solid rgba(102, 126, 234, .2)
    }

    .slider {
      width: 100%;
      height: 8px;
      border-radius: 4px;
      background: linear-gradient(90deg, #e2e8f0 0%, #cbd5e1 100%);
      outline: none;
      appearance: none;
      -webkit-appearance: none;
      cursor: pointer;
      transition: .3s
    }

    .slider:hover {
      background: linear-gradient(90deg, #cbd5e1 0%, #94a3b8 100%)
    }

    .slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      box-shadow: 0 4px 12px rgba(102, 126, 234, .4), 0 2px 4px rgba(118, 75, 162, .3);
      transition: .3s
    }

    .slider::-webkit-slider-thumb:hover {
      transform: scale(1.1)
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: .2s;
      border: none;
      gap: 8px;
      width: 100%
    }

    .btn-primary {
      background: linear-gradient(135deg, #0073bb 0%, #005a94 100%);
      color: #fff;
      box-shadow: 0 4px 12px rgba(0, 115, 187, .3)
    }

    .btn-primary:hover {
      transform: translateY(-2px)
    }

    .table-container {
      overflow-x: auto;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      margin-bottom: 0;
      background: #fff;
      box-shadow: 0 1px 3px rgba(0, 0, 0, .1)
    }

    table {
      width: 100%;
      border-collapse: collapse;
      background: #fff
    }

    th {
      background: #f9fafb;
      padding: 16px;
      text-align: left;
      font-weight: 600;
      color: #374151;
      border-bottom: 1px solid #e5e7eb;
      font-size: 14px
    }

    td {
      padding: 16px;
      border-bottom: 1px solid #f3f4f6;
      font-size: 14px;
      color: #0f1419
    }

    tr:last-child td {
      border-bottom: none
    }

    tr:hover {
      background: #f9fafb
    }

    /* Suggested panel internal scroll (extra safety) */
    .suggested-scroll {
      max-height: calc(100vh - 180px);
      /* keeps header/padding visible */
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      padding-right: 8px;
    }

    .segment-card {
      background: #fff;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 16px;
      border-left: 4px solid #0073bb;
      box-shadow: 0 2px 4px rgba(0, 0, 0, .1)
    }

    .segment-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 12px
    }

    .segment-section {
      margin-bottom: 12px
    }

    .segment-section h4 {
      font-size: 12px;
      font-weight: 600;
      color: #6b7280;
      margin-bottom: 6px;
      letter-spacing: .5px;
      text-transform: uppercase
    }

    .keywords {
      display: flex;
      flex-wrap: wrap;
      gap: 6px
    }

    .keyword-tag {
      background: #f0f9ff;
      color: #0369a1;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      border: 1px solid #bae6fd
    }

    .headlines {
      display: flex;
      flex-direction: column;
      gap: 8px
    }

    .headline {
      background: #f9fafb;
      padding: 12px;
      border-radius: 6px;
      border: 1px solid #e5e7eb;
      font-weight: 500
    }

    .loading {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 60px;
      flex-direction: column;
      gap: 16px
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid rgba(102, 126, 234, .2);
      border-top: 4px solid #667eea;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      position: relative
    }

    .spinner::after {
      content: '';
      position: absolute;
      top: -4px;
      left: -4px;
      width: 40px;
      height: 40px;
      border: 4px solid transparent;
      border-top: 4px solid #764ba2;
      border-radius: 50%;
      animation: spin 1.5s linear infinite reverse
    }

    .loading-text {
      color: #64748b;
      font-size: 14px
    }

    @keyframes spin {
      0% {
        transform: rotate(0)
      }

      100% {
        transform: rotate(360deg)
      }
    }

    @media (max-width: 768px) {
      .split-container {
        flex-direction: column
      }

      .left-panel,
      .right-panel {
        width: 100%;
        height: auto;
        overflow: visible
      }

      .suggested-scroll {
        max-height: none
      }
    }
  </style>
</head>

<body>
  <div class="split-container">
    <!-- LEFT: Form + Retrieved Segments -->
    <div class="left-panel">
      <div class="app-title">
        <h1>Amazon Ads アシスタント</h1>
      </div>

      <div class="form-section">
        <div class="form-group">
          <label for="campaign-brief">ターゲットオーディエンスについて</label>
          <textarea id="campaign-brief" class="text-input" placeholder="ターゲットオーディエンスについて詳細を入力してください..."></textarea>
        </div>

        <!-- hidden keyword weight (kept) -->
        <input type="hidden" id="keyword-weight" value="0.5">

        <button class="btn btn-primary" onclick="generateComplete()">
          <span>✨</span> 検索
        </button>
      </div>

      <!-- Retrieved Segments -->
      <div class="results-section">
        <table>
          <thead>
            <tr>
              <th>セグメント名</th>
              <th>マッチ率 %</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colspan="2" style="text-align:center;color:#6b7280;padding:32px;">
                表示できるセグメント情報はありません。<br> 検索完了後に表示されます。
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- RIGHT: Suggested Target Segments (ALWAYS OPEN + SCROLLABLE) -->
    <div class="right-panel">
      <div class="results-section">
        <div class="section-header">マッチしたセグメント</div>
        <div id="suggested_panel" class="suggested-scroll">
          <p style="color:#6b7280;text-align:center;">表示できるセグメント情報はありません。<br> 検索完了後に表示されます。</p>
        </div>
      </div>
    </div>
  </div>

  <script>
    async function generateComplete() {
      const campaignBrief = document.getElementById('campaign-brief').value;
      const topK = 10;
      const keywordWeight = document.getElementById('keyword-weight').value;
      const enableKeywords = true;

      if (!campaignBrief.trim()) {
        alert('詳細を入力してください');
        return;
      }
      try {
        showLoading('検索中...');

        // Single API call that does both retrieval and generation
        const response = await fetch('/api/generate', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            campaign_brief: campaignBrief,
            top_k: parseInt(topK),
            keyword_weight: parseFloat(keywordWeight),
            enable_keywords: enableKeywords
          })
        });

        const data = await response.json();
        if (!response.ok) {
          alert('エラー: ' + data.error);
          hideLoading();
          return;
        }

        // Update both tables with consistent data
        if (data.segments) {
          updateResultsTable(data.segments);
        }
        if (data.generated_segments && data.generated_segments.length > 0) {
          updateProposedSegments(data.generated_segments);
        }
      } catch (err) {
        alert('Network error: ' + err.message);
      } finally {
        hideLoading();
      }
    }

    function updateResultsTable(segments) {
      const tbody = document.querySelector('tbody');
      if (!segments || segments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="2" style="text-align:center;color:#64748b;">セグメントが見つかりません</td></tr>';
        return;
      }
      tbody.innerHTML = segments.map(s => `
        <tr>
          <td>${s.name}</td>
          <td>${s.match_percent.toFixed(1)}%</td>
        </tr>`).join('');
    }

    function updateProposedSegments(segments) {
      const container = document.getElementById('suggested_panel');
      if (!segments || segments.length === 0) {
        container.innerHTML = '<p style="color:#64748b;text-align:center;">表示できるセグメントはありません</p>';
        return;
      }
      container.innerHTML = segments.map(seg => `
        <div class="segment-card">
          <div class="segment-title">${seg.name || '名前なしセグメント'}</div>
          <div class="segment-section"><h4>理由</h4><p>${seg.why_fits || '説明がありません'}</p></div>
          <div class="segment-section"><h4>キーワード</h4>
            <div class="keywords">${(seg.keywords || []).map(kw => `<span class="keyword-tag">${kw}</span>`).join('')}</div>
          </div>
        </div>`).join('');
    }

    function showLoading(msg) {
      hideLoading();
      const div = document.createElement('div');
      div.id = 'loading'; div.className = 'loading';
      div.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(248,250,252,.9);z-index:1000;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:16px;';
      div.innerHTML = `<div class="spinner"></div><div class="loading-text">${msg}</div>`;
      document.body.appendChild(div);
    }
    function hideLoading() {
      const el = document.getElementById('loading'); if (el) el.remove();
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
        'message': 'Main app is running',
        'base_path': base_path,
        'files_exist': {
            'docs.jsonl': os.path.exists(os.path.join(base_path, 'Data', 'docs.jsonl')),
            'faiss.index': os.path.exists(os.path.join(base_path, 'Data', 'faiss.index')),
            'japan.json': os.path.exists(os.path.join(base_path, 'Data', 'japan.json')),
            '12.py': os.path.exists(os.path.join(base_path, '12.py')),
            'app.py': os.path.exists(os.path.join(base_path, 'app.py')),
            'utils_dir': os.path.exists(os.path.join(base_path, 'utils'))
        },
        'directory_contents': {
            'root': os.listdir(base_path) if os.path.exists(base_path) else [],
            'data': os.listdir(os.path.join(base_path, 'Data')) if os.path.exists(os.path.join(base_path, 'Data')) else []
        },
        'environment_vars': {
            'OPENAI_API_KEY': 'set' if os.getenv('OPENAI_API_KEY') else 'not set',
            'EMBEDDING_BACKEND': os.getenv('EMBEDDING_BACKEND', 'not set'),
            'EMBEDDING_MODEL': os.getenv('EMBEDDING_MODEL', 'not set')
        }
    })

@app.route('/test-simple')
def test_simple():
    """Simple test endpoint that doesn't depend on external files"""
    return jsonify({
        'message': 'Simple test works',
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'file_path': __file__
    })

@app.route('/api/test', methods=['POST'])
def test_api():
    """Test API endpoint that doesn't depend on external files"""
    try:
        data = request.json
        return jsonify({
            'status': 'success',
            'message': 'API endpoint is working',
            'received_data': data,
            'timestamp': str(os.times())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mock-retrieve', methods=['POST'])
def mock_retrieve():
    """Mock retrieve endpoint for testing"""
    try:
        data = request.json or {}
        return jsonify({
            'segments': [
                {'name': 'テストセグメント1', 'match_percent': 85.5},
                {'name': 'テストセグメント2', 'match_percent': 72.3},
                {'name': 'テストセグメント3', 'match_percent': 68.9}
            ],
            'total_found': 3,
            'message': 'Mock data - real API may have issues'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mock-generate', methods=['POST'])
def mock_generate():
    """Mock generate endpoint for testing"""
    try:
        data = request.json or {}
        return jsonify({
            'segments': [
                {'name': 'テストセグメント1', 'match_percent': 85.5}
            ],
            'generated_segments': [
                {
                    'name': 'テストセグメント1',
                    'why_fits': 'このセグメントはテスト用です。',
                    'keywords': ['テスト', 'キーワード', '例'],
                    'headlines': ['テスト見出し1', 'テスト見出し2'],
                    'description': 'これはテスト用の説明文です。'
                }
            ],
            'total_found': 1,
            'message': 'Mock data - real API may have issues'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick-test', methods=['POST'])
def quick_test():
    """Quick test that runs 12.py with minimal parameters"""
    try:
        data = request.json or {}
        campaign_brief = data.get('campaign_brief', 'test brief')
        
        import subprocess
        script_path = os.path.join(os.path.dirname(__file__), '..', '12.py')
        cmd = [sys.executable, script_path, '--brief', campaign_brief, '--debug']
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, 
                              cwd=os.path.join(os.path.dirname(__file__), '..'))
        
        return jsonify({
            'status': 'completed',
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': ' '.join(cmd)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/retrieve', methods=['POST'])
def retrieve_segments():
    try:
        # Import subprocess here to avoid import issues
        import subprocess
        
        data = request.json or {}
        print(f"Received data: {data}")

        campaign_brief = data.get('campaign_brief', '').strip()
        top_k = int(data.get('top_k', 10))
        keyword_weight = float(data.get('keyword_weight', 0.4))
        enable_keywords = data.get('enable_keywords', True)

        if not campaign_brief:
            return jsonify({'error': 'Campaign brief is required'}), 400

        # Minimum characters for a useful marketing brief
        MIN_BRIEF_CHARS = 10
        if len(campaign_brief) < MIN_BRIEF_CHARS:
            return jsonify({
                "error": f"キャンペーン説明が短すぎます。最低 {MIN_BRIEF_CHARS} 文字必要です。"
            }), 400

        # Build command for 12.py - use absolute path
        script_path = os.path.join(os.path.dirname(__file__), '..', '12.py')
        cmd = [
            sys.executable, script_path,
            '--brief', campaign_brief,
            '--kw-weight', str(keyword_weight),
            '--retrieval-only'  # Only get matches, no LLM generation
        ]
        if not enable_keywords:
            cmd.append('--no-extract')

        print(f"Running command: {' '.join(cmd)}")

        # Run the script with proper working directory and timeout
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=90,  # 90 second timeout for 10 segments
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )

        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")

        if result.returncode != 0:
            return jsonify({'error': f'Script error: {result.stderr}'}), 500

        # Parse the output from 12.py
        segments = parse_retrieval_output(result.stdout)

        return jsonify({
            'segments': segments,
            'total_found': len(segments),
            'debug_info': {
                'stdout_length': len(result.stdout),
                'stderr_length': len(result.stderr),
                'return_code': result.returncode,
                'stdout_preview': result.stdout[:500] if result.stdout else 'No stdout'
            }
        })

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_segments():
    try:
        import subprocess
        
        data = request.json or {}
        print(f"Generate received data: {data}")

        campaign_brief = data.get('campaign_brief', '').strip()
        top_k = int(data.get('top_k', 10))
        keyword_weight = float(data.get('keyword_weight', 0.4))
        enable_keywords = data.get('enable_keywords', True)

        if not campaign_brief:
            return jsonify({'error': 'Campaign brief is required'}), 400

        # Build command for 12.py (without --retrieval-only for full generation)
        script_path = os.path.join(os.path.dirname(__file__), '..', '12.py')
        cmd = [
            sys.executable, script_path,
            '--brief', campaign_brief,
            '--kw-weight', str(keyword_weight)
        ]
        if not enable_keywords:
            cmd.append('--no-extract')

        print(f"Running generate command: {' '.join(cmd)}")

        # Run the script with timeout
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=90,  # 90 second timeout for 10 segments
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )

        print(f"Generate return code: {result.returncode}")
        print(f"Generate STDOUT: {result.stdout}")
        print(f"Generate STDERR: {result.stderr}")

        if result.returncode != 0:
            return jsonify({'error': f'Script error: {result.stderr}'}), 500

        # Parse both retrieval results and generated segments
        segments, generated_segments = parse_full_output(result.stdout, campaign_brief)

        return jsonify({
            'segments': segments,
            'generated_segments': generated_segments,
            'total_found': len(segments),
            'debug_info': {
                'stdout_length': len(result.stdout),
                'stderr_length': len(result.stderr),
                'return_code': result.returncode,
                'stdout_preview': result.stdout[:500] if result.stdout else 'No stdout'
            }
        })

    except Exception as e:
        print(f"Generate error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def parse_retrieval_output(output):
    """Parse the retrieval-only output from 12.py"""
    import re
    
    segments = []
    lines = output.split('\n')

    for i, line in enumerate(lines):
        # Look for lines like: "1) Tech Enthusiasts 25-34"
        match = re.match(r'(\d+)\)\s+(.+)', line.strip())
        if match:
            segment_name = match.group(2)

            # Look for the next line with scores
            if i + 1 < len(lines):
                score_line = lines[i + 1]
                # Parse: "   • score: 0.891  |  match: 89.1%  |  est CTR: 2.41%"
                score_match = re.search(r'match:\s*([\d.]+)%', score_line)

                if score_match:
                    match_percent = float(score_match.group(1))
                    segments.append({
                        'name': segment_name,
                        'match_percent': match_percent
                    })
    return segments

def parse_full_output(output, brief=""):
    """Parse both retrieval results and generated segments from full 12.py output"""
    # Split output into retrieval and generation parts
    parts = output.split('💡 Proposed Target Segments')

    # Parse retrieval part
    segments = parse_retrieval_output(parts[0])

    # Parse generated segments
    generated_segments = []
    if len(parts) > 1:
        generated_segments = parse_generated_segments(parts[1], brief)

    return segments, generated_segments

def parse_generated_segments(markdown_text, brief=""):
    """Parse the generated segments from markdown output"""
    import re
    
    segments = []
    print(f"Parsing markdown text: {markdown_text[:500]}...")

    # Split by segment markers - look for **Segment N:** pattern
    segment_blocks = re.split(r'\*\*Segment \d+:', markdown_text)
    print(f"Found {len(segment_blocks)} segment blocks")

    for i, block in enumerate(segment_blocks[1:], 1):  # Skip first empty part
        print(f"Processing block {i}: {block[:200]}...")

        segment = {}

        # Extract segment name (first line after the segment marker)
        lines = block.strip().split('\n')
        if lines:
            name_line = lines[0].strip().replace('**', '').strip()
            if name_line:
                segment['name'] = name_line

        # Extract "Why it fits"
        why_match = re.search(r'\*\*Why it fits:\*\*\s*([^\*]+?)(?=\*\*|$)', block, re.DOTALL)
        if why_match:
            segment['why_fits'] = why_match.group(1).strip()

        # Extract keywords
        keywords_match = re.search(r'\*\*Keywords:\*\*\s*([^\*]+?)(?=\*\*|$)', block, re.DOTALL)
        if keywords_match:
            keywords_text = keywords_match.group(1).strip()
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            if len(keywords) <= 1:
                keywords = re.findall(r'[•·-]\s*([^\n]+)', keywords_text)
                keywords = [kw.strip() for kw in keywords if kw.strip()]
            segment['keywords'] = keywords[:10]

        if segment.get('name') and (segment.get('why_fits') or segment.get('keywords')):
            segments.append(segment)

    return segments

# Export for Vercel
app = app
