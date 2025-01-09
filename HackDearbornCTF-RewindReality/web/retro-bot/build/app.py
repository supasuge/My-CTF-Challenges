from flask import Flask, request, jsonify, send_from_directory
import os
from dotenv import load_dotenv
app = Flask(__name__, static_folder='static')
load_dotenv()
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Call the Groq script
    response = os.popen(f'python3 chat.py "{user_message}"').read()
    
    return jsonify({'response': response.strip()})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)