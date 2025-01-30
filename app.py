import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Sample vulnerable code examples
DEMO_EXAMPLES = {
    "SQL Injection Example": """
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    # Vulnerable to SQL injection
    cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{query}%'")
    results = cursor.fetchall()
    return str(results)
""",
    "File Upload Vulnerability": """
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    # Vulnerable to path traversal and unrestricted file upload
    filename = file.filename
    file.save(os.path.join('/uploads', filename))
    return 'File uploaded successfully'
""",
    "Command Injection Example": """
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/ping', methods=['POST'])
def ping():
    host = request.form['host']
    # Vulnerable to command injection
    result = subprocess.check_output(f'ping -c 1 {host}', shell=True)
    return result.decode()
"""
}
# Page configuration
st.set_page_config(
    page_title="Code Vulnerability Scanner",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
    <style>
        /* Improve spacing between input and button */
        .stButton {
            margin-top: 1rem;
        }
        
        /* Better alignment for select box */
        .stSelectbox {
            margin-bottom: 0.5rem;
        }
        
        /* Improve demo section spacing */
        .demo-title {
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Make the text area fill the column better */
        .stTextArea {
            margin-bottom: 1rem;
        }
        
        /* Improve code block readability */
        .code-block code {
            padding: 0.5rem;
            display: block;
            overflow-x: auto;
            line-height: 1.5;
        }
        
        /* Better spacing for vulnerability cards */
        .vulnerability-card {
            margin: 1.5rem 0;
        }
        
        /* Improve header spacing */
        .vulnerability-card h3 {
            margin-top: 0;
            margin-bottom: 1rem;
            color: #1E3A8A;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* Main container */
        .main > div {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Headers */
        h1 {
            color: #1E3A8A;
            font-size: 2.5rem !important;
            margin-bottom: 2rem !important;
            font-weight: 600 !important;
        }
        h2 {
            color: #2563EB;
            font-size: 1.8rem !important;
            margin-top: 2rem !important;
            font-weight: 500 !important;
        }
        
        /* Code input */
        .stTextArea textarea {
            font-family: 'Courier New', Courier, monospace;
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            background-color: #F8FAFC !important;
            padding: 1rem !important;
        }
        
        /* Button */
        .stButton button {
            background-color: #2563EB !important;
            color: white !important;
            padding: 0.5rem 2rem !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        .stButton button:hover {
            background-color: #1D4ED8 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Vulnerability cards */
        .vulnerability-card {
            background-color: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .vulnerability-card.high {
            border-left: 4px solid #DC2626;
        }
        .vulnerability-card.medium {
            border-left: 4px solid #F59E0B;
        }
        .vulnerability-card.low {
            border-left: 4px solid #10B981;
        }
        
        /* Code blocks */
        .code-block {
            background-color: #1E293B;
            color: #E5E7EB;
            padding: 1rem;
            border-radius: 6px;
            font-family: 'Courier New', Courier, monospace;
            margin: 1rem 0;
            overflow-x: auto;
        }
        
        /* Summary section */
        .summary-card {
            background-color: #F8FAFC;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border: 1px solid #E5E7EB;
        }
        
        /* Risk level badges */
        .risk-badge {
            display: inline-block;
            padding: 0.25rem 1rem;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.875rem;
            text-transform: uppercase;
            margin-left: 0.5rem;
        }
        .risk-badge.high {
            background-color: #FEE2E2;
            color: #DC2626;
        }
        .risk-badge.medium {
            background-color: #FEF3C7;
            color: #D97706;
        }
        .risk-badge.low {
            background-color: #D1FAE5;
            color: #059669;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* Previous styles remain... */
        
        /* Demo section styling */
        .demo-container {
            background-color: #F8FAFC;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #E5E7EB;
        }
        
        .demo-title {
            color: #2563EB;
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        /* Make radio buttons more visible */
        .stRadio > label {
            color: #1E3A8A !important;
            font-weight: 500 !important;
        }
        
        /* Style the selectbox */
        .stSelectbox > label {
            color: #1E3A8A !important;
            font-weight: 500 !important;
        }
        
        .stSelectbox > div > div {
            background-color: white !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Try to get API key from different sources
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("No Google API key found. Please set the GOOGLE_API_KEY in your .env file or Streamlit secrets.")
    st.stop()

# Configure Google Gemini AI
genai.configure(api_key=GOOGLE_API_KEY)

# Safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
]

model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)

def analyze_code(code):
    prompt = """
    You are a security expert analyzing code for vulnerabilities. 
    Your task is to return ONLY a JSON object in the following exact format:
    {
        "vulnerabilities": [
            {
                "type": "string - name of vulnerability",
                "severity": "string - must be exactly one of: high, medium, or low",
                "description": "string - clear description of the vulnerability",
                "recommendation": "string - specific steps to fix the vulnerability",
                "code_block": "string - exact vulnerable code snippet from the input"
            }
        ],
        "summary": "string - brief overview of all findings",
        "risk_level": "string - must be exactly one of: high, medium, or low"
    }
    """
    
    try:
        response = model.generate_content(prompt + code)
        if response.parts:
            result_text = response.text.strip()
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '', 1)
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            return json.loads(result_text.strip())
    except Exception as e:
        st.error(f"Error analyzing code: {str(e)}")
        return None


def main():
    st.title("Code Vulnerability Scanner")
    
    # Create two columns for the input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code = st.text_area("Paste your code here:", height=200)
    
    with col2:
        st.markdown("""
            <div class="demo-title">Try a Demo</div>
        """, unsafe_allow_html=True)
        
        demo_selection = st.selectbox(
            "Load example code:",
            ["Select an example..."] + list(DEMO_EXAMPLES.keys()),
            key="demo_select"
        )
        
        if st.button("Load Example", key="load_example") and demo_selection != "Select an example...":
            code = DEMO_EXAMPLES[demo_selection]
            # Use st.experimental_rerun() to update the text area
            st.session_state['code_input'] = code
            st.experimental_rerun()
    
    # If there's code in the session state, update the text area
    if 'code_input' in st.session_state:
        st.session_state['code_input'] = code
    
    # Center the analyze button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("Analyze Code", use_container_width=True)
    
    if analyze_button:
        if not code.strip():
            st.warning("Please enter some code to analyze or select a demo example.")
            return
            
        with st.spinner("Analyzing code..."):
            result = analyze_code(code)
            
            if result:
                # Display results [Previous display code remains the same...]
                # Summary Section
                st.markdown(f"""
                    <div class="summary-card">
                        <h2>Analysis Summary</h2>
                        <p><strong>Risk Level:</strong> 
                            <span class="risk-badge {result['risk_level']}">{result['risk_level'].upper()}</span>
                        </p>
                        <p>{result['summary']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Vulnerabilities Section
                st.markdown("<h2>Vulnerabilities Found</h2>", unsafe_allow_html=True)
                
                for vuln in result['vulnerabilities']:
                    st.markdown(f"""
                        <div class="vulnerability-card {vuln['severity']}">
                            <h3>{vuln['type']}</h3>
                            <p><strong>Severity:</strong> 
                                <span class="risk-badge {vuln['severity']}">{vuln['severity'].upper()}</span>
                            </p>
                            <p><strong>Description:</strong> {vuln['description']}</p>
                            <div class="code-block"><code>{vuln['code_block']}</code></div>
                            <p><strong>Recommendation:</strong> {vuln['recommendation']}</p>
                        </div>
                    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
