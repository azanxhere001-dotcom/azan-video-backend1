AZAN — YouTube backend starter

WHAT'S INCLUDED
- Azan responsive website with its original branding
- YouTube thumbnail preview
- Description generator, hashtag helper, and copy buttons
- FastAPI backend with /api/info and /api/download endpoints
- Quality choices: Best available, 4K, 1080p, 720p, 480p, audio only
- Friendly error messages for unsupported or restricted videos

QUICK START — WINDOWS
1. Install Python 3.10+ from https://www.python.org/downloads/ (tick 'Add Python to PATH').
2. Double-click START_AZAN_WINDOWS.bat. On first run it installs Python packages automatically.
3. Open http://127.0.0.1:8000 in your browser and keep the black terminal window open.
4. FFmpeg is recommended/required to merge separate high-quality video and audio streams; install it if downloads fail during merging.

QUICK START — MAC / LINUX
1. Install Python 3.10+ and FFmpeg.
2. Run: bash START_AZAN_MAC_LINUX.sh
3. Open http://127.0.0.1:8000 in your browser.

RUN LOCALLY (manual option; Python 3.10+ recommended)
1. Install FFmpeg on your computer (required to combine video/audio streams).
2. Open a terminal in the extracted azan-website folder.
3. Create a virtual environment (optional but recommended):
   Windows: py -m venv .venv && .venv\Scripts\activate
   macOS/Linux: python3 -m venv .venv && source .venv/bin/activate
4. Install packages:
   pip install -r requirements.txt
5. Start the site and backend from the azan-website folder:
   uvicorn backend.app:app --host 127.0.0.1 --port 8000
6. Open http://127.0.0.1:8000 in your browser.
   Do not open index.html directly; API calls need the server.

DOCKER OPTION
From this folder run:
  docker build -t azan-website .
  docker run --rm -p 8000:8000 azan-website
Then visit http://127.0.0.1:8000.

IMPORTANT
- This is backend code you must run/host; it is not already published online.
- Use only videos you own or are explicitly authorized to download. Respect YouTube's Terms of Service, copyright, local law, and the rights of creators.
- It does not bypass private-video restrictions, DRM, paid access, or sign-in requirements.
- Video availability and formats vary by region, account restrictions, and source changes. Quality is the closest available option at or below the selected maximum, not a guarantee that every resolution exists.
- Public deployment needs HTTPS, rate limiting, request limits, monitoring, and appropriate legal review. Do not expose an unrestricted download service to the public without safeguards.
