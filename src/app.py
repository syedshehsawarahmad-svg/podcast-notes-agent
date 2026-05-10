import streamlit as st
import os
import json
from pathlib import Path
from transcriber import transcribe_audio
from summarizer import generate_podcast_analysis
from video_extractor import extract_audio_from_video
from youtube_extractor import download_youtube_audio

# Configure Streamlit page
st.set_page_config(
    page_title="Podcast Notes Agent",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and header
st.title("🎤 Podcast Notes Agent")
st.caption("📻 Process audio or video, get instant highlights and key takeaways powered by AI")

# Teach mode toggle
col1, col2 = st.columns([0.9, 0.1])
with col2:
    show_teach_mode = st.checkbox("👨🏫", help="Show system prompts and API requests")

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("videos", exist_ok=True)
os.makedirs("downloads", exist_ok=True)

# Initialize session state
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""
if "uploaded_video_name" not in st.session_state:
    st.session_state.uploaded_video_name = ""
if "youtube_url" not in st.session_state:
    st.session_state.youtube_url = ""
if "content_type" not in st.session_state:
    st.session_state.content_type = "podcast"
if "last_system_prompt" not in st.session_state:
    st.session_state.last_system_prompt = ""
if "last_raw_json" not in st.session_state:
    st.session_state.last_raw_json = ""
if "transcription_request" not in st.session_state:
    st.session_state.transcription_request = {}

# Sidebar: File upload
with st.sidebar:
    st.header("📥 Content Source")
    
    input_mode = st.radio(
        "Select Input Source",
        ["🎙️ Podcast Mode", "🎬 Video Mode", "🎥 YouTube Mode"]
    )
    
    if input_mode == "🎙️ Podcast Mode":
        st.session_state.content_type = "podcast"
        st.markdown("Supported formats: MP3, WAV, M4A, OGG, FLAC")
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=["mp3", "wav", "m4a", "ogg", "flac"],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            file_path = f"uploads/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.uploaded_file_name = uploaded_file.name
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            st.markdown(f"**File size:** {uploaded_file.size / 1024 / 1024:.2f} MB")
            
    elif input_mode == "🎬 Video Mode":
        st.session_state.content_type = "video"
        st.markdown("Supported formats: MP4, WebM, MKV")
        uploaded_video = st.file_uploader(
            "Choose a video file",
            type=["mp4", "webm", "mkv"],
            label_visibility="collapsed"
        )
        
        if uploaded_video is not None:
            file_path = f"videos/{uploaded_video.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_video.getbuffer())
            st.session_state.uploaded_video_name = uploaded_video.name
            st.success(f"✅ Uploaded: {uploaded_video.name}")
            st.markdown(f"**File size:** {uploaded_video.size / 1024 / 1024:.2f} MB")
            
    elif input_mode == "🎥 YouTube Mode":
        st.session_state.content_type = "youtube"
        st.markdown("Paste a YouTube URL below")
        youtube_url = st.text_input("YouTube URL")
        if youtube_url:
            st.session_state.youtube_url = youtube_url
            st.success("✅ URL loaded")

    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("""
    1. Select source type and provide file
    2. Click Transcribe (extracts audio if video)
    3. Click "Analyze" to get AI insights
    4. Export your notes
    """)

# Main content area
st.markdown("---")

# Show current file status
if st.session_state.content_type == "podcast" and st.session_state.uploaded_file_name:
    st.info(f"📁 **Current file:** {st.session_state.uploaded_file_name} [PODCAST]")
elif st.session_state.content_type == "video" and st.session_state.uploaded_video_name:
    st.info(f"📁 **Current file:** {st.session_state.uploaded_video_name} [VIDEO]")
elif st.session_state.content_type == "youtube" and st.session_state.youtube_url:
    st.info(f"📁 **Current source:** {st.session_state.youtube_url} [YOUTUBE]")
else:
    st.warning("👉 **Start by uploading a file in the sidebar**")

# Tab 1: Transcription
tab1, tab2, tab3 = st.tabs(["📝 Transcription", "✨ Analysis", "📚 Resources"])

with tab1:
    st.subheader(f"Step 1: Transcribe {st.session_state.content_type.capitalize()}")
    st.markdown("Convert audio to text using OpenAI's Whisper API")
    
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        if st.session_state.content_type == "video":
            btn_text = "🎬 Extract Audio & Transcribe"
        elif st.session_state.content_type == "youtube":
            btn_text = "🎥 Download Audio & Transcribe"
        else:
            btn_text = "🎙️ Transcribe Podcast"
            
        if st.button(btn_text, type="primary", use_container_width=True):
            if st.session_state.content_type == "podcast" and not st.session_state.uploaded_file_name:
                st.error("❌ Please upload a podcast file first")
            elif st.session_state.content_type == "video" and not st.session_state.uploaded_video_name:
                st.error("❌ Please upload a video file first")
            elif st.session_state.content_type == "youtube" and not st.session_state.youtube_url:
                st.error("❌ Please enter a YouTube URL first")
            else:
                if st.session_state.content_type == "video":
                    file_path = f"videos/{st.session_state.uploaded_video_name}"
                    with st.spinner("📥 Extracting audio from video..."):
                        ext_res = extract_audio_from_video(file_path)
                        if not ext_res["success"]:
                            st.error(f"❌ Extraction failed: {ext_res['error']}")
                            st.stop()
                        audio_path = ext_res["file_path"]
                elif st.session_state.content_type == "youtube":
                    with st.spinner("📥 Downloading audio from YouTube..."):
                        ext_res = download_youtube_audio(st.session_state.youtube_url)
                        if not ext_res["success"]:
                            st.error(f"❌ Download failed: {ext_res['error']}")
                            st.stop()
                        audio_path = ext_res["file_path"]
                        st.info(f"📺 **Video Title:** {ext_res['title']}")
                else:
                    audio_path = f"uploads/{st.session_state.uploaded_file_name}"
                
                with st.spinner("🔄 Transcribing audio..."):
                    result = transcribe_audio(audio_path, source_type=st.session_state.content_type)
                    st.session_state.transcription_request = {
                        "model": "whisper-1",
                        "file": audio_path,
                        "language": "en"
                    }
                
                if result["success"]:
                    st.session_state.transcript = result["text"]
                    st.success("✅ Transcription complete!")
                else:
                    st.error(f"❌ Transcription failed: {result['error']}")
    
    # Show transcript if available
    if st.session_state.transcript:
        st.markdown("---")
        st.subheader("📖 Full Transcript")
        
        with st.expander("View full transcript", expanded=True):
            st.text_area(
                "Transcript:",
                value=st.session_state.transcript,
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )
        
        # Transcript stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Word Count", len(st.session_state.transcript.split()))
        with col2:
            st.metric("Character Count", len(st.session_state.transcript))
        with col3:
            est_minutes = len(st.session_state.transcript.split()) / 150
            st.metric("Est. Duration", f"{int(est_minutes)} min")

with tab2:
    st.subheader(f"Step 2: Analyze {st.session_state.content_type.capitalize()}")
    st.markdown("Generate highlights, key takeaways, and summary using GPT-4o")
    
    if st.session_state.transcript:
        if st.button("✨ Generate Highlights & Takeaways", type="primary", use_container_width=True):
            with st.spinner("🤖 Analyzing content with GPT-4o..."):
                analysis = generate_podcast_analysis(st.session_state.transcript, content_type=st.session_state.content_type)
                st.session_state.analysis_result = analysis
                st.session_state.last_system_prompt = analysis.get("system_prompt", "")
                st.session_state.last_raw_json = analysis.get("raw_response", "")
        
        # Show analysis results
        if st.session_state.analysis_result and st.session_state.analysis_result["success"]:
            result = st.session_state.analysis_result
            
            st.success("✅ Analysis complete!")
            st.markdown("---")
            
            # Summary
            st.subheader("📋 Executive Summary")
            st.info(result["summary"])
            
            # Key Takeaways and Highlights in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💡 Key Takeaways")
                for i, takeaway in enumerate(result["takeaways"], 1):
                    st.markdown(f"**{i}. {takeaway}**")
            
            with col2:
                st.subheader("⭐ Highlights")
                for i, highlight in enumerate(result["highlights"], 1):
                    st.markdown(f"**{i}.** _{highlight}_")
            
            # Topics
            st.markdown("---")
            st.subheader("🏷️ Topics Covered")
            topic_cols = st.columns(min(max(len(result["topics"]), 1), 3))
            for i, topic in enumerate(result["topics"]):
                with topic_cols[i % len(topic_cols)]:
                    st.metric("", topic)
            
            # Guest info
            if result["guest_info"]:
                st.markdown("---")
                st.subheader("👤 Guest Information")
                st.write(result["guest_info"])
            
            # Export and reset buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Export Notes", use_container_width=True):
                    # Create export text
                    export_text = f"""CONTENT NOTES EXPORT ({st.session_state.content_type.upper()})
{'='*50}

SUMMARY
{'-'*50}
{result['summary']}

KEY TAKEAWAYS
{'-'*50}
{chr(10).join([f"{i}. {t}" for i, t in enumerate(result['takeaways'], 1)])}

HIGHLIGHTS
{'-'*50}
{chr(10).join([f"{i}. {h}" for i, h in enumerate(result['highlights'], 1)])}

TOPICS COVERED
{'-'*50}
{chr(10).join([f"• {t}" for t in result['topics']])}

GUEST INFORMATION
{'-'*50}
{result['guest_info'] if result['guest_info'] else 'Not mentioned'}

FULL TRANSCRIPT
{'-'*50}
{st.session_state.transcript}

Generated by Podcast Notes Agent
"""
                    st.download_button(
                        label="📥 Download TXT",
                        data=export_text,
                        file_name=f"notes_{st.session_state.content_type}.txt",
                        mime="text/plain"
                    )
            
            with col2:
                if st.button("📊 Export JSON", use_container_width=True):
                    export_json = {
                        "summary": result["summary"],
                        "takeaways": result["takeaways"],
                        "highlights": result["highlights"],
                        "topics": result["topics"],
                        "guest_info": result["guest_info"],
                        "transcript": st.session_state.transcript
                    }
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(export_json, indent=2),
                        file_name=f"notes_{st.session_state.content_type}.json",
                        mime="application/json"
                    )
            
            with col3:
                if st.button("🔄 New Content", use_container_width=True):
                    st.session_state.transcript = ""
                    st.session_state.analysis_result = None
                    st.session_state.uploaded_file_name = ""
                    st.session_state.uploaded_video_name = ""
                    st.session_state.youtube_url = ""
                    st.rerun()
        
        elif st.session_state.analysis_result and not st.session_state.analysis_result["success"]:
            st.error(f"❌ Analysis failed: {st.session_state.analysis_result['error']}")
    
    else:
        st.info("👉 Transcribe content first to see analysis")

