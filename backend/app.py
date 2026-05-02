import os
import re
import urllib.parse
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import google.generativeai as genai

load_dotenv()

# Set up API keys in your .env file
# YOUTUBE_API_KEY="..."
# GEMINI_API_KEY="..."

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not YOUTUBE_API_KEY or not GEMINI_API_KEY:
    print("Please set YOUTUBE_API_KEY and GEMINI_API_KEY in your .env file.")
    exit(1)

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = urllib.parse.parse_qs(parsed_url.query)
            return p['v'][0]
        if parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        if parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    raise ValueError("Invalid YouTube URL")

def get_video_details(video_id):
    """Fetches video description and details."""
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()
    if not response['items']:
        raise ValueError("Video not found.")
    return response['items'][0]['snippet']

def extract_chapters_from_text(text):
    """Extracts timestamps/chapters from a given text (description or comment)."""
    pattern = re.compile(r'(?:(\d{1,2}):)?(\d{1,2}):(\d{2})(?:\s+-?\s+)?(.+)')
    chapters = []
    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            chapters.append(line.strip())
    return chapters

def get_chapters_from_comments(video_id):
    """Fetches top comments searching for timestamps."""
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            order="relevance",
            maxResults=10
        )
        response = request.execute()
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            chapters = extract_chapters_from_text(comment)
            if len(chapters) > 2: # At least a few timestamps
                return chapters
    except Exception as e:
        print(f"Error fetching comments: {e}")
    return []

def get_transcript(video_id):
    """Fetches the transcript of the video."""
    try:
        api = YouTubeTranscriptApi()
        # By default, fetch tries "en" first. You can add more languages if needed.
        transcript_obj = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
        transcript = " ".join([snippet.text for snippet in transcript_obj.snippets])
        return transcript
    except Exception as e:
        raise ValueError(f"Could not retrieve transcript: {e}")

def generate_notes(transcript, chapters):
    """Calls OpenAI API to generate notes."""
    system_prompt = """You are an expert technical educator and master note-taker. I will provide a transcript of a video. Your goal is to process this information into a high-density, structured study guide so I can understand everything without watching the video.
Your Task:
Translate & Decipher: Translate the content into high-quality, professional English. If the speaker uses 'Hinglish' (mixing Hindi with English technical terms), ensure the technical terms are preserved and placed in the correct context.
Master Structure: Once translated, organize the information into the following structure:
Chapter Name
Detailed Hierarchical Notes of that chapter its concepts and example explained in depth.
Add code snippets of the concepts and their examples in all the chapters , if you can't make a code snippet based on the transcript then make your own examples , referring to the concepts explained in the transcript
Tell me what new concepts are introduced that weren't in the previous videos .
Understanding Quiz: 10 challenging questions.

Divide the video into following chapters:
{chapters}"""

    if not chapters:
        system_chapters = "The video chapters are not provided. Please analyze the transcript and intelligently divide it into logical chapters."
    else:
        system_chapters = "\n".join(chapters)

    prompt = system_prompt.format(chapters=system_chapters)

    model = genai.GenerativeModel('gemini-flash-latest')
    full_prompt = f"{prompt}\n\nHere is the transcript:\n\n{transcript}"
    
    response = model.generate_content(full_prompt)
    return response.text

def main():
    url = input("Enter YouTube Video URL: ").strip()
    try:
        video_id = get_video_id(url)
        print(f"[*] Processing Video ID: {video_id}")

        print("[*] Fetching video details...")
        snippet = get_video_details(video_id)
        description = snippet['description']
        
        print("[*] Looking for chapters...")
        chapters = extract_chapters_from_text(description)
        if chapters:
            print("[*] Chapters found in description.")
        else:
            print("[*] Chapters not in description. Checking comments...")
            chapters = get_chapters_from_comments(video_id)
            if chapters:
                print("[*] Chapters found in comments.")
            else:
                print("[*] No chapters found. The AI will generate them.")

        print("[*] Fetching transcript...")
        transcript = get_transcript(video_id)

        print("[*] Generating AI notes (this may take a minute)...")
        notes = generate_notes(transcript, chapters)

        with open(f"{video_id}_notes.md", "w") as f:
            f.write(notes)
        print(f"[*] Done! Notes saved to {video_id}_notes.md")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
