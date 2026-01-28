import streamlit as st
import joblib
import scanner 
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="OCP Code Judge", page_icon="⚖️", layout="wide")

st.title("⚖️ OCP Violation Detector & Refactor Tool")
st.markdown("### Detects OCP Violations using Random Forest and suggests polymorphic fixes.")

# --- SIDEBAR: AI SETTINGS ---
with st.sidebar:
    st.header("🔑 AI Settings")
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("AI Connected!")

# --- LOAD THE JUDGE ---
@st.cache_resource
def load_judge():
    try:
        return joblib.load('OCP_Model.pkl')
    except:
        return None

judge_model = load_judge()

if judge_model is None:
    st.error("❌ 'ocp_model.joblib' not found. Please ensure it is in the same directory.")
    st.stop()

# --- REFACTORING AI ---
def get_ocp_fix(bad_code, block_id):
    if not api_key:
        return "⚠️ Please enter an API Key in the sidebar to generate fixes."
    try:
        prompt = f"""
        You are a Senior Software Architect. The following Python code in {block_id} violates 
        the Open-Closed Principle (OCP) due to hardcoded if-elif chains.
        Refactor it using Polymorphism or the Strategy Pattern.
        Provide ONLY code.
        
        BAD CODE:
        {bad_code}
        """
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN APP ---
uploaded_file = st.file_uploader("Upload Python File (.py)", type="py")

if uploaded_file:
    code_content = uploaded_file.read().decode("utf-8")
    
    # 1. Show Original Code
    with st.expander("📄 View Original Source Code", expanded=False):
        st.code(code_content, language='python')

    st.divider()

    # 2. Scan the file
    results = scanner.analyze_code_content(code_content)


    if not results:
        st.warning("No conditional blocks found.")
    else:
        st.subheader("🔍 Analysis Report")
        
        # Create tabs for each found block
        tab_titles = [f"Block {i+1}" for i in range(len(results))]
        tabs = st.tabs(tab_titles)

        for i, tab in enumerate(tabs):
            # item is [branch_count, is_ocp_risk]
            features = results[i] 
            
            with tab:
                # 2. Prediction
                prediction = judge_model.predict([features])[0]
                confidence = judge_model.predict_proba([features])[0]

                if prediction == 1:
                    st.error("🚩 OCP VIOLATION DETECTED")
                    is_violating = True
                    prob = confidence[1]
                else:
                    st.success("✅ OCP COMPLIANT")
                    is_violating = False
                    prob = confidence[0]

                # 3. Metrics
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.progress(prob, text=f"Confidence: {int(prob*100)}%")
                    st.metric("Total Branches", features[0])
                    st.metric("High Risk (Strings)", "Yes" if features[1] == 1 else "No")

                with col2:
                    if is_violating:
                        if st.button(f"✨ Refactor Block {i+1}", key=f"btn_{i}"):
                            fixed = get_ocp_fix(code_content, f"Block {i+1}")
                            st.code(fixed, language='python')
                    else:
                        st.info("This logic is clean.")