with tab3:
    st.subheader("📚 How to Use")
    st.markdown("""
    ### Modes
    - 🎙️ **Podcast Mode**: Upload audio files (MP3, WAV, M4A, OGG, FLAC)
    - 🎬 **Video Mode**: Upload video files (MP4, WebM, MKV)
    - 🎥 **YouTube Mode**: Paste YouTube links
    
    ### Features
    - 🎙️ **Transcription**: Converts audio to text using OpenAI Whisper
    - ✨ **Analysis**: Extracts key insights using GPT-4o
    - 📋 **Summary**: 2-3 paragraph executive summary
    - 💡 **Takeaways**: 3-5 actionable key learnings
    - ⭐ **Highlights**: 3-5 memorable quotes or moments
    - 🏷️ **Topics**: Main themes covered in podcast
    - 👤 **Guest Info**: Information about speakers
    - 💾 **Export**: Download as TXT or JSON
    """)

# TEACH MODE
if show_teach_mode:
    st.markdown("---")
    st.markdown("## 👨🏫 Teach Mode: How It Works")
    
    if st.session_state.last_system_prompt:
        with st.expander("🔧 System Prompt for Analysis", expanded=False):
            st.markdown("**This prompt tells GPT-4o how to analyze content:**")
            st.code(st.session_state.last_system_prompt, language="text")
        
        with st.expander("📤 Raw API Response (JSON)", expanded=False):
            st.markdown("**Raw JSON response from GPT-4o before parsing:**")
            st.code(st.session_state.last_raw_json, language="json")
    
    if st.session_state.transcription_request:
        with st.expander("🎙️ Transcription API Request", expanded=False):
            st.markdown("**Parameters sent to Whisper API:**")
            st.code(json.dumps(st.session_state.transcription_request, indent=2), language="json")
