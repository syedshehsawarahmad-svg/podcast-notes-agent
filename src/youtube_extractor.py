import os
import yt_dlp
import uuid

def download_youtube_audio(url: str) -> dict:
    """
    Downloads audio from a YouTube video.
    
    Args:
        url: URL of the YouTube video
    
    Returns:
        Dictionary with keys:
        - success (bool): Whether extraction was successful
        - file_path (str): Path to the extracted audio file
        - duration (float): Duration of the audio in seconds (if available)
        - title (str): Title of the video
        - error (str): Error message if failed
    """
    try:
        os.makedirs("downloads", exist_ok=True)
        
        file_id = str(uuid.uuid4())[:8]
        output_template = f"downloads/youtube_audio_{file_id}.%(ext)s"
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            return {
                "success": True,
                "file_path": filename,
                "duration": info.get("duration", 0),
                "title": info.get("title", "Unknown Title"),
                "error": None
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to download YouTube audio: {str(e)}",
            "file_path": None,
            "duration": 0,
            "title": ""
        }
