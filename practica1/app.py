from flask import Flask, render_template, request

app = Flask(__name__)

usuarios = {
    "prueba@gmail.com": "oso1234",
    "vaessita_1234@gmail.com": "vanessita1234"
}

@app.route("/")
def inicio():
    return render_template("nicio.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    if email in usuarios and usuarios[email] == password:

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
