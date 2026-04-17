from flask import Flask, render_template, url_for 

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/crear_cuenta')
def formulario():
    return render_template('formulario.html')

@app.route('/gestor_tareas')
def gestor():
    return render_template('gestor_tareas.html')


if __name__ == '__main__':
    app.run(debug=True)