from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Leer el archivo Excel
file_path = r'C:\Users\USUARIO\Dropbox\CEFIP\organizacion\codigos_web\tarifas\tarifas_gas.xlsx'
df = pd.read_excel(file_path)

@app.route('/')
def index():
    # Obtener listas únicas para el formulario
    anios = df['Anio'].unique().tolist()
    provincias = df['Provincia'].unique().tolist()
    return render_template('index.html', anios=anios, provincias=provincias)

@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json
    anio = data.get('anio')
    provincia = data.get('provincia')
    ciudad = data.get('ciudad')
    consumo = data.get('consumo')
    ingresos = data.get('ingresos', '.')

    # Convertir a tipo numérico por si acaso viene como string
    try:
        consumo = float(consumo)
    except ValueError:
        return jsonify({'error': 'La cantidad ingresada no es válida'}), 400

    if consumo < 0:
        return jsonify({'error': 'La cantidad ingresada no es válida'}), 400

    # Filtrar el DataFrame por año, provincia y ciudad
    df_filtered = df[(df['Anio'] == int(anio)) & (df['Provincia'] == provincia) & (df['Ciudad'] == ciudad)]

    if ciudad != "Ciudad C" and (ciudad != "Ciudad B" or ingresos != '.'):
        df_filtered = df_filtered[df_filtered['Ingresos'] == ingresos]
    
    # Filtrar por rango de consumo
    tarifa = df_filtered[(df_filtered['Consumo_min'] <= consumo) & (df_filtered['Consumo_max'] >= consumo)]

    if tarifa.empty:
        return jsonify({'error': 'No se encontró tarifa para el consumo especificado en la ciudad seleccionada'}), 400

    tarifa_unitaria = tarifa['Tarifa'].values[0]
    total = round(consumo * tarifa_unitaria, 2)  # Redondear a 2 decimales

    return jsonify({'total': total, 'message': f'Su gasto en consumo de gas es de {total}*', 'note': 'Puede no ser el valor de la factura ya que no contempla impuestos y tasas que los gobiernos pueden cobrar.'})

if __name__ == '__main__':
    app.run(debug=True)
