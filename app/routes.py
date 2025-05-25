import glob
import os
import io
from flask import Blueprint, render_template, request, redirect, url_for, make_response, session
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import coleccion_registros
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import load_workbook
from openpyxl.cell import MergedCell
from datetime import datetime
from pymongo import MongoClient

main = Blueprint('main', __name__)

# Conexión a MongoDB local
client = MongoClient('mongodb://localhost:27017/')
db = client['mantenimientos']
coleccion_usuarios = db['usuarios']

# Almacena los archivos de hojas de vida que han sido actualizados
hojas_actualizadas = set()

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        user = coleccion_usuarios.find_one({"usuario": usuario})

        if user and check_password_hash(user['password'], password):
            session['usuario'] = usuario
            return redirect(url_for('main.dashboard'))
        else:
            mensaje = "❌ Usuario o contraseña incorrectos."
            return render_template('login.html', mensaje=mensaje)

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        password = request.form['password']

        if coleccion_usuarios.find_one({"usuario": usuario}):
            mensaje = "❌ El nombre de usuario ya está registrado."
            return render_template('register.html', mensaje=mensaje)

        if coleccion_usuarios.find_one({"email": email}):
            mensaje = "❌ El correo ya está registrado."
            return render_template('register.html', mensaje=mensaje)

        password_hash = generate_password_hash(password)

        nuevo_usuario = {
            "usuario": usuario,
            "email": email,
            "password": password_hash,
            "rol": "usuario",
            "activo": True,
            "creado": datetime.now()
        }

        coleccion_usuarios.insert_one(nuevo_usuario)
        mensaje = "Usuario registrado exitosamente. Ahora puede iniciar sesión."
        return render_template('register.html', mensaje=mensaje)

    return render_template('register.html')

@main.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@main.route('/dashboard')
def dashboard():
    if 'usuario' in session:
        return render_template('dashboard.html', usuario=session['usuario'])
    return redirect(url_for('main.login'))

@main.route('/alertas')
def alertas():
    return render_template('alertas.html')

@main.route('/hojas-de-vida')
def hojas_de_vida():
    archivos = sorted(hojas_actualizadas)
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
    if 'usuario' not in session:
        return redirect(url_for('main.login'))  # Bloquea si no ha iniciado sesión

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
        hojas_actualizadas.add(f"{equipo}.xlsx")

        return redirect(url_for('main.mantenimiento', mensaje='ok'))

    mensaje = request.args.get('mensaje')
    registros = list(coleccion_registros.find().sort("_id", -1))
    return render_template('mantenimiento.html', registros=registros, mensaje=mensaje)

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


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))  # ← Esto lleva al index.html


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

