from google import genai
from google.genai import types
import json

def analyze_frames(frames, api_key: str) -> dict:
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = '''
        You are an emergency response expert analyzing CCTV footage frames.
        Analyze the provided images left to right in chronological order.
        Determine if an accident occurred.
        Return ONLY a highly structured JSON object.
        
        Format required:
        {
          "incident_type": "string",
          "vehicle_count": integer,
          "severity_score": integer,
          "required_units": ["Ambulance", "Police", "Fire", "None"],
          "pii_detected": boolean,
          "accident_detected": boolean,
          "latitude": 37.7749,
          "longitude": -122.4194
        }
        '''
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt] + frames,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        data = json.loads(response.text)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}
