# app.py
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Code Vulnerability Scanner",
    layout="wide"
)

# Configure Google Gemini AI
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]  # For Streamlit deployment
genai.configure(api_key=GOOGLE_API_KEY)

# Safety settings for Gemini
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

model = genai.GenerativeModel(
    'gemini-pro',
    safety_settings=safety_settings
)

def analyze_code(code):
    prompt = """
    You are a security expert analyzing code for vulnerabilities. 
    Your task is to return ONLY a JSON object in the following exact format, with no additional text, markdown, or explanation:

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

    Important rules:
    1. severity and risk_level must be exactly "high", "medium", or "low" (lowercase)
    2. code_block should contain the exact vulnerable code snippet from the input
    3. Return ONLY the JSON object, no other text
    4. Ensure all JSON fields are present
    5. Make recommendation specific and actionable

    Analyze this code and respond ONLY with the JSON object:
    """
    
    try:
        response = model.generate_content(
            prompt + code,
            generation_config={
                'max_output_tokens': 2000,
                'temperature': 0.1
            }
        )
        
        if response.parts:
            # Clean and parse the response
            result_text = response.text.strip()
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '', 1)
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result_text = result_text.strip()
            return json.loads(result_text)
    except Exception as e:
        st.error(f"Error analyzing code: {str(e)}")
        return None

def main():
    st.title("Code Vulnerability Scanner")
    
    # Custom CSS
    st.markdown("""
        <style>
        .vulnerability-high {
            border-left: 4px solid #ff4b4b;
            padding-left: 10px;
        }
        .vulnerability-medium {
            border-left: 4px solid #ffa600;
            padding-left: 10px;
        }
        .vulnerability-low {
            border-left: 4px solid #00cc66;
            padding-left: 10px;
        }
        .code-block {
            background-color: #1e1e1e;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Code input
    code = st.text_area("Paste your code here:", height=200)
    
    if st.button("Analyze Code"):
        if not code.strip():
            st.warning("Please enter some code to analyze.")
            return
            
        with st.spinner("Analyzing code..."):
            result = analyze_code(code)
            
            if result:
                # Display summary
                st.header("Analysis Summary")
                risk_color = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }
                st.markdown(f"**Risk Level:** {risk_color.get(result['risk_level'], '⚪')} {result['risk_level'].upper()}")
                st.markdown(f"**Summary:** {result['summary']}")
                
                # Display vulnerabilities
                st.header("Vulnerabilities Found")
                for vuln in result['vulnerabilities']:
                    with st.expander(f"{vuln['type']} - {vuln['severity'].upper()}"):
                        st.markdown(f"<div class='vulnerability-{vuln['severity']}'>"
                                  f"<p><strong>Description:</strong> {vuln['description']}</p>"
                                  f"<div class='code-block'><code>{vuln['code_block']}</code></div>"
                                  f"<p><strong>Recommendation:</strong> {vuln['recommendation']}</p>"
                                  "</div>", 
                                  unsafe_allow_html=True)

if __name__ == '__main__':
    main()

# *********************
# LOCAL TESTING WITHOUT STREAMLIT 
# *********************



# from flask import Flask, request, jsonify, render_template
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv
# import json

# # Load environment variables
# load_dotenv()

# app = Flask(__name__)

# # Configure Google Gemini AI
# genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# safety_settings = [
#     {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "threshold": "BLOCK_NONE",
#     },
#     {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "threshold": "BLOCK_ONLY_HIGH",
#     },
#     {
#         "category": "HARM_CATEGORY_HARASSMENT",
#         "threshold": "BLOCK_ONLY_HIGH",
#     },
#     {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "threshold": "BLOCK_ONLY_HIGH",
#     },
# ]

# model = genai.GenerativeModel(
#     'gemini-pro',
#     safety_settings=safety_settings
# )

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/analyze', methods=['POST'])
# def analyze_code():
#     code = request.json.get('code', '')
    
#     prompt = """
#     You are a security expert analyzing code for vulnerabilities. 
#     Your task is to return ONLY a JSON object in the following exact format, with no additional text, markdown, or explanation:

#     {
#         "vulnerabilities": [
#             {
#                 "type": "string - name of vulnerability",
#                 "severity": "string - must be exactly one of: high, medium, or low",
#                 "description": "string - clear description of the vulnerability",
#                 "recommendation": "string - specific steps to fix the vulnerability",
#                 "code_block": "string - exact vulnerable code snippet from the input"
#             }
#         ],
#         "summary": "string - brief overview of all findings",
#         "risk_level": "string - must be exactly one of: high, medium, or low"
#     }

#     Important rules:
#     1. severity and risk_level must be exactly "high", "medium", or "low" (lowercase)
#     2. code_block should contain the exact vulnerable code snippet from the input
#     3. Return ONLY the JSON object, no other text
#     4. Ensure all JSON fields are present
#     5. Make recommendation specific and actionable

#     Analyze this code and respond ONLY with the JSON object:

#     """
    
#     try:
#         response = model.generate_content(
#             prompt + code,
#             generation_config={
#                 'max_output_tokens': 2000,
#                 'temperature': 0.1
#             }
#         )
        
#         if response.parts:
#             try:
#                 # Clean the response text
#                 result_text = response.text.strip()
                
#                 # Remove any markdown code block indicators if present
#                 if result_text.startswith('```json'):
#                     result_text = result_text.replace('```json', '', 1)
#                 if result_text.endswith('```'):
#                     result_text = result_text[:-3]
                
#                 result_text = result_text.strip()
                
#                 # Parse JSON
#                 json_result = json.loads(result_text)
                
#                 # Validate required fields
#                 required_fields = ['vulnerabilities', 'summary', 'risk_level']
#                 if not all(field in json_result for field in required_fields):
#                     raise ValueError("Missing required fields in JSON response")
                
#                 # Validate vulnerabilities structure
#                 for vuln in json_result['vulnerabilities']:
#                     required_vuln_fields = ['type', 'severity', 'description', 'recommendation', 'code_block']
#                     if not all(field in vuln for field in required_vuln_fields):
#                         raise ValueError("Missing required fields in vulnerability")
#                     if vuln['severity'] not in ['high', 'medium', 'low']:
#                         raise ValueError("Invalid severity level")
                
#                 if json_result['risk_level'] not in ['high', 'medium', 'low']:
#                     raise ValueError("Invalid risk level")
                
#                 return jsonify({
#                     "status": "success",
#                     "result": json_result
#                 })
#             except (json.JSONDecodeError, ValueError) as e:
#                 return jsonify({
#                     "status": "error",
#                     "message": f"Invalid JSON format: {str(e)}",
#                     "raw_response": result_text
#                 })
#         else:
#             return jsonify({
#                 "status": "error",
#                 "message": "No response generated",
#                 "details": str(response)
#             })
            
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         })

# if __name__ == '__main__':
#     app.run(debug=True)



