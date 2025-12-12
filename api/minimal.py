from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Minimal API is working', 'status': 'ok'})

@app.route('/test')
def test():
    return jsonify({'test': 'success', 'endpoint': 'minimal test'})

# Export for Vercel
app = app