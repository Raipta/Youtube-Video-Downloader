from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Allows frontend (any domain) to talk to this backend

# Path to cookies file (used to avoid YouTube's bot-detection on cloud servers)
COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

# ──────────────────────────────────────────────
# ENDPOINT 1: Get video info (title + thumbnail)
# Called when user clicks "Fetch"
# ──────────────────────────────────────────────
@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
    }
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                "title": info.get('title', 'Unknown Title'),
                "thumbnail": info.get('thumbnail', ''),
                "duration": info.get('duration', 0),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# ENDPOINT 2: Get direct download link
# Called when user clicks a Download button
# ──────────────────────────────────────────────
@app.route('/get-download', methods=['POST'])
def get_download():
    data = request.get_json()
    video_url = data.get('url')
    quality = data.get('quality', '360p')

    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    # ── FORMAT SELECTION ──
    # 1080p FIX: YouTube splits 1080p into video+audio streams.
    # We try to get a merged 1080p stream. If not available,
    # we fall back to best available mp4.
    if quality == '1080p':
        # Try progressive (merged) 1080p first, then best mp4
        format_filter = (
            'best[height<=1080][ext=mp4]'     # merged stream (rare but exists)
            '/bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]'  # DASH (needs merge)
            '/best[ext=mp4]'                   # any best mp4
            '/best'
        )
    elif quality == '720p':
        format_filter = (
            'best[height<=720][ext=mp4]'
            '/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]'
            '/best[ext=mp4]'
            '/best'
        )
    elif quality == '360p':
        format_filter = (
            'best[height<=360][ext=mp4]'
            '/worst[ext=mp4]'
            '/best[ext=mp4]'
            '/best'
            '/worst'
        )

    elif quality == 'mp3':
        # For MP3: get best audio stream URL (browser plays/downloads it)
        format_filter = 'bestaudio[ext=m4a]/bestaudio/best'

    elif quality == 'm4a':
        format_filter = 'bestaudio[ext=m4a]/bestaudio/best'

    else:
        format_filter = 'best'

    ydl_opts = {
        'format': format_filter,
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
    }
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # For merged formats (1080p DASH), yt-dlp returns a list of formats
            # We need the video URL from the selected format
            direct_link = None

            if 'requested_formats' in info:
                # DASH stream: two separate URLs - take the video one
                # Note: browser can't merge these natively.
                # For true 1080p merge, ffmpeg on server is needed.
                # Here we return the best single-stream fallback.
                for fmt in info['requested_formats']:
                    if fmt.get('vcodec') != 'none':
                        direct_link = fmt.get('url')
                        break
                if not direct_link:
                    direct_link = info['requested_formats'][0].get('url')
            else:
                direct_link = info.get('url')

            if not direct_link:
                return jsonify({"error": "Could not extract download link"}), 500

            return jsonify({
                "direct_link": direct_link,
                "title": info.get('title', ''),
                "ext": info.get('ext', 'mp4'),
            })

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": "Video unavailable or private: " + str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# Health check (Railway uses this)
# ──────────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "YTGrab backend running ✅"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Backend running on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
