import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory

app = Flask(_name_)
proceso_activo = None

USUARIOS_PERMITIDOS = {
    "admin": "clavepro2026",
    "cliente1": "tango247",
    "tiktoker": "livevip"
}

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# 🔍 NUEVA RUTA: Permite ver en la página web qué error específico está ocurriendo
@app.route('/ver-errores', methods=['GET'])
def ver_errores():
    if os.path.exists("registro_stream.txt"):
        with open("registro_stream.txt", "r") as f:
            lineas = f.readlines()
            # Nos muestra las últimas 20 líneas del motor para no saturar la pantalla
            return jsonify({"status": "success", "logs": "".join(lineas[-20:])})
    return jsonify({"status": "success", "logs": "No hay transmisiones registradas aún."})

@app.route('/iniciar-live', methods=['POST'])
def iniciar_live():
    global proceso_activo
    datos = request.json
    
    usuario = datos.get('usuario')
    contrasena = datos.get('contrasena')
    
    if usuario not in USUARIOS_PERMITIDOS or USUARIOS_PERMITIDOS[usuario] != contrasena:
        return jsonify({"status": "error", "mensaje": "❌ Acceso denegado."})
        
    video = datos.get('video_url')
    rtmp = datos.get('rtmp_url')
    key = datos.get('stream_key')
    destino = f"{rtmp}/{key}"
    
    if proceso_activo and proceso_activo.poll() is None:
        proceso_activo.terminate()

    # Limpiamos registros anteriores
    if os.path.exists("registro_stream.txt"):
        os.remove("registro_stream.txt")

    # Comando optimizado que guarda todas las fallas en un archivo de texto interno
    comando = (
        f"ffmpeg -stream_loop -1 -re -i '{video}' "
        f"-c:v libx264 -preset ultrafast -b:v 2000k -bufsize 4000k "
        f"-c:a aac -b:a 128k -f flv -tls_verify 0 "
        f"'{destino}' > registro_stream.txt 2>&1"
    )
    
    try:
        proceso_activo = subprocess.Popen(comando, shell=True)
        return jsonify({"status": "success", "mensaje": "🚀 Comando enviado. Monitorea la consola de abajo para ver el estado real."})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": f"Fallo en el motor: {str(e)}"})

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
