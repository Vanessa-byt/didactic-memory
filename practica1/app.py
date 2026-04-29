from flask import Flask, render_template, request
from pymongo import MongoClient
from typing import Optional, Dict
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["usuariosDB"]                
usuarios_collection = db["usuarios"]     

def obtener_usuario(email: str, contraseña: str) -> Optional[Dict]:
    try:
        usuario = usuarios_collection.find_one({"email": email, "contraseña": contraseña})
        if usuario:
            usuario['_id'] = str(usuario['_id'])
        return usuario
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

def crear_usuario(nombre: str, email: str, contraseña: str, apellido: str) -> Optional[str]:
    try:
        resultado = usuarios_collection.insert_one({
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "contraseña": contraseña,
            "fecha_registro": datetime.now(),
            "activo": True
        })
        print("✅ Usuario insertado en MongoDB")
        return str(resultado.inserted_id)
    except DuplicateKeyError:
        print(f"❌ Error: El email {email} ya está registrado")
        return None

    
@app.route("/crearcuenta", methods=["POST"])
def crear_cuenta():
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    contraseña = request.form["contraseña"]

    id_usuario = crear_usuario(nombre, email, contraseña, apellido)
    if id_usuario:
        return render_template("gestor_tareas.html", usuario=email)
    else:
        return "❌ El correo ya está registrado"

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["contraseña"]

    usuario = obtener_usuario(email, password)

    if usuario:
        return render_template("gestor_tareas.html", usuario=email)
    else:
        return render_template("nicio.html", mensaje="Usuario no existe o contraseña incorrecta")
    
@app.route("/")
def inicio():
    return render_template("nicio.html")

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")


if __name__ == "__main__":
    app.run(debug=True)
