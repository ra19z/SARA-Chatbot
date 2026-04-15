from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from knowledge import find_answer
from datetime import datetime

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')
CORS(app)

OLLAMA_URL = 'http://localhost:11434/api/generate'

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Flask Server OK',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        
        print(f'\n{"="*70}')
        print(f'⏰ TIME: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'👤 USER: {user_message}')
        
        if not user_message:
            return jsonify({'error': 'Pesan kosong'}), 400

        # STEP 1: Check Knowledge Base first
        print('🔍 Searching Knowledge Base...')
        kb_result = find_answer(user_message)
        
        if kb_result:
            print('✅ FOUND IN KB - USING KNOWLEDGE BASE')
            
            # Check apakah ada type khusus (seperti location)
            if isinstance(kb_result, dict) and kb_result.get('type') == 'location':
                print('📍 LOCATION TYPE - Returning structured data')
                print(f'{"="*70}\n')
                return jsonify({
                    'reply': kb_result['answer'],
                    'type': 'location',
                    'address': kb_result.get('address'),
                    'maps_url': kb_result.get('maps_url'),
                    'details': kb_result.get('details'),
                    'source': 'kb',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Normal text response
            answer = kb_result.get('answer') if isinstance(kb_result, dict) else kb_result
            print(f'📝 ANSWER: {str(answer)[:100]}...')
            print(f'{"="*70}\n')
            return jsonify({
                'reply': answer,
                'source': 'kb',
                'timestamp': datetime.now().isoformat()
            })

                # STEP 2: Use Ollama if not in KB
        else:
            print('⚠️  NOT IN KB - CALLING OLLAMA AI')
            try:
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        'model': 'llama3',
                        'prompt': user_message,
                        'stream': False,
                        'temperature': 0.7
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    ai_answer = response.json().get('response', 'Tidak bisa jawab')
                    print(f'🤖 AI ANSWER: {str(ai_answer)[:100]}...')
                    print(f'{"="*70}\n')
                    return jsonify({
                        'reply': ai_answer,
                        'source': 'ollama',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    print(f'❌ OLLAMA ERROR: {response.status_code}')
                    return jsonify({
                        'reply': '❌ Ollama API tidak tersedia. Silakan hubungi IT.',
                        'source': 'error'
                    }), 503
                    
            except requests.exceptions.RequestException as e:
                print(f'❌ OLLAMA CONNECTION ERROR: {str(e)}')
                return jsonify({
                    'reply': f'❌ Tidak bisa connect ke Ollama: {str(e)}',
                    'source': 'error'
                }), 503

if __name__ == '__main__':
    print('\n' + '='*70)
    print('🚀 SARA_BOT FLASK SERVER STARTED')
    print('='*70)
    print(f'✅ Backend:     http://localhost:5000')
    print(f'📡 Ollama API:  http://localhost:11434')
    print(f'🤖 Model:       llama3')
    print(f'📁 Knowledge:   Loaded')
    print(f'⏰ Started at:   {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*70 + '\n')
    # Production mode - disable debug
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, port=port, host='0.0.0.0')