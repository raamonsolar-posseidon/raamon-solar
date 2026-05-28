"""
RA-AMON SOLAR · Servidor Flask
Railway.app deployment
"""
import os, base64, tempfile, shutil, json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response
from motor import generar_propuesta

app = Flask(__name__, static_folder='static')
PORT = int(os.environ.get('PORT', 8080))

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health():
    plantilla = Path('propuesta_plantilla.pptx')
    return jsonify({'status':'ok','plantilla':plantilla.exists(),'version':'2.0'})

@app.route('/generar', methods=['POST'])
def generar():
    data = request.get_json(force=True) or {}

    nombre    = str(data.get('nombre','')).strip()
    paneles   = int(data.get('paneles', 20))
    precio    = int(data.get('precio', 0))
    inv_marca = str(data.get('inv_marca','HUAWEI')).strip()
    inv_modelo= str(data.get('inv_modelo','SUN2000')).strip()
    inv_kw    = int(data.get('inv_kw', 8))
    inv_fase  = str(data.get('inv_fase','BIFÁSICO')).strip()

    # Validaciones
    if not nombre:
        return jsonify({'error':'Nombre del cliente requerido'}), 400
    if precio < 1_000_000:
        return jsonify({'error':'Precio inválido (mín. $1.000.000)'}), 400
    if not (1 <= paneles <= 200):
        return jsonify({'error':'Cantidad de paneles inválida (1-200)'}), 400

    tmp = tempfile.mkdtemp()
    try:
        output_path, datos = generar_propuesta(
            nombre, paneles, precio,
            inv_marca, inv_modelo, inv_kw, inv_fase, tmp
        )
        with open(output_path,'rb') as f:
            b64 = base64.b64encode(f.read()).decode()

        nombre_arch = Path(output_path).name
        return jsonify({
            'ok': True,
            'filename': nombre_arch,
            'data': b64,
            'resumen': {
                'payback':  round(datos['payback'], 2),
                'ahorro20': int(datos['ahorro20']),
                'tir':      round(datos['tir'], 1),
                'van':      int(datos['van']),
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
