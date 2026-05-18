import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video, providing the important points in a structured way
within 500 words. The transcript is: """

def extract_video_id(youtube_url):
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1].split("?")[0]
    return None

# NEW (works)
def get_transcript(video_id):
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    return " ".join([t.text for t in transcript])

def generate_summary(transcript_text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt + transcript_text}
        ]
    )
    return response.choices[0].message.content

# --- Streamlit UI ---
st.title("🎬 YouTube Transcriber & Summarizer")
st.subheader("Powered by Groq + LLaMA 3.3")

youtube_link = st.text_input("Enter YouTube Video URL:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
if st.button("Get Summary"):
    if not youtube_link:
        st.error("Please enter a YouTube URL.")
    else:
        video_id = extract_video_id(youtube_link)
        if not video_id:
            st.error("Invalid YouTube URL.")
        else:
            with st.spinner("Fetching transcript and summarizing..."):
                try:
                    transcript = get_transcript(video_id)
                    summary = generate_summary(transcript)
                    st.markdown("## 📝 Summary")
                    st.write(summary)
                except Exception as e:
                    st.error(f"Error: {e}")