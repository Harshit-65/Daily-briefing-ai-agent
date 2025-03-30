import os
from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from briefing_agent import BriefingAgent
from speech_service import ElevenLabsService
from traffic_service import TrafficService

load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize services
briefing_agent = BriefingAgent()
speech_service = ElevenLabsService()
traffic_service = TrafficService()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/generate-briefing', methods=['POST'])
def generate_briefing():
    try:
        traffic_info = traffic_service.get_traffic_info(
            os.getenv('HOME_ADDRESS'),
            os.getenv('OFFICE_ADDRESS')
        )

        # Generate the briefing text
        briefing_text = briefing_agent.generate_briefing(traffic_info)
        
        # Convert to speech
        audio_file = speech_service.text_to_speech(briefing_text)
        
        return jsonify({
            'success': True,
            'text': briefing_text,
            'audio_url': f'/static/briefing.mp3?t={os.path.getmtime("static/briefing.mp3")}' if audio_file else None
        })
    except Exception as e:
        print(f"Error generating briefing: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_file(f'static/{filename}')

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=True, port=3000)


