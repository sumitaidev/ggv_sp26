import os
import pyttsx3
import streamlit as st


def text_to_speech(text, voice_gender, speed):
    """Generates audio from text and saves it to a file."""
    engine = pyttsx3.init()

    # Set speed (Default is usually around 200)
    engine.setProperty("rate", speed)

    # Set voice gender
    voices = engine.getProperty("voices")
    if voice_gender == "Female" and len(voices) > 1:
        engine.setProperty("voice", voices[1].id)
    else:
        engine.setProperty("voice", voices[0].id)

    # Save to a temporary file instead of speaking it directly out loud
    output_filename = "temp_speech.wav"
    engine.save_to_file(text, output_filename)
    engine.runAndWait()

    return output_filename


# --- STREAMLIT UI ---
st.set_page_config(page_title="Offline TTS Generator", page_icon="🔊")

st.title("🔊 Offline Text-to-Voice Generator")
st.write(
    "Type your text below, adjust the settings, and generate offline speech instantly."
)

# Text Input
user_text = st.text_area(
    "Enter Text", "Hello! This is a completely offline web app built with Python."
)

# Sidebar for settings
st.sidebar.header("Voice Configuration")
gender = st.sidebar.selectbox("Voice Gender", ["Male", "Female"])
speed = st.sidebar.slider(
    "Speech Speed", min_value=100, max_value=300, value=175, step=10
)

# Generate Button
if st.button("Generate Voice"):
    if user_text.strip() == "":
        st.warning("Please enter some text first!")
    else:
        with st.spinner("Processing speech offline..."):
            try:
                # Generate the audio file
                audio_file = text_to_speech(user_text, gender, speed)

                # Display the audio player in Streamlit
                st.success("Generated successfully!")
                st.audio(audio_file, format="audio/wav")

                # Optional: Add a download button for the user
                with open(audio_file, "rb") as file:
                    st.download_button(
                        label="Download Audio File",
                        data=file,
                        file_name="offline_voice.wav",
                        mime="audio/wav",
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")