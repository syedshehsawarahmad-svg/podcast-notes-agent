import os
from moviepy.editor import VideoFileClip
import uuid

def extract_audio_from_video(video_path: str) -> dict:
    """
    Extracts the audio track from a video file and saves it as an MP3.
    
    Args:
        video_path: Path to the video file (MP4, WebM, MKV)
    
    Returns:
        Dictionary with keys:
        - success (bool): Whether extraction was successful
        - file_path (str): Path to the extracted audio file
        - duration (float): Duration of the audio in seconds
        - error (str): Error message if failed
    """
    try:
        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file not found: {video_path}", "file_path": None, "duration": 0}
            
        os.makedirs("downloads", exist_ok=True)
        
        # Generate a unique output path
        file_id = str(uuid.uuid4())[:8]
        output_filename = f"downloads/extracted_audio_{file_id}.mp3"
        
        # Load video and extract audio
        video = VideoFileClip(video_path)
        audio = video.audio
        
        if audio is None:
            return {"success": False, "error": "No audio track found in the video.", "file_path": None, "duration": 0}
            
        duration = video.duration
        
        # Write audio to file
        # logger=None silences the moviepy progress bar
        audio.write_audiofile(output_filename, codec='libmp3lame', logger=None)
        
        # Close the clips to release file locks
        audio.close()
        video.close()
        
        return {
            "success": True,
            "file_path": output_filename,
            "duration": duration,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract audio: {str(e)}",
            "file_path": None,
            "duration": 0
        }
