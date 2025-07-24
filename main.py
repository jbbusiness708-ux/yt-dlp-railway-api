from flask import Flask, request, jsonify
import subprocess
import os

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
            ['yt-dlp', '-f', 'bestaudio+best', '--merge-output-format', 'mp4', url, '-o', output_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return jsonify({'error': 'Download failed', 'details': result.stderr}), 500

        return jsonify({'message': 'Download successful', 'file': output_path})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 👇👇 This is the fix for Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
