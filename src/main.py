import os
from dotenv import load_dotenv
from openai import OpenAI
from transcriber import transcribe_audio
from summarizer import generate_podcast_analysis
from video_extractor import extract_audio_from_video
from youtube_extractor import download_youtube_audio

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERROR: OPENAI_API_KEY not found in .env")
    print("Please create a .env file with your OpenAI API key")
    exit(1)

client = OpenAI(api_key=api_key)

print("✅ Podcast Notes Agent initialized. API key loaded.")


def process_video(video_path: str):
    """
    Process a video file: extract audio, transcribe, and analyze.
    """
    print(f"\n{'='*60}")
    print(f"🎬 PROCESSING VIDEO: {video_path}")
    print('='*60)
    
    # Extract audio
    print("\n📥 Extracting audio from video...")
    extraction = extract_audio_from_video(video_path)
    if not extraction["success"]:
        print(f"❌ Extraction error: {extraction['error']}")
        return
        
    audio_path = extraction["file_path"]
    print(f"✅ Audio extracted successfully to: {audio_path}")
    
    # Transcribe
    print("\n📝 STEP 1: TRANSCRIBING AUDIO")
    transcript_result = transcribe_audio(audio_path, source_type="video")
    if not transcript_result["success"]:
        print(f"❌ Transcription error: {transcript_result['error']}")
        return
        
    transcript = transcript_result["text"]
    print(f"✅ Transcription complete!")
    
    # Analyze
    print("\n📊 STEP 2: ANALYZING CONTENT")
    analysis_result = generate_podcast_analysis(transcript, content_type="video")
    if not analysis_result["success"]:
        print(f"❌ Analysis error: {analysis_result['error']}")
        return
        
    print("✅ Analysis complete!\n")
    
    # Display results
    print(f"{'='*60}")
    print("📋 SUMMARY")
    print('='*60)
    print(analysis_result["summary"])
    
    print(f"\n{'='*60}")
    print("💡 KEY TAKEAWAYS")
    print('='*60)
    for i, takeaway in enumerate(analysis_result["takeaways"], 1):
        print(f"{i}. {takeaway}")
    
    print(f"\n{'='*60}")
    print("✨ VIDEO NOTES GENERATED SUCCESSFULLY")
    print('='*60)


def process_youtube(url: str):
    """
    Process a YouTube video: download audio, transcribe, and analyze.
    """
    print(f"\n{'='*60}")
    print(f"🎥 PROCESSING YOUTUBE: {url}")
    print('='*60)
    
    # Extract audio
    print("\n📥 Downloading audio from YouTube...")
    extraction = download_youtube_audio(url)
    if not extraction["success"]:
        print(f"❌ Download error: {extraction['error']}")
        return
        
    audio_path = extraction["file_path"]
    print(f"✅ Audio downloaded successfully to: {audio_path}")
    print(f"📺 Title: {extraction['title']}")
    
    # Transcribe
    print("\n📝 STEP 1: TRANSCRIBING AUDIO")
    transcript_result = transcribe_audio(audio_path, source_type="youtube")
    if not transcript_result["success"]:
        print(f"❌ Transcription error: {transcript_result['error']}")
        return
        
    transcript = transcript_result["text"]
    print(f"✅ Transcription complete!")
    
    # Analyze
    print("\n📊 STEP 2: ANALYZING CONTENT")
    analysis_result = generate_podcast_analysis(transcript, content_type="youtube")
    if not analysis_result["success"]:
        print(f"❌ Analysis error: {analysis_result['error']}")
        return
        
    print("✅ Analysis complete!\n")
    
    # Display results
    print(f"{'='*60}")
    print("📋 SUMMARY")
    print('='*60)
    print(analysis_result["summary"])
    
    print(f"\n{'='*60}")
    print("💡 KEY TAKEAWAYS")
    print('='*60)
    for i, takeaway in enumerate(analysis_result["takeaways"], 1):
        print(f"{i}. {takeaway}")
    
    print(f"\n{'='*60}")
    print("✨ YOUTUBE NOTES GENERATED SUCCESSFULLY")
    print('='*60)


def main():
    """
    Main function to demonstrate the podcast notes agent.
    
    This function:
    1. Transcribes a podcast audio file
    2. Analyzes the transcript
    3. Displays results in formatted output
    """
    
    # Example audio file path
    sample_audio = "uploads/sample_podcast.mp3"
    
    # Check if file exists
    if not os.path.exists(sample_audio):
        print(f"\n⚠️  Sample audio file not found: {sample_audio}")
        print("To test, please place an audio file in the uploads/ directory")
        print("Supported formats: mp3, wav, m4a, ogg, flac")
        return
    
    print(f"\n{'='*60}")
    print("📝 STEP 1: TRANSCRIBING PODCAST")
    print('='*60)
    
    # Transcribe audio
    transcript_result = transcribe_audio(sample_audio)
    
    if not transcript_result["success"]:
        print(f"❌ Transcription error: {transcript_result['error']}")
        return
    
    transcript = transcript_result["text"]
    print(f"✅ Transcription complete!")
    print(f"📊 Transcript length: {len(transcript)} characters")
    print(f"\n📖 Transcript preview (first 300 chars):\n{transcript[:300]}...\n")
    
    # Analyze transcript
    print(f"{'='*60}")
    print("📊 STEP 2: ANALYZING PODCAST")
    print('='*60)
    
    analysis_result = generate_podcast_analysis(transcript)
    
    if not analysis_result["success"]:
        print(f"❌ Analysis error: {analysis_result['error']}")
        return
    
    print("✅ Analysis complete!\n")
    
    # Display results
    print(f"{'='*60}")
    print("📋 SUMMARY")
    print('='*60)
    print(analysis_result["summary"])
    
    print(f"\n{'='*60}")
    print("💡 KEY TAKEAWAYS")
    print('='*60)
    for i, takeaway in enumerate(analysis_result["takeaways"], 1):
        print(f"{i}. {takeaway}")
    
    print(f"\n{'='*60}")
    print("⭐ HIGHLIGHTS")
    print('='*60)
    for i, highlight in enumerate(analysis_result["highlights"], 1):
        print(f"{i}. {highlight}")
    
    print(f"\n{'='*60}")
    print("🏷️  TOPICS COVERED")
    print('='*60)
    for topic in analysis_result["topics"]:
        print(f"• {topic}")
    
    if analysis_result["guest_info"]:
        print(f"\n{'='*60}")
        print("👤 GUEST INFORMATION")
        print('='*60)
        print(analysis_result["guest_info"])
    
    print(f"\n{'='*60}")
    print("✨ PODCAST NOTES GENERATED SUCCESSFULLY")
    print('='*60)


if __name__ == "__main__":
    main()
