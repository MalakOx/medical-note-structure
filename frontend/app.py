import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO

st.set_page_config(page_title="Medical Note Structurer", page_icon="🏥", layout="wide")

st.title("🏥 Medical Note Structuring Assistant")
st.markdown("**HealthCare+ Clinic** - Convert unstructured clinical notes into structured data")

# Sidebar for configuration
st.sidebar.header("Configuration")
backend_url = st.sidebar.text_input("Backend URL", value="http://localhost:8000")

# Test backend connection
if st.sidebar.button("Test Connection"):
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get("ollama") == "connected":
                st.sidebar.success("✅ Backend and Ollama connected")
            else:
                st.sidebar.error("❌ Backend connected but Ollama disconnected")
        else:
            st.sidebar.error("❌ Backend disconnected")
    except:
        st.sidebar.error("❌ Cannot connect to backend")

# Main interface
st.header("Upload Clinical Notes")
uploaded_file = st.file_uploader(
    "Upload a CSV file with clinical notes", 
    type="csv",
    help="CSV should have columns: patient_id, doctor_notes"
)

# Option to use sample data
if st.button("Use Sample Data"):
    sample_data = """patient_id,doctor_notes
001,"Patient complains of fatigue and joint pain for 3 weeks. Morning stiffness lasting 2 hours. Physical exam shows swollen joints in hands and wrists. Diagnosed with rheumatoid arthritis. Started methotrexate 15mg weekly and folic acid 5mg daily. Follow-up in 6 weeks to monitor response and check liver function."
002,"Severe cough and shortness of breath for 5 days. Fever 101.5F. Chest X-ray shows consolidation in right lower lobe. Possible pneumonia. Started azithromycin 500mg daily for 5 days. Return if symptoms worsen or no improvement in 3 days."
003,"Routine checkup. Blood pressure 140/90. Patient reports headaches and dizziness. No chest pain. Started lisinopril 10mg daily for hypertension. Lifestyle counseling provided. Recheck blood pressure in 2 weeks.\""""
    uploaded_file = StringIO(sample_data)

if uploaded_file:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Validate required columns
        if 'patient_id' not in df.columns or 'doctor_notes' not in df.columns:
            st.error("❌ CSV must contain 'patient_id' and 'doctor_notes' columns")
            st.stop()
        
        st.success(f"✅ Loaded {len(df)} clinical notes")
        
        # Display preview
        st.subheader("Preview of Uploaded Data")
        st.dataframe(df.head(), use_container_width=True)
        
        # Process notes
        if st.button("Extract Structured Information", type="primary"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, row in df.iterrows():
                status_text.text(f"Processing note {idx + 1} of {len(df)}...")
                progress_bar.progress((idx + 1) / len(df))
                
                try:
                    # Send request to backend
                    response = requests.post(
                        f"{backend_url}/extract/", 
                        data={"note": row["doctor_notes"]},
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        extracted = response.json()["structured"]
                        
                        # Try to parse JSON response
                        try:
                            structured = json.loads(extracted)
                        except:
                            # Fallback if JSON parsing fails
                            structured = {
                                "symptoms": ["Parsing error"],
                                "diagnosis": "Parsing error", 
                                "medications": ["Parsing error"],
                                "follow_up": "Parsing error"
                            }
                        
                        # Convert lists to string for CSV export
                        result_row = {
                            "patient_id": row["patient_id"],
                            "original_note": row["doctor_notes"][:100] + "...",  # Truncate for display
                            "symptoms": "; ".join(structured.get("symptoms", ["N/A"])) if isinstance(structured.get("symptoms"), list) else structured.get("symptoms", "N/A"),
                            "diagnosis": structured.get("diagnosis", "N/A"),
                            "medications": "; ".join(structured.get("medications", ["N/A"])) if isinstance(structured.get("medications"), list) else structured.get("medications", "N/A"),
                            "follow_up": structured.get("follow_up", "N/A")
                        }
                        results.append(result_row)
                    
                    else:
                        # Handle API error
                        results.append({
                            "patient_id": row["patient_id"],
                            "original_note": row["doctor_notes"][:100] + "...",
                            "symptoms": "API Error",
                            "diagnosis": "API Error",
                            "medications": "API Error", 
                            "follow_up": "API Error"
                        })
                
                except Exception as e:
                    # Handle connection error
                    results.append({
                        "patient_id": row["patient_id"],
                        "original_note": row["doctor_notes"][:100] + "...",
                        "symptoms": f"Error: {str(e)[:50]}",
                        "diagnosis": "Connection Error",
                        "medications": "Connection Error",
                        "follow_up": "Connection Error"
                    })
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            if results:
                result_df = pd.DataFrame(results)
                st.success("✅ Extraction complete!")
                
                st.subheader("Structured Medical Notes")
                st.dataframe(result_df, use_container_width=True)
                
                # Download button
                csv_data = result_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Structured Notes (CSV)",
                    data=csv_data,
                    file_name="structured_medical_notes.csv",
                    mime="text/csv"
                )
                
                # Summary statistics
                st.subheader("Processing Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Notes Processed", len(results))
                with col2:
                    successful = sum(1 for r in results if "Error" not in str(r["diagnosis"]))
                    st.metric("Successfully Processed", successful)
                with col3:
                    error_rate = (len(results) - successful) / len(results) * 100
                    st.metric("Error Rate", f"{error_rate:.1f}%")
            
            else:
                st.error("❌ No results generated. Please check your backend connection.")
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. **Start Ollama**: Run `ollama pull llama2` then `ollama serve`
2. **Start Backend**: Run `uvicorn backend.main:app --reload`
3. **Upload CSV**: File should have 'patient_id' and 'doctor_notes' columns
4. **Process**: Click 'Extract Structured Information'
5. **Download**: Export results as CSV
""")

st.sidebar.header("About")
st.sidebar.info("""
This application uses LLaMA2 via Ollama to extract structured information from unstructured clinical notes, helping healthcare professionals organize patient data for EMR systems.
""")