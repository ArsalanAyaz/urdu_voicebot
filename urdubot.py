import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from tempfile import NamedTemporaryFile

# Load environment variables
load_dotenv(".env")

API_KEY = os.getenv("API_KEY")

# Initialize the language model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    api_key=API_KEY,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Manually set the ffmpeg and ffprobe paths if necessary
AudioSegment.converter = "C:/Program Files/ffmpeg/bin/ffmpeg"
AudioSegment.ffprobe = "C:/Program Files/ffmpeg/bin/ffprobe"

# Apply custom styling for a professional dark theme and Urdu font
st.markdown(
    """
    <style>
    body {
        background-color: #121212;
    }
    .main {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
    }
    h1, h2, p, .stButton button {
        color: white;
    }
    h1 {
        text-align: center;
        color: #ffcc00;
    }
    .stButton button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
    }
    .response-text {
        font-family: 'Noto Nastaliq Urdu', serif;
        font-size: 24px;
        color: #ffffff;
        direction: rtl;
    }
    .blue-text {
        color: #1E90FF;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# App title and instructions
st.title("Urdu Voice Assistant App")
st.markdown("### <span class='blue-text'>Made by Arsalan Ayaz</span>", unsafe_allow_html=True)  # Text color changed to blue

st.markdown("""
<p style='text-align: center; font-size: 18px;'>This app allows you to give voice input in Urdu and provides responses through an AI assistant.</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Record audio function
def record_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Recording... speak in Urdu", icon="🎤")
        try:
            audio = r.listen(source)
            return audio
        except Exception as e:
            st.error(f"Error recording audio: {e}")
            return None

# Convert audio to text function
def convert_audio_to_text(audio):
    try:
        recognizer = sr.Recognizer()
        text = recognizer.recognize_google(audio, language='ur')
        return text
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

# Generate response using gemini-1.5-pro
def generate_response(input_text):
    try:
        # Create a list of BaseMessages, SystemMessage to set the role, and HumanMessage for the user input
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=input_text)
        ]

        # Print the messages to debug what is being sent
        st.write("Messages being sent: ", messages)

        # Use the structured messages with the language model API
        response = llm.invoke(messages)
        
        # Process the response
        if response and hasattr(response, 'content'):
            return response.content  # Access the response text directly from the AIMessage object
        else:
            return "No valid message content found in the response."
    except ValueError as ve:
        st.error(f"Error generating response: {ve}")
        return f"Error generating response: {ve}"
    except Exception as e:
        st.error(f"Unexpected error generating response: {e}")
        return f"Unexpected error generating response: {e}"

# Convert text to speech function
def text_to_speech(text):
    try:
        speech = gTTS(text=text, lang='ur', slow=False)
        audio_bytes = BytesIO()
        speech.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.error(f"Error converting text to speech: {e}")
        return None

# Play audio function
def play_audio(audio_bytes):
    # Create a temporary file to store the audio
    with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(audio_bytes.getbuffer())
        tmp_file_path = tmp_file.name
    
    try:
        # Load the audio and play it
        audio_segment = AudioSegment.from_file(tmp_file_path, format="mp3")
        play(audio_segment)
    except Exception as e:
        st.error(f"Error playing audio: {e}")
    finally:
        # Ensure the file is deleted after playing, and wait for it to be free
        if os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except PermissionError:
                st.warning(f"File {tmp_file_path} is still in use, could not delete.")

# Interactive section to record audio and get AI response
st.markdown("## Record Your Voice:")
if st.button("🎤 Record Audio"):
    audio_input = record_audio()
    if audio_input:
        input_text = convert_audio_to_text(audio_input)
        if input_text:
            st.markdown(f"**You said:** *{input_text}*")
            response_text = generate_response(input_text)
            
            # Display the AI's response with Urdu font and right-to-left alignment
            st.markdown(f"<p class='response-text'>{response_text}</p>", unsafe_allow_html=True)

            audio_bytes = text_to_speech(response_text)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
                play_audio(audio_bytes)

st.markdown("---")

# Footer
st.markdown("<p style='text-align: center; color: white;'>© 2024 Urdu Voice Assistant by Arsalan Ayaz</p>", unsafe_allow_html=True)
