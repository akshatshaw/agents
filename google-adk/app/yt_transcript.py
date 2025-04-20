from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(yt_url:str)-> str:
    """
    Extracts the video ID from a given YouTube URL.

    This function supports both standard YouTube URLs (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
    and shortened URLs (e.g., https://youtu.be/VIDEO_ID). It parses the input URL and extracts the 
    unique video identifier used to fetch metadata such as transcripts, titles, etc.

    Parameters:
        yt_url (str): The full URL of the YouTube video.

    Returns:
        str: The extracted YouTube video ID if successful; otherwise, returns None.

    Example:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    parsed_url = urlparse(yt_url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    return None

def get_youtube_transcript(yt_url : str)-> dict:
    """
    Retrieves the transcript (subtitles) of a YouTube video as plain text.

    This function takes a YouTube video URL and optional language code,
    extracts the video ID, and uses the YouTube Transcript API to fetch 
    the transcript (if available). It returns the transcript as a single 
    concatenated string.

    Parameters:
        yt_url (str): The full URL of the YouTube video.
        lang (str, optional): Preferred language code for the transcript. Defaults to 'en'.

    Returns:
        dict: A dictionary containing the transcript under the key "result".

    Raises:
        ValueError: If the video ID cannot be extracted or the transcript is not available.

    Example:
        >>> get_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        {'result': 'Never gonna give you up Never gonna let you down ...'}
    """
    video_id = extract_video_id(yt_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    full_text = " ".join([t["text"] for t in transcript])
    return {"result" : full_text}

if __name__ == "__main__":
    yt_url = "https://www.youtube.com/watch?v=sBuoMkJsMsA"
    transcript = get_youtube_transcript(yt_url)
    print(transcript)