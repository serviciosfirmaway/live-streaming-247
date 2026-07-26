import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
proceso_activo = None

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/iniciar-live', methods=['POST'])
def iniciar_live():
    global proceso_activo
    datos = request.json
    video = datos.get('video_url')
    rtmp = datos.get('rtmp_url')
    key = datos.get('stream_key')
    
    destino = f"{rtmp}/{key}"
    
    if proceso_activo and proceso_activo.poll() is None:
        proceso_activo.terminate()

    # Comando FFmpeg con bucle y reconexión automáticos
    comando = (
        f"ffmpeg -stream_loop -1 -re -i {video} "
        f"-c:v libx264 -preset ultrafast -b:v 2000k "
        f"-c:a aac -b:a 128k -f flv {destino}"
    )
    
    try:
        proceso_activo = subprocess.Popen(comando, shell=True)
        return jsonify({"status": "success", "mensaje": "🚀 Servidor en línea. ¡Tu transmisión 24/7 está activa!"})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": f"Fallo en el motor: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
