import streamlit as st
import joblib
import scanner
import google.generativeai as genai
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="SRP Code Judge", page_icon="⚖️", layout="wide")

st.title("⚖️ SRP Violation Detector & Refactor Tool")
st.markdown("### Detects SRP Violations and suggests fixes using GenAI.")

# --- SIDEBAR: API KEY ---
# We need this to "Write" the new code. The user enters their key securely.
with st.sidebar:
    st.header("🔑 AI Settings")
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    st.info("Get a free key at: [aistudio.google.com](https://aistudio.google.com/app/apikey)")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("AI Connected!")

# --- LOAD THE JUDGE (Random Forest) ---
@st.cache_resource
def load_judge():
    try:
        return joblib.load('srp_judge_model.pkl')
    except:
        return None

judge_model = load_judge()

if judge_model is None:
    st.error("❌ 'srp_judge_model.pkl' not found. Please run your training script first.")
    st.stop()

# --- HELPER: THE "WRITER" AI ---
def get_srp_fix(bad_code, class_name):
    """Sends the messy code to Gemini and asks for a refactored version."""
    if not api_key:
        return "⚠️ Please enter an API Key in the sidebar to generate fixes."
    
    try:
        # The Prompt
        prompt = f"""
        You are a Senior Software Architect expert in SOLID principles.
        The following Python class '{class_name}' violates the Single Responsibility Principle (SRP).
        
        Please refactor it by splitting it into smaller, focused classes.
        Provide ONLY the Python code for the corrected version. Do not add explanations.
        
        BAD CODE:
        {bad_code}
        """
        
        # FIX: Using the exact model ID from your list
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        with st.spinner('🤖 AI is thinking and rewriting your code...'):
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error contacting AI: {str(e)}"

# --- MAIN APP LOGIC ---
uploaded_file = st.file_uploader("Upload Python File (.py)", type="py")

if uploaded_file:
    code_content = uploaded_file.read().decode("utf-8")
    
    # 1. Show Original Code
    with st.expander("📄 View Original Source Code", expanded=False):
        st.code(code_content, language='python')

    st.divider()
    st.subheader("🔍 Analysis Report")

    # 2. Scan the file
    results = scanner.analyze_code_content(code_content)

    if not results:
        st.warning("No classes found in this file.")
    else:
        # Create tabs for each class found
        class_names = [r['Class Name'] for r in results]
        tabs = st.tabs(class_names)

        for i, tab in enumerate(tabs):
            item = results[i]
            features = item["Features"]
            
            with tab:
                # 3. The Judge Decides
                prediction = judge_model.predict([features])[0]
                confidence = judge_model.predict_proba([features])[0]
                
                # Setup Display Variables
                if prediction == 1.0:
                    status_color = "red"
                    status_text = "SRP VIOLATION DETECTED"
                    score = confidence[1]
                    is_messy = True
                else:
                    status_color = "green"
                    status_text = "CLEAN CODE"
                    score = confidence[0]
                    is_messy = False

                # 4. Display Metrics
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"## :{status_color}[{status_text}]")
                    st.progress(score, text=f"Confidence: {int(score*100)}%")
                    
                    st.write("---")
                    st.metric("Methods", item["Methods"])
                    st.metric("Responsibilities", item["Responsibilities"], 
                             delta="-High" if item["Responsibilities"] > 1 else "Normal",
                             delta_color="inverse")
                    st.metric("Cohesion Score", f"{item['Cohesion']:.2f}")

                with col2:
                    # 5. The "Fix It" Section (Only for Messy Code)
                    if is_messy:
                        st.warning(f"⚠️ The class `{item['Class Name']}` is doing too much ({item['Responsibilities']} responsibilities).")
                        st.markdown("### 🛠️ Suggested Fix")
                        
                        # The Magic Button
                        if st.button(f"✨ Generate Refactored Code for {item['Class Name']}", key=f"btn_{i}"):
                            # CALL THE WRITER AI
                            fixed_code = get_srp_fix(code_content, item['Class Name'])
                            st.success("Here is the corrected version:")
                            st.code(fixed_code, language='python')
                    else:
                        st.success("🎉 This class is already optimized and follows SRP.")
                        st.balloons()