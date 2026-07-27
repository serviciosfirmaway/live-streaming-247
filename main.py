import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
proceso_activo = None

# 📋 ESTA ES TU LISTA MAESTRA DE CLIENTES ACTIVOS (TÚ CONTROLAS ESTO)
# Puedes cambiar estos nombres y claves por los de tus clientes que te paguen
USUARIOS_PERMITIDOS = {
    "admin": "clavepro2026",    # Tu cuenta de acceso
    "cliente1": "tango247",     # Primer cliente de prueba
    "tiktoker": "livevip"       # Segundo cliente
}

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# 🔐 FILTRO DE SEGURIDAD: Verifica si el cliente tiene permiso antes de transmitir
@app.route('/iniciar-live', methods=['POST'])
def iniciar_live():
    global proceso_activo
    datos = request.json
    
    usuario = datos.get('usuario')
    contrasena = datos.get('contrasena')
    
    # Comprobamos si el usuario existe y si la contraseña coincide
    if usuario not in USUARIOS_PERMITIDOS or USUARIOS_PERMITIDOS[usuario] != contrasena:
        return jsonify({"status": "error", "mensaje": "❌ Acceso denegado. Usuario o contraseña incorrectos o cuenta vencida."})
        
    video = datos.get('video_url')
    rtmp = datos.get('rtmp_url')
    key = datos.get('stream_key')
    destino = f"{rtmp}/{key}"
    
    if proceso_activo and proceso_activo.poll() is None:
        proceso_activo.terminate()

    comando = (
        f"ffmpeg -stream_loop -1 -re -i {video} "
        f"-c:v libx264 -preset ultrafast -b:v 2000k "
        f"-c:a aac -b:a 128k -f flv {destino}"
    )
    
    try:
        proceso_activo = subprocess.Popen(comando, shell=True)
        return jsonify({"status": "success", "mensaje": "🚀 ¡Acceso verificado! Tu transmisión 24/7 está activa."})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": f"Fallo en el motor: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
