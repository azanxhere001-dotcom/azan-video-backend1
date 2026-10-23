from __future__ import annotations
import os, re, tempfile, shutil
from pathlib import Path
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel, Field
import yt_dlp

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="Azan Video Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://azanfreetool.netlify.app", "https://azan-video-backend1.azan.blitz.cloud"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

class VideoRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    quality: str | None = None

def validate_youtube_url(raw: str) -> str:
    try:
        parsed = urlparse(raw.strip())
    except Exception:
        raise HTTPException(400, "Please enter a valid YouTube URL.")
    host = (parsed.hostname or "").lower().rstrip(".")
    allowed = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be", "www.youtube-nocookie.com"}
    if parsed.scheme not in {"http", "https"} or host not in allowed:
        raise HTTPException(400, "Only YouTube video URLs are supported.")
    if parsed.username or parsed.password:
        raise HTTPException(400, "URL credentials are not allowed.")
    return raw.strip()

def base_options():
    return {"quiet": True, "no_warnings": True, "noplaylist": True, "ignoreerrors": False, "socket_timeout": 20, "retries": 2}

def friendly_error(exc: Exception) -> str:
    msg = str(exc)
    low = msg.lower()
    if "private video" in low or "sign in" in low or "members-only" in low:
        return "This video is private or access-restricted. Azan cannot access restricted videos."
    if "unavailable" in low or "not available" in low:
        return "This video is unavailable in the current region or has been removed."
    if "requested format is not available" in low:
        return "That quality is not available for this video. Try Best available or 720p."
    return "Could not process this video. Check the URL and try another supported public video."

@app.post("/api/info")
def video_info(req: VideoRequest):
    url = validate_youtube_url(req.url)
    try:
        with yt_dlp.YoutubeDL({**base_options(), "skip_download": True, "extract_flat": False}) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise ValueError("No video information returned")
        heights = sorted({int(f["height"]) for f in info.get("formats", []) if f.get("height") and f.get("vcodec") != "none"}, reverse=True)
        qualities = [f"{h}p" for h in heights if h <= 2160]
        return {"title": info.get("title", "YouTube video"), "thumbnail": info.get("thumbnail"), "duration": info.get("duration"), "qualities": qualities}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(422, friendly_error(exc)) from exc

@app.post("/api/download")
def download_video(req: VideoRequest):
    url = validate_youtube_url(req.url)
    quality = (req.quality or "Best available").strip()
    quality_map = {
        "Best available": "bestvideo*+bestaudio/best",
        "2160p (4K)": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
        "1080p (Full HD)": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "720p (HD)": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "Audio only": "bestaudio/best",
    }
    if quality not in quality_map:
        raise HTTPException(400, "Choose one of the listed quality options.")
    temp_dir = Path(tempfile.mkdtemp(prefix="azan_"))
    opts = {**base_options(), "format": quality_map[quality], "outtmpl": str(temp_dir / "%(title).150B-%(id)s.%(ext)s"), "merge_output_format": "mp4", "max_filesize": 1_500_000_000, "restrictfilenames": True}
    if quality == "Audio only":
        opts["format"] = "bestaudio/best"
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = Path(ydl.prepare_filename(info))
            if not filepath.exists():
                # yt-dlp may merge separate streams into the requested container.
                candidates = [p for p in temp_dir.iterdir() if p.is_file() and p.suffix.lower() in {".mp4", ".mkv", ".webm", ".m4a", ".mp3", ".opus"}]
                if not candidates:
                    raise FileNotFoundError("Downloaded file not found")
                filepath = candidates[0]
        safe_title = re.sub(r"[^A-Za-z0-9._ -]", "", info.get("title") or "azan-video").strip()[:100] or "azan-video"
        ext = filepath.suffix or (".m4a" if quality == "Audio only" else ".mp4")
        download_name = safe_title + ext
        media_type = "audio/mp4" if quality == "Audio only" and ext == ".m4a" else "application/octet-stream"
        def cleanup():
            shutil.rmtree(temp_dir, ignore_errors=True)
        return FileResponse(path=str(filepath), filename=download_name, media_type=media_type, background=BackgroundTask(cleanup))
    except HTTPException:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(422, friendly_error(exc)) from exc

# Serve only the frontend file; do not expose backend source files.
@app.get("/")
def homepage():
    from fastapi.responses import FileResponse as HTMLFileResponse
    return HTMLFileResponse(str(ROOT / "index.html"), media_type="text/html")

