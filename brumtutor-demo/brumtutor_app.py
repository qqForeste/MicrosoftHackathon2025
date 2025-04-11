# BrumTutor Tech Demo

import streamlit as st
import requests
import base64

# --- Config ---
AZURE_OPENAI_ENDPOINT = "https://YOUR-PROXY-ENDPOINT.openai.azure.com/"
API_KEY = ""  # Leave blank for now
MODEL = "gpt-4o"
DEPLOYMENT_NAME = "gpt-4o-vision"

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

# --- UI ---
st.title("📚 BrumTutor – AI Homework Helper")
st.write("Helping Birmingham students understand their homework step-by-step")

uploaded_file = st.file_uploader("Upload a photo of your question (e.g. maths, science)", type=["jpg", "png", "jpeg"])

language = st.selectbox("Preferred language for explanation:", ["English", "Polish", "Urdu", "Arabic", "Punjabi"])

if uploaded_file:
    st.image(uploaded_file, caption="Your question", use_column_width=True)
    image_bytes = uploaded_file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    with st.spinner("Reading your question and thinking... 🧠"):

        # Fallback if no API key
        if not API_KEY or API_KEY.strip() == "":
            st.warning("⚠️ API key not found. Showing mock explanation instead.")
            st.markdown("### 🧾 AI Explanation (Example):")
            st.write(f"""
In **{language}**, here’s how to solve your question:

**Step 1**: Identify what the question is asking.  
**Step 2**: Break the problem into smaller steps.  
**Step 3**: Solve it one part at a time.  
**Step 4**: Double check your answer.

👉 This is a placeholder explanation. // Waiting for API Key
""")
        else:
            # Actual API call
            prompt = f"""
You are a helpful tutor for secondary school students in Birmingham.
Please read the question in the uploaded image and explain it step-by-step in simple {language}.
Avoid just giving the answer — teach the process kindly, like a real tutor.
"""

            data = {
                "messages": [
                    {"role": "system", "content": "You are a helpful and friendly AI tutor."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                "temperature": 0.7,
                "max_tokens": 800,
            }

            response = requests.post(
                f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-15-preview",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                st.markdown("### 🧾 AI Explanation:")
                st.write(answer)
            else:
                st.error("Failed to get response from Azure OpenAI. Check your API key or endpoint.")
