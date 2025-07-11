# Medical Note Structuring Assistant

This application helps healthcare professionals convert unstructured clinical notes into structured data using LLaMA2 via Ollama.

## Features

- Extract symptoms, diagnosis, medications, and follow-up instructions from clinical notes
- Upload batch CSV files of clinical notes for processing
- View and export structured results as CSV
- Streamlit frontend with FastAPI backend
- Local LLM processing using Ollama + LLaMA2

## Project Structure

```
medical-note-structurer/
├── backend/
│   └── main.py          # FastAPI backend
├── frontend/
│   └── app.py           # Streamlit frontend
├── data/
│   └── example_notes.csv # Sample clinical notes
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Prerequisites

1. Python 3.8+
2. Ollama installed locally
3. LLaMA2 model downloaded

## Setup Instructions

### 1. Install Ollama and LLaMA2

```bash
# Install Ollama (visit https://ollama.ai for installation instructions)
# Then pull the LLaMA2 model
ollama pull llama2
```

### 2. Clone and Setup Project

```bash
git clone <your-repo-url>
cd medical-note-structurer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Ollama Server

```bash
ollama serve
```

### 4. Start Backend API

```bash
# From project root directory
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

### 5. Start Frontend Application

```bash
# From project root directory
streamlit run frontend/app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

1. **Prepare Data**: Create a CSV file with columns `patient_id` and `doctor_notes`
2. **Upload File**: Use the file uploader in the Streamlit interface
3. **Process Notes**: Click "Extract Structured Information" to analyze notes
4. **Download Results**: Export the structured data as CSV

## Sample Data Format

Your CSV should follow this format:

```csv
patient_id,doctor_notes
001,"Patient complains of fatigue and joint pain. Diagnosed with rheumatoid arthritis. Started methotrexate 15mg weekly. Follow-up in 6 weeks."
002,"Severe cough and shortness of breath. Possible pneumonia. Started azithromycin 500mg daily. Return if symptoms worsen."
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Check Ollama connection status
- `POST /extract/` - Extract structured information from clinical notes

## Troubleshooting

### Backend Issues
- Ensure Ollama is running: `ollama serve`
- Check if LLaMA2 is installed: `ollama list`
- Verify backend is running on port 8000

### Frontend Issues
- Check backend URL in sidebar configuration
- Use "Test Connection" button to verify backend connectivity
- Ensure CSV has correct column names: `patient_id`, `doctor_notes`

### Performance
- Processing time depends on note length and complexity
- LLaMA2 responses may vary in format - the app handles parsing errors gracefully
- For large batches, processing may take several minutes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Ensure compliance with healthcare data regulations (HIPAA, etc.) when using with real patient data.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify Ollama and LLaMA2 setup
3. Check application logs for error messages#   m e d i c a l - n o t e - s t r u c t u r e  
 