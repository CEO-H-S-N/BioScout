import streamlit as st
import pandas as pd
import os
from datetime import date
import requests
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium

from utils.rag_helpers import load_knowledge_snippets, get_top_snippet
from utils.api_helpers import query_llm_with_context

load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/facebook/deit-base-patch16-224"

OBS_FILE = "observations.csv"
SCORES_FILE = "scores.csv"
RAG_FOLDER = "rag_knowledge"

def identify_species_with_huggingface(image_file):
    if image_file is None:
        return "No image data found."

    filename = image_file.name.lower()
    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
        content_type = "image/jpeg"
    elif filename.endswith(".png"):
        content_type = "image/png"
    else:
        return "Unsupported image format. Please upload JPG or PNG."

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": content_type
    }

    image_file.seek(0)
    image_bytes = image_file.read()

    try:
        response = requests.post(API_URL, headers=headers, data=image_bytes)
        if response.status_code == 200:
            result = response.json()
            return result[0]['label']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

st.set_page_config(page_title="BioScout Islamabad", layout="wide")

st.title("🦜 BioScout Islamabad")
st.write("Submit biodiversity observations and ask Islamabad nature-related questions!")

# Default map center
default_lat, default_lon = 33.6844, 73.0479

st.header("📸 Submit New Observation")

with st.form("obs_form", clear_on_submit=True):
    username = st.text_input("Your Name (for ranking)")
    species_name = st.text_input("Species Name (optional)")
    obs_date = st.date_input("Date Observed", value=date.today())
    notes = st.text_area("Additional Notes")
    image_file = st.file_uploader("Upload an Image (jpg/png)", type=["jpg", "jpeg", "png"])

    st.markdown("**Click on the map to place a draggable pin for your observation location. Drag to adjust before submitting.**")
    location_text = st.text_input("Or enter location coordinates (lat, lon)")
    user_location_guess = st.text_input("What do you call this place? (e.g., 'Trail 5, Margalla')")

    m = folium.Map(location=[default_lat, default_lon], zoom_start=12)

    marker_location = None
    if location_text:
        try:
            lat_str, lon_str = location_text.split(",")
            lat_manual = float(lat_str.strip())
            lon_manual = float(lon_str.strip())
            if -90 <= lat_manual <= 90 and -180 <= lon_manual <= 180:
                marker_location = [lat_manual, lon_manual]
            else:
                st.error("Latitude must be between -90 and 90, longitude between -180 and 180.")
        except Exception:
            st.error("Please enter coordinates in the format: lat, lon (e.g., 33.6844, 73.0479)")

    if not marker_location and "marker_location" in st.session_state:
        marker_location = st.session_state.marker_location

    if marker_location:
        folium.Marker(
            location=marker_location,
            draggable=True,
            popup="Drag me to adjust location",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

    map_data = st_folium(m, height=600, width="100%")

    if map_data:
        if not location_text:
            if "last_object" in map_data and map_data["last_object"]:
                pos = map_data["last_object"]["lat"], map_data["last_object"]["lng"]
                st.session_state.marker_location = [pos[0], pos[1]]
            elif map_data.get("last_clicked"):
                st.session_state.marker_location = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]

    submitted = st.form_submit_button("Submit Observation")

    if submitted:
        if not username:
            st.error("Please enter your name for the ranking system.")
        elif not image_file:
            st.error("Please upload an image.")
        elif not marker_location:
            st.error("Please select a location by clicking the map or entering coordinates.")
        else:
            lat, lon = marker_location

            ai_species = identify_species_with_huggingface(image_file)
            st.success(f"✅ Observation recorded! **AI Suggests:** {ai_species}")

            image_name = image_file.name

            # Location string with optional label
            if user_location_guess:
                location_str = f"{lat:.5f}, {lon:.5f} ({user_location_guess})"
            else:
                location_str = f"{lat:.5f}, {lon:.5f}"

            if not os.path.exists(OBS_FILE):
                pd.DataFrame(columns=["username", "species_name", "date", "location", "notes", "image_name"]).to_csv(OBS_FILE, index=False)

            df_obs = pd.read_csv(OBS_FILE)
            new_entry = {
                "username": username,
                "species_name": species_name or ai_species,
                "date": obs_date,
                "location": location_str,
                "notes": notes,
                "image_name": image_name
            }
            df_obs = pd.concat([df_obs, pd.DataFrame([new_entry])], ignore_index=True)
            df_obs.to_csv(OBS_FILE, index=False)

            if os.path.exists(SCORES_FILE):
                df_scores = pd.read_csv(SCORES_FILE)
            else:
                df_scores = pd.DataFrame(columns=["username", "score"])

            if username in df_scores["username"].values:
                df_scores.loc[df_scores["username"] == username, "score"] += 1
            else:
                df_scores = pd.concat([df_scores, pd.DataFrame([{"username": username, "score": 1}])], ignore_index=True)

            df_scores.to_csv(SCORES_FILE, index=False)

            if "marker_location" in st.session_state:
                del st.session_state.marker_location

            # Workaround for rerun without experimental_rerun()
            st.session_state["just_submitted"] = not st.session_state.get("just_submitted", False)

if st.session_state.get("just_submitted", False):
    st.experimental_rerun = lambda: None  # dummy replacement to avoid errors
    st.experimental_rerun()

st.header("📂 Past Observations")

if os.path.exists(OBS_FILE):
    df_obs = pd.read_csv(OBS_FILE)
    st.dataframe(df_obs, use_container_width=True)
else:
    st.info("No observations submitted yet.")

st.header("🏆 User Leaderboard")

if os.path.exists(SCORES_FILE):
    df_scores = pd.read_csv(SCORES_FILE)
    df_scores = df_scores.sort_values(by="score", ascending=False).reset_index(drop=True)
    st.table(df_scores)
else:
    st.info("No user rankings available yet. Start submitting observations!")

st.header("💬 Islamabad Biodiversity Q&A")
query = st.text_input("Ask a question about Islamabad's biodiversity...")

if query:
    with st.spinner("Thinking..."):
        snippets = load_knowledge_snippets(RAG_FOLDER)
        top_snip = get_top_snippet(query, snippets)
        answer = query_llm_with_context(query, top_snip)

    st.subheader("📚 Retrieved Context")
    st.code(top_snip, language="markdown")

    st.subheader("🧠 AI Answer")
    st.markdown(answer)
