import streamlit as st
from openai import AzureOpenAI
import pandas as pd
import os
from datetime import datetime

# --- Azure OpenAI Config ---
ENDPOINT = "https://mango-bush-0a9e12903.5.azurestaticapps.net/api/v1"
API_KEY = "07c10633-f1e4-43e9-8cc9-a17d18a479e8"
API_VERSION = "2024-02-01"
DEPLOYMENT_NAME = "gpt-4o"

client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version=API_VERSION,
)

# --- Save and Analyze Grievance ---
def save_grievance_to_csv(grievance_text, priority, location="Unknown"):
    log_file = "grievance_log.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
    else:
        df = pd.DataFrame(columns=["Timestamp", "Text", "Priority", "Location", "ReportCount"])

    matches = df[df["Location"].str.contains(location, case=False, na=False)]
    report_count = len(matches) + 1

    new_row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Text": grievance_text,
        "Priority": priority,
        "Location": location,
        "ReportCount": report_count,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(log_file, index=False)

    return report_count

# --- AI Processing ---
def process_grievance(grievance_description):
    messages = [
        {"role": "system", "content": """
You are an automated assistant that logs public service grievances for a local council.
Your tasks:
1. Acknowledge the grievance and thank the user.
2. Clearly summarise the issue reported.
3. Assign a PRIORITY LEVEL to the issue:
   - High Priority: urgent safety, health or infrastructure threats.
   - Medium Priority: disruptive or impactful, but not immediately dangerous.
   - Low Priority: minor or cosmetic issues.
4. Outline the council’s next steps to address the problem.
5. Ask the user for any missing info (location, time, severity, photos if needed).
Maintain a formal, helpful, and civic tone — like a public services assistant.
Return the response using Markdown formatting, and include an emoji next to the priority level.
"""}, 
        {"role": "user", "content": grievance_description},
    ]
    try:
        completion = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
        )
        ai_response = completion.choices[0].message.content

        # Extract the priority from the response (looking for a pattern)
        if "High Priority" in ai_response:
            priority = "High"
        elif "Medium Priority" in ai_response:
            priority = "Medium"
        elif "Low Priority" in ai_response:
            priority = "Low"
        else:
            priority = "Low"  # Default if AI doesn't classify it properly

        return ai_response, priority
    except Exception as e:
        return f"Error processing grievance: {e}", "Low"  # Default to Low priority on error

# --- Streamlit UI ---
st.set_page_config(page_title="Grievance Reporter", page_icon="🚨")
st.title("🤖 BrumBot Reporting System🚨 ")
st.write("Hello! My name is BrumBot I am here to help feedback any issues you are having to Birmingham Council.")

grievance_input = st.text_area("Describe the issue you're experiencing:")
location_input = st.text_input("Where is this happening?")

if st.button("Submit Grievance"):
    with st.spinner("Submitting and processing your report..."):
        ai_feedback, priority = process_grievance(grievance_input)
        report_count = save_grievance_to_csv(grievance_input, priority, location_input)

        st.success("✅ Grievance logged successfully!")
        st.markdown("### 📋 AI Feedback:")
        st.write(ai_feedback)

        if report_count > 1:
            st.warning(f"⚠️ This issue has been reported {report_count} times. It will be escalated for faster review.")

# Optional: View Log
if st.checkbox("Show grievance log"):
    if os.path.exists("grievance_log.csv"):
        st.dataframe(pd.read_csv("grievance_log.csv"))
    else:
        st.info("No reports yet.")
