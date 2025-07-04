from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import json

app = FastAPI()

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def query_llama(prompt: str):
    """Query the local Ollama LLaMA2 model"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": prompt, "stream": False},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return "Error: Unable to connect to Ollama"
    except Exception as e:
        return f"Error: {str(e)}"

@app.post("/extract/")
def extract_medical_info(note: str = Form(...)):
    """Extract structured information from medical notes"""
    prompt = (
        f"Extract the following information from this doctor's note and return ONLY a valid JSON object:\n"
        f"- symptoms: list of patient symptoms\n"
        f"- diagnosis: primary diagnosis or suspected condition\n"
        f"- medications: list of prescribed medications with dosages\n"
        f"- follow_up: follow-up instructions or recommendations\n\n"
        f"Return the output in this exact JSON format:\n"
        f'{{"symptoms": ["symptom1", "symptom2"], "diagnosis": "diagnosis here", "medications": ["med1", "med2"], "follow_up": "follow-up instructions"}}\n\n'
        f"Doctor's note:\n{note}"
    )
    
    structured_data = query_llama(prompt)
    
    # Try to parse as JSON, if fails provide a fallback structure
    try:
        json.loads(structured_data)
        return {"structured": structured_data}
    except:
        # Fallback structure if JSON parsing fails
        fallback = {
            "symptoms": ["Unable to parse"],
            "diagnosis": "Unable to parse", 
            "medications": ["Unable to parse"],
            "follow_up": "Unable to parse"
        }
        return {"structured": json.dumps(fallback)}

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "Medical Note Structurer API is running"}

@app.get("/health")
def health_check():
    """Check if Ollama is accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "ollama": "connected"}
        else:
            return {"status": "unhealthy", "ollama": "disconnected"}
    except:
        return {"status": "unhealthy", "ollama": "disconnected"}