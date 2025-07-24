from flask import Flask, request, jsonify
import subprocess, uuid

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error":"Missing URL"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    try:
        subprocess.run([
            "yt-dlp", "-f", "best[ext=mp4]",
            "-o", filename, url
        ], check=True)
        return jsonify({
            "status": "success",
            "file_url": f"{request.host_url}{filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
