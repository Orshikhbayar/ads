from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello from Vercel!', 'status': 'working'}

@app.route('/test')
def test():
    return {'test': 'This is a test endpoint'}

# Export for Vercel
app = app