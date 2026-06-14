import re
from youtube_transcript_api import YouTubeTranscriptApi
try:
    from pytube import YouTube
except ImportError:
    YouTube = None


def get_video_id(url: str) -> str | None:
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_metadata(video_id: str) -> dict:
    data = {"title": "", "channel": "", "duration": 0, "thumbnail": ""}
    if YouTube is None:
        return data
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        data["title"] = yt.title or ""
        data["channel"] = yt.author or ""
        data["duration"] = yt.length or 0
        data["thumbnail"] = yt.thumbnail_url or ""
    except Exception:
        pass
    return data


def get_transcript(url: str) -> tuple[str | None, str | None]:
    video_id = get_video_id(url)
    if not video_id:
        return None, None

    try:
        api = YouTubeTranscriptApi()
        transcripts = api.list(video_id)
    except Exception:
        return None, video_id

    transcript = None
    for t in transcripts:
        if t.language_code == "en":
            if t.is_generated:
                if transcript is None:
                    transcript = t.fetch()
            else:
                transcript = t.fetch()
                break

    return transcript, video_id


def format_transcript(transcript) -> str:
    if transcript is None:
        return ""
    txt = ""
    for item in transcript:
        try:
            text = item.text if hasattr(item, "text") else item.get("text", "")
            start = item.start if hasattr(item, "start") else item.get("start", 0)
            txt += f"Text: {text} Start: {start}\n"
        except (KeyError, AttributeError):
            pass
    return txt
