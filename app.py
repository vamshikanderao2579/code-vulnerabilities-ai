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

# Secure code examples
SECURE_CODE_EXAMPLES = {
    "SQL Injection": """
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    # Using parameterized query to prevent SQL injection
    cursor.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()
    return str(results)
""",
    "File Upload": """
from flask import Flask, request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg'}

def allowed_file(filename):
    return '.' in filename and \\
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        safe_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.abspath(safe_path).startswith(
            os.path.abspath(UPLOAD_FOLDER)
        ):
            file.save(safe_path)
            return 'File uploaded successfully'
    return 'Invalid file', 400
""",
    "Command Injection": """
from flask import Flask, request
import subprocess
import ipaddress

app = Flask(__name__)

def is_valid_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

@app.route('/ping', methods=['POST'])
def ping():
    host = request.form.get('host', '')
    if not is_valid_ip(host):
        return 'Invalid IP address', 400
    
    try:
        # Use list of arguments instead of shell=True
        result = subprocess.run(
            ['ping', '-c', '1', host],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return 'Ping timeout', 408
"""
}

# Page configuration
st.set_page_config(
    page_title="Code Vulnerability Scanner",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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
            background-color: #282c34;
            color: #abb2bf;
            padding: 1rem;
            border-radius: 6px;
            font-family: 'Courier New', Courier, monospace;
            margin: 1rem 0;
            overflow-x: auto;
            border: 1px solid #3e4451;
            font-size: 0.9rem;
            line-height: 1.5;
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
        
        /* Code comparison section */
        .code-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 1rem 0;
        }
        .code-section {
            background-color: #f8fafc;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #e5e7eb;
        }
        .code-section h4 {
            color: #1e3a8a;
            margin-bottom: 0.5rem;
        }
        
        /* Demo section */
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
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'code_input' not in st.session_state:
    st.session_state.code_input = ""

# API configuration
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("No Google API key found. Please set the GOOGLE_API_KEY in your .env file or Streamlit secrets.")
    st.stop()

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_secure_code_example(vuln_type):
    """Get the secure code example for a vulnerability type"""
    if "SQL Injection" in vuln_type:
        return SECURE_CODE_EXAMPLES["SQL Injection"]
    elif "File Upload" in vuln_type or "Path Traversal" in vuln_type:
        return SECURE_CODE_EXAMPLES["File Upload"]
    elif "Command Injection" in vuln_type:
        return SECURE_CODE_EXAMPLES["Command Injection"]
    return "No secure code example available for this vulnerability type."

def analyze_code(code):
    prompt = """
    You are a security expert analyzing code for vulnerabilities. 
    Your task is to return ONLY a JSON object in the following exact format:
    {
        "vulnerabilities": [
            {
                "type": "vulnerability name",
                "severity": "high/medium/low",
                "description": "clear description of the issue",
                "recommendation": "specific steps to fix it",
                "code_block": "exact vulnerable code"
            }
        ],
        "summary": "brief overview of findings",
        "risk_level": "high/medium/low"
    }
    Analyze this code:
    """
    
    try:
        response = model.generate_content(prompt + code)
        if response.parts:
            result_text = response.text.strip()
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            return json.loads(result_text)
    except Exception as e:
        st.error(f"Error analyzing code: {str(e)}")
        return None

def load_example():
    if st.session_state.demo_select != "Select an example...":
        st.session_state.code_input = DEMO_EXAMPLES[st.session_state.demo_select]

def main():
    st.title("Code Vulnerability Scanner")
    
    # Create two columns for the input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code = st.text_area(
            "Paste your code here:",
            value=st.session_state.code_input,
            height=200,
            key="code_area"
        )
    
    with col2:
        st.markdown("""
            <div class="demo-title">Try a Demo</div>
        """, unsafe_allow_html=True)
        
        demo_selection = st.selectbox(
            "Load example code:",
            ["Select an example..."] + list(DEMO_EXAMPLES.keys()),
            key="demo_select",
            on_change=load_example
        )
    
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
                    secure_code = get_secure_code_example(vuln['type'])
                    st.markdown(f"""
                        <div class="vulnerability-card {vuln['severity']}">
                            <h3>{vuln['type']}</h3>
                            <p><strong>Severity:</strong> 
                                <span class="risk-badge {vuln['severity']}">{vuln['severity'].upper()}</span>
                            </p>
                            <p><strong>Description:</strong> {vuln['description']}</p>
                            <div class="code-comparison">
                                <div class="code-section">
                                    <h4>Vulnerable Code</h4>
                                    <div class="code-block"><code>{vuln['code_block']}</code></div>
                                </div>
                                <div class="code-section">
                                    <h4>Recommended Secure Code</h4>
                                    <div class="code-block"><code>{secure_code}</code></div>
                                </div>
                            </div>
                            <p><strong>Recommendation:</strong> {vuln['recommendation']}</p>
                        </div>
                    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
