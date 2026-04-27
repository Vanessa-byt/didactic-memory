from flask import Flask, render_template, request
from pymongo import MongoClient
from typing import Optional, Dict

app = Flask(__name__)

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["usuariosDB"]                
usuarios_collection = db["usuarios"]     

def obtener_usuario(email: str, password: str) -> Optional[Dict]:
    """Obtener usuario por email y contraseña"""
    try:
        usuario = usuarios_collection.find_one({"email": email, "password": password})
        if usuario:
            usuario['_id'] = str(usuario['_id'])  # convertir ObjectId a string
        return usuario
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

def crear_usuario(self, nombre: str, email: str, contraseña: str, apellido: str) -> Optional[str]:
        """Crear un nuevo usuario"""
        try:
            resultado = self.usuarios.insert_one({
                "nombre": nombre,
                "apellido": apellidos,
                "email": email,
                "contraseña": password,
                "fecha_registro": datetime.now(),
                "activo": True
            })
            return str(resultado.inserted_id)
        except DuplicateKeyError:
            print(f"❌ Error: El email {email} ya está registrado")
            return None

@app.route("/")
def inicio():
    return render_template("nicio.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    usuario = obtener_usuario(email, password)

    if usuario:
        return render_template("gestor_tareas.html", usuario=email)
    else:
        return render_template("nicio.html", mensaje="Usuario no existe o contraseña incorrecta")

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

@app.route("/gestor_tareas")
def gestor():
    return render_template("gestor_tareas.html")

if __name__ == "__main__":
    app.run(debug=True)
