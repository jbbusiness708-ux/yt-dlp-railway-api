from flask import Flask, request, jsonify
import subprocess
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to the yt-dlp API!'

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        output_path = f"{url.split('=')[-1]}.mp4"
        result = subprocess.run(
            [
                'yt-dlp',
                '--cookies', 'cookies.txt',
                '-f', 'bestaudio+best',
                '--merge-output-format', 'mp4',
                url,
                '-o', output_path
            ],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))  # ✅ Ensure it finds cookies.txt
        )

        if result.returncode != 0:
            return jsonify({'error': 'Download failed', 'details': result.stderr}), 500

        return jsonify({'message': 'Download successful', 'file': output_path})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clip', methods=['POST'])
def clip_video():
    video_file = None
    for file in os.listdir():
        if file.endswith(".mp4"):
            video_file = file
            break

    if not video_file:
        return jsonify({'error': 'No .mp4 video found'}), 404

    if not os.path.exists("clip_data.json"):
        return jsonify({'error': 'clip_data.json not found'}), 404

    try:
        with open("clip_data.json", "r") as f:
            clips = json.load(f)

        for idx, clip in enumerate(clips):
            start = clip["start"]
            duration = clip["duration"]
            output_file = f"clip_{idx+1}.mp4"

            result = subprocess.run(
                [
                    "ffmpeg",
                    "-ss", str(start),
                    "-i", video_file,
                    "-t", str(duration),
                    "-c", "copy",
                    output_file
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return jsonify({'error': f'FFmpeg failed on clip {idx+1}', 'details': result.stderr}), 500

        return jsonify({'message': 'All clips created successfully'})

    except Exception as e:
        return jsonify({'error': 'Clip processing failed', 'details': str(e)}), 500

# ✅ Railway port fix
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
