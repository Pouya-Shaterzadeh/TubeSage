import re
import tempfile
import os
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi


def get_video_id(url: str) -> str | None:
    patterns = [
        # Standard watch URL: youtube.com/watch?v=VIDEO_ID
        r'(?:https?://)?(?:www\.|m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        # Shortened: youtu.be/VIDEO_ID
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
        # Embed: youtube.com/embed/VIDEO_ID
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        # Shorts: youtube.com/shorts/VIDEO_ID
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        # Live: youtube.com/live/VIDEO_ID
        r'(?:https?://)?(?:www\.)?youtube\.com/live/([a-zA-Z0-9_-]{11})',
        # Watch with extra params: youtube.com/watch?param=val&v=VIDEO_ID
        r'(?:https?://)?(?:www\.|m\.)?youtube\.com/watch\?[^"\s]*v=([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_metadata(video_id: str) -> dict:
    data = {"title": "", "channel": "", "duration": 0, "thumbnail": ""}
    try:
        import yt_dlp
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            data["title"] = info.get("title", "")
            data["channel"] = info.get("uploader", "")
            data["duration"] = info.get("duration", 0) or 0
            data["thumbnail"] = info.get("thumbnail", "")
    except Exception:
        pass
    return data


def _fetch_transcript_api(url: str) -> tuple | None:
    """Try youtube-transcript-api (may be blocked on cloud servers)."""
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


def _fetch_transcript_ytdlp(url: str) -> tuple | None:
    """Fallback: use yt-dlp to extract subtitles (bypasses cloud IP blocks)."""
    video_id = get_video_id(url)
    if not video_id:
        return None, None

    try:
        import yt_dlp
    except ImportError:
        return None, video_id

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "vtt",
            "outtmpl": os.path.join(tmpdir, "%(id)s"),
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception:
            return None, video_id

        # Find downloaded subtitle file
        subtitle_files = list(Path(tmpdir).glob(f"*{video_id}*.en.vtt"))
        if not subtitle_files:
            return None, video_id

        vtt_path = subtitle_files[0]
        vtt_text = vtt_path.read_text(encoding="utf-8")

        # Parse VTT into (text, start) tuples
        parsed = _parse_vtt(vtt_text)
        if not parsed:
            return None, video_id

        # Return as list of dict-like objects matching youtube-transcript-api format
        transcript = [{"text": text, "start": start} for text, start in parsed]
        return transcript, video_id


def _parse_vtt(vtt_text: str) -> list:
    """Parse WebVTT content into list of (text, start_time) tuples."""
    import re as _re

    results = []
    # Remove header
    lines = vtt_text.split("\n")
    # Remove WEBVTT header and blank lines
    i = 0
    while i < len(lines) and (lines[i].strip().startswith("WEBVTT") or not lines[i].strip()):
        i += 1

    cue_pattern = _re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}"
    )
    while i < len(lines):
        line = lines[i].strip()
        match = cue_pattern.match(line)
        if match:
            start_time = _vtt_time_to_seconds(match.group(1))
            i += 1
            # Collect text lines until blank line or next cue
            text_parts = []
            while i < len(lines) and lines[i].strip():
                # Remove VTT tags like <c> or </c>
                clean = _re.sub(r"<[^>]+>", "", lines[i].strip())
                if clean:
                    text_parts.append(clean)
                i += 1
            if text_parts:
                results.append((" ".join(text_parts), start_time))
        else:
            i += 1
    return results


def _vtt_time_to_seconds(timestamp: str) -> float:
    """Convert 'HH:MM:SS.mmm' to seconds."""
    parts = timestamp.split(":")
    h, m = int(parts[0]), int(parts[1])
    s_ms = parts[2].split(".")
    s = int(s_ms[0])
    ms = int(s_ms[1]) if len(s_ms) > 1 else 0
    return h * 3600 + m * 60 + s + ms / 1000


def get_transcript(url: str) -> tuple:
    """Fetch transcript, trying youtube-transcript-api first, then yt-dlp fallback."""
    # Try youtube-transcript-api first
    transcript, video_id = _fetch_transcript_api(url)
    if transcript is not None:
        return transcript, video_id

    # Fallback to yt-dlp
    transcript, video_id = _fetch_transcript_ytdlp(url)
    if transcript is not None:
        return transcript, video_id

    return None, video_id


def format_transcript(transcript) -> str:
    if transcript is None:
        return ""
    txt = ""
    for item in transcript:
        try:
            if isinstance(item, dict):
                text = item.get("text", "")
                start = item.get("start", 0)
            else:
                text = item.text if hasattr(item, "text") else ""
                start = item.start if hasattr(item, "start") else 0
            txt += f"Text: {text} Start: {start}\n"
        except (KeyError, AttributeError, TypeError):
            pass
    return txt
