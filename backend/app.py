from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from knowledge import find_answer
from datetime import datetime

# Initialize Flask app dengan kondisi yang benar
if os.path.exists('../frontend'):
    app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')
else:
    app = Flask(__name__)

CORS(app)

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_ENABLED = os.environ.get('OLLAMA_ENABLED', 'true').lower() == 'true'

@app.route('/')
def index():
    try:
        return send_from_directory('../frontend', 'index.html')
    except:
        return jsonify({'error': 'Frontend not found'}), 404

@app.route('/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory('../frontend', filename)
    except:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Flask Server OK',
        'timestamp': datetime.now().isoformat(),
        'ollama_enabled': OLLAMA_ENABLED,
        'ollama_url': OLLAMA_URL if OLLAMA_ENABLED else 'disabled'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # DEBUG: Print raw request info
        print(f'\n{"="*70}')
        print(f'📥 Raw Request:')
        print(f'   Content-Type: {request.content_type}')
        print(f'   Data: {request.data[:200] if request.data else "EMPTY"}')
        
        # Parse message dengan error handling lebih baik
        try:
            json_data = request.get_json(force=True, silent=False)
            if json_data is None:
                print('❌ JSON data is None!')
                return jsonify({'error': 'Invalid JSON format'}), 400
            
            user_message = json_data.get('message', '').strip()
        except Exception as e:
            print(f'❌ JSON Parse Error: {str(e)}')
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
        
        print(f'⏰ TIME: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'👤 USER: {user_message}')
        
        if not user_message:
            print('⚠️  User message is empty')
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

        # STEP 2: Use Ollama if not in KB (dan Ollama enabled)
        else:
            if not OLLAMA_ENABLED:
                print('⚠️  NOT IN KB - OLLAMA DISABLED')
                return jsonify({
                    'reply': '❌ Pertanyaan tidak ada di Knowledge Base dan Ollama disabled.',
                    'source': 'kb_only'
                }), 200
            
            print('⚠️  NOT IN KB - CALLING OLLAMA AI')
            try:
                print(f'📡 Connecting to Ollama: {OLLAMA_URL}')
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        'model': 'llama3',
                        'prompt': user_message,
                        'stream': False,
                        'temperature': 0.7
                    },
                    timeout=60
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
                        'reply': f'❌ Ollama error: Status {response.status_code}',
                        'source': 'error'
                    }), 200
                    
            except requests.exceptions.Timeout:
                print(f'⏱️  OLLAMA TIMEOUT')
                return jsonify({
                    'reply': '⏱️ Ollama sedang loading... (timeout). Silakan coba lagi.',
                    'source': 'timeout'
                }), 200
                
            except requests.exceptions.ConnectionError:
                print(f'🔌 OLLAMA CONNECTION ERROR')
                return jsonify({
                    'reply': '🔌 Tidak bisa connect ke Ollama. Pastikan service berjalan.',
                    'source': 'connection_error'
                }), 200
                
            except Exception as e:
                print(f'❌ OLLAMA ERROR: {str(e)}')
                return jsonify({
                    'reply': f'❌ Ollama Error: {str(e)}',
                    'source': 'error'
                }), 200
    
    except Exception as e:
        print(f'❌ UNEXPECTED ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'reply': f'❌ Error: {str(e)}',
            'source': 'error'
        }), 500

if __name__ == '__main__':
    print('\n' + '='*70)
    print('🚀 SARA_BOT FLASK SERVER STARTED')
    print('='*70)
    print(f'✅ Backend:     http://localhost:5000')
    print(f'📡 Ollama:      {"ENABLED" if OLLAMA_ENABLED else "DISABLED"}')
    if OLLAMA_ENABLED:
        print(f'📍 Ollama URL:  {OLLAMA_URL}')
    print(f'🤖 Model:       llama3')
    print(f'📁 Knowledge:   Loaded')
    print(f'⏰ Started at:   {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*70 + '\n')
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, port=port, host='0.0.0.0')