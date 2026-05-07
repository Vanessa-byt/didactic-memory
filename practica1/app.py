from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from typing import Optional, Dict, List
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from datetime import datetime, timedelta

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["usuariosDB"]                
usuarios_collection = db["usuarios"]     
tareas_collection = db["tareas"]

# ---------------- FUNCIONES DE USUARIO ----------------

def obtener_usuario(email: str, contraseña: str) -> Optional[Dict]:
    usuario = usuarios_collection.find_one({"email": email, "contraseña": contraseña})
    if usuario:
        usuario['_id'] = str(usuario['_id'])
    return usuario

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
        return str(resultado.inserted_id)
    except DuplicateKeyError:
        return None

# ---------------- FUNCIONES DE TAREAS ----------------

def crear_tarea(usuario_id: str, titulo: str, descripcion: str = "", 
                fecha_limite: Optional[datetime] = None) -> Optional[str]:
    """Crear una nueva tarea para un usuario"""
    tarea = {
        "usuario_id": ObjectId(usuario_id),
        "titulo": titulo,
        "descripcion": descripcion,
        "estado": "pendiente",
        "fecha_creacion": datetime.now(),
        "fecha_limite": fecha_limite or datetime.now() + timedelta(days=7),
        "completada": False,
        "etiquetas": []
    }
    resultado = tareas_collection.insert_one(tarea)
    return str(resultado.inserted_id)

def buscar_tareas(texto: str) -> List[Dict]:
    """Buscar tareas por texto en título o descripción"""
    tareas = tareas_collection.find({
        "$text": {"$search": texto}
    }).sort([("score", {"$meta": "textScore"})])
    resultado = []
    for t in tareas:
        t['_id'] = str(t['_id'])
        t['usuario_id'] = str(t['usuario_id'])
        resultado.append(t)
    return resultado

def eliminar_tarea(tarea_id: str) -> bool:
    """Eliminar una tarea"""
    resultado = tareas_collection.delete_one({"_id": ObjectId(tarea_id)})
    return resultado.deleted_count > 0

def actualizar_estado_tarea(tarea_id: str, nuevo_estado: str) -> bool:
    """Actualizar el estado de una tarea"""
    estados_validos = ["pendiente", "en_progreso", "completada", "cancelada"]
    if nuevo_estado not in estados_validos:
        return False
    resultado = tareas_collection.update_one(
        {"_id": ObjectId(tarea_id)},
        {
            "$set": {
                "estado": nuevo_estado,
                "completada": nuevo_estado == "completada",
                "fecha_actualizacion": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0

# ---------------- RUTAS ----------------

@app.route("/crearcuenta", methods=["POST"])
def crear_cuenta():
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    contraseña = request.form["contraseña"]

    id_usuario = crear_usuario(nombre, email, contraseña, apellido)
    if id_usuario:
        return redirect(url_for("gestor_tareas", usuario_id=id_usuario))
    else:
        return "❌ El correo ya está registrado"

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["contraseña"]

    usuario = obtener_usuario(email, password)
    if usuario:
        return redirect(url_for("gestor_tareas", usuario_id=usuario["_id"]))
    else:
        return render_template("nicio.html", mensaje="Usuario no existe o contraseña incorrecta")

@app.route("/")
def inicio():
    return render_template("nicio.html")

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

@app.route("/gestor/<usuario_id>")
def gestor_tareas(usuario_id):
    tareas = list(tareas_collection.find({"usuario_id": ObjectId(usuario_id)}))
    for t in tareas:
        t["_id"] = str(t["_id"])
        if "fecha_creacion" in t:
            t["fecha_creacion"] = t["fecha_creacion"].strftime("%d/%m/%Y %H:%M")
        if "fecha_limite" in t:
            t["fecha_limite"] = t["fecha_limite"].strftime("%d/%m/%Y")
    return render_template("gestor_tareas.html", tareas=tareas, usuario_id=usuario_id)

@app.route("/crear_tarea/<usuario_id>", methods=["POST"])
def crear_tarea_route(usuario_id):
    titulo = request.form["titulo"]
    descripcion = request.form.get("descripcion", "")
    fecha_limite = request.form.get("fecha_limite")
    fecha_limite = datetime.strptime(fecha_limite, "%Y-%m-%d") if fecha_limite else None
    crear_tarea(usuario_id, titulo, descripcion, fecha_limite)
    return redirect(url_for("gestor_tareas", usuario_id=usuario_id))

@app.route("/buscar_tareas/<usuario_id>", methods=["GET"])
def buscar_tareas_route(usuario_id):
    texto = request.args.get("texto", "")
    tareas = buscar_tareas(texto)
    for t in tareas:
        t["_id"] = str(t["_id"])
    return render_template("gestor_tareas.html", tareas=tareas, usuario_id=usuario_id)

@app.route("/eliminar_tarea/<usuario_id>/<tarea_id>", methods=["POST"])
def eliminar_tarea_route(usuario_id, tarea_id):
    eliminar_tarea(tarea_id)
    return redirect(url_for("gestor_tareas", usuario_id=usuario_id))

@app.route("/actualizar_tarea/<usuario_id>/<tarea_id>", methods=["POST"])
def actualizar_tarea_route(usuario_id, tarea_id):
    nuevo_estado = request.form["estado"]
    actualizar_estado_tarea(tarea_id, nuevo_estado)
    return redirect(url_for("gestor_tareas", usuario_id=usuario_id))

if __name__ == "__main__":
    app.run(debug=True)
