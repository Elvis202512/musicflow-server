import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import yt_dlp
import shutil

app = Flask(__name__)
CORS(app)

# Dossier temporaire pour le serveur
TEMP_DIR = "/tmp/downloads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

YDL_OPTS_BASE = {'quiet': True, 'no_warnings': True, 'nocheckcertificate': True}

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    vid_id = data.get('id')
    mode = data.get('format', 'mp3') # 'mp3' ou 'mp4'
    
    # Nettoyage des vieux fichiers à chaque requête
    for f in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, f))

    opts = {**YDL_OPTS_BASE, 'outtmpl': f'{TEMP_DIR}/%(title)s.%(ext)s'}
    
    if mode == 'mp3':
        opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })
    else:
        opts['format'] = 'bestvideo+bestaudio/best'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid_id}", download=True)
            # Trouver le fichier généré
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            # Si vidéo mp4, le nom est correct tel quel
            final_file = filename if mode == 'mp4' else filename
            
            return send_file(final_file, as_attachment=True)
            
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)