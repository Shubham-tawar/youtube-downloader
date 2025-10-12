from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_video():
    url = request.form.get("url")
    format_choice = request.form.get("format")

    if not url:
        return " Please enter a valid YouTube URL."

    unique_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.%(ext)s")

    if format_choice == "video":
        ydl_opts = {
            'ffmpeg_location': r'C:\Program Files (x86)\ffmpeg\bin',
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }],
            "postprocessor_args": [
                "-c:v", "libx264",  # Re-encode video to H.264
                "-c:a", "aac",      # Re-encode audio to AAC
                "-strict", "experimental"
            ],
        }

    elif format_choice == "audio":
        ydl_opts = {
            'ffmpeg_location': r'C:\Program Files (x86)\ffmpeg\bin',
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            
        }
    else:
        return " Invalid format selected."

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)
            file_name = os.path.splitext(file_name)[0]

            # Adjust extension depending on format
            if format_choice == "video":
                file_path = f"{file_name}.mp4"
            else:
                file_path = f"{file_name}.mp3"

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f" Error: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)