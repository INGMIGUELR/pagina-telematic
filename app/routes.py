import glob
import os
import io
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from app.db import coleccion_registros
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import load_workbook
from openpyxl.cell import MergedCell
from datetime import datetime

main = Blueprint('main', __name__)

# Almacena los archivos de hojas de vida que han sido actualizados
hojas_actualizadas = set()

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/login')
def login():
    return render_template('login.html')

@main.route('/register')
def register():
    return render_template('register.html')

@main.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/alertas')
def alertas():
    return render_template('alertas.html')


@main.route('/hojas-de-vida')
def hojas_de_vida():
    archivos = sorted(hojas_actualizadas)  # Orden ascendente alfabético
    return render_template('hojas_de_vida.html', archivos=archivos)

@main.route('/limpiar-historial', methods=['POST'])
def limpiar_historial():
    coleccion_registros.delete_many({})
    hojas_actualizadas.clear()
    return redirect(url_for('main.hojas_de_vida'))

@main.route('/plan-general')
def plan_general():
    return render_template('plan_general.html')


@main.route('/mantenimiento', methods=['GET', 'POST'])
def mantenimiento():
    if request.method == 'POST':
        equipo = request.form['equipo']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']

        nuevo_registro = {
            "equipo": equipo,
            "fecha": fecha,
            "descripcion": descripcion
        }

        coleccion_registros.insert_one(nuevo_registro)
        actualizar_hoja_vida(equipo, fecha, descripcion)

        # Guardamos el archivo actualizado en el conjunto
        hojas_actualizadas.add(f"{equipo}.xlsx")

        return redirect(url_for('main.mantenimiento'))

    registros = list(coleccion_registros.find().sort("_id", -1))
    return render_template('mantenimiento.html', registros=registros)

@main.route('/mantenimientos-mensuales')
def mantenimientos_mensuales():
    registros = list(coleccion_registros.find())
    registros_por_mes = {}

    

    for reg in registros:
        try:
            fecha = datetime.strptime(reg['fecha'], '%Y-%m-%d')
        except Exception as e:
            print(f"⚠️ Fecha inválida en registro: {reg}, error: {e}")
            continue

        mes = fecha.strftime('%Y-%m')
        if mes not in registros_por_mes:
            registros_por_mes[mes] = []
        registros_por_mes[mes].append(reg)

    return render_template('mantenimientos_mensuales.html', registros_por_mes=registros_por_mes)
    return render_template("plan_general.html", datos_plan=datos, totales_mes=totales, total_general=total)


def actualizar_hoja_vida(equipo_id, fecha, descripcion):
    carpeta = os.path.join("static", "hojas_vida")
    archivo_equipo = os.path.join(carpeta, f"{equipo_id}.xlsx")

    if not os.path.exists(archivo_equipo):
        print(f"❌ No se encontró la hoja de vida para el equipo: {equipo_id}")
        return

    wb = load_workbook(archivo_equipo)
    ws = wb.active

    fila = 33
    while True:
        celda = ws[f"A{fila}"]
        if not isinstance(celda, MergedCell) and celda.value is None:
            break
        fila += 1

    ws[f"A{fila}"] = fecha
    ws[f"C{fila}"] = descripcion
    ws[f"M{fila}"] = "SV Romero Romero Miguel Ángel"


    wb.save(archivo_equipo)

