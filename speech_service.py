import os
from dotenv import load_dotenv
import requests

load_dotenv()

class ElevenLabsService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def text_to_speech(self, text):
        """Convert text to speech using ElevenLabs API."""
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Save the audio file
            filename = "static/briefing.mp3"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
