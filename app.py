# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # Used to allow requests from your Blogger page
import subprocess # To run yt-dlp as a command-line tool
import json # To parse yt-dlp's JSON output
import os # For environment variables, if needed

app = Flask(__name__)
# Enable CORS for all origins. In a production app, you'd restrict this to your Blogger domain.
CORS(app)

@app.route('/')
def home():
    return "Video Downloader Backend is running!"

@app.route('/download-video', methods=['POST'])
def download_video():
    """
    API endpoint to handle video download requests.
    Expects a JSON payload with 'videoUrl' and 'platform'.
    """
    data = request.get_json()
    if not data or 'videoUrl' not in data:
        return jsonify({"message": "Missing videoUrl in request"}), 400

    video_url = data['videoUrl']
    platform = data.get('platform', 'Unknown') # Get platform, default to 'Unknown'

    print(f"Received request for URL: {video_url} from platform: {platform}")

    try:
        # --- IMPORTANT: This is where yt-dlp is called ---
        # We use subprocess to run yt-dlp as a command-line tool.
        # The '-j' flag makes yt-dlp output video information in JSON format.
        # The '--no-warnings' flag suppresses warnings.
        # The '--skip-download' flag tells yt-dlp NOT to download the video itself,
        # but just to give us the information, including the direct URL.
        # We're specifically looking for the 'url' field in the JSON output,
        # which is often the direct stream URL.
        
        # Note: yt-dlp might return multiple formats. For simplicity, we'll try to get the best quality URL.
        # For more advanced use, you'd parse the 'formats' array to pick a specific resolution/format.
        
        # Example command: yt-dlp -j --no-warnings --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        command = [
            "yt-dlp",
            "-j",             # Output JSON
            "--no-warnings",  # Suppress warnings
            "--skip-download",# Don't download, just get info
            video_url
        ]
        
        # Run the command and capture its output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Parse the JSON output from yt-dlp
        video_info = json.loads(result.stdout)
        
        # Extract the direct download URL and title
        # yt-dlp provides a 'url' field which is often the direct stream URL for the best format.
        # For more control, you'd iterate through video_info['formats']
        download_url = video_info.get('url')
        video_title = video_info.get('title', 'Video')

        if download_url:
            print(f"Found download URL: {download_url}")
            return jsonify({
                "success": True,
                "downloadUrl": download_url,
                "title": video_title,
                "message": "Download link retrieved successfully."
            }), 200
        else:
            print("No direct download URL found by yt-dlp.")
            return jsonify({"success": False, "message": "Could not find a direct download link for this video."}), 500

    except subprocess.CalledProcessError as e:
        print(f"yt-dlp error: {e.stderr}")
        return jsonify({"success": False, "message": f"Error processing video: {e.stderr.strip()}"}), 500
    except json.JSONDecodeError:
        print("Error parsing yt-dlp output as JSON.")
        return jsonify({"success": False, "message": "Error parsing video information."}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"success": False, "message": f"An unexpected error occurred: {str(e)}"}), 500

# This block allows you to run the Flask app directly
if __name__ == '__main__':
    # You can change the port if 5000 is already in use
    app.run(debug=True, port=5000)