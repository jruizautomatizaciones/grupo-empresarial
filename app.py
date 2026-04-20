import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "grupo_empresarial_2026_jruiz"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def cargar_json(ruta):
    with open(os.path.join(BASE_DIR, ruta), encoding="utf-8") as f:
        return json.load(f)

def get_usuarios():
    return cargar_json("data/usuarios/usuarios.json")

def get_empresas():
    return cargar_json("data/empresas/empresas.json")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def empresa_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        empresa_id = kwargs.get("empresa_id", "")
        usuario = session.get("usuario", {})
        if empresa_id not in usuario.get("empresas", []):
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET","POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("home"))
    error = ""
    if request.method == "POST":
        user = request.form.get("usuario","").strip().lower()
        pwd  = request.form.get("password","").strip()
        usuarios = get_usuarios()
        if user in usuarios and usuarios[user]["password"] == pwd:
            session["usuario"] = usuarios[user]
            session["usuario"]["id"] = user
            return redirect(url_for("home"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    usuario  = session["usuario"]
    empresas = get_empresas()
    mis_empresas = {k: v for k,v in empresas.items() if k in usuario["empresas"]}
    return render_template("home.html", usuario=usuario, empresas=mis_empresas)

@app.route("/empresa/<empresa_id>")
@login_required
@empresa_required
def empresa(empresa_id):
    usuario  = session["usuario"]
    empresas = get_empresas()
    emp      = empresas.get(empresa_id)
    if not emp:
        return redirect(url_for("home"))
    return render_template("empresa.html", usuario=usuario, empresa=emp, empresa_id=empresa_id)

@app.route("/empresa/<empresa_id>/facturas")
@login_required
@empresa_required
def facturas(empresa_id):
    empresas = get_empresas()
    emp = empresas.get(empresa_id, {})
    return render_template("modulo.html", titulo="Facturas Proveedores", icono="📄",
        empresa=emp, empresa_id=empresa_id,
        estado="En construccion — modulo activo para EXALBOM", usuario=session["usuario"])

@app.route("/empresa/<empresa_id>/horario")
@login_required
@empresa_required
def horario(empresa_id):
    empresas = get_empresas()
    emp = empresas.get(empresa_id, {})
    return render_template("modulo.html", titulo="Control Horario", icono="⏰",
        empresa=emp, empresa_id=empresa_id,
        estado="Integracion con sistema IBES activo" if empresa_id=="ibes" else "Proximamente",
        usuario=session["usuario"])

@app.route("/empresa/<empresa_id>/dashboard")
@login_required
@empresa_required
def dashboard(empresa_id):
    empresas = get_empresas()
    emp = empresas.get(empresa_id, {})
    return render_template("modulo.html", titulo="Dashboard", icono="📊",
        empresa=emp, empresa_id=empresa_id,
        estado="Proximamente", usuario=session["usuario"])

@app.route("/admin/usuarios")
@login_required
def admin_usuarios():
    if session["usuario"].get("rol") != "admin":
        return redirect(url_for("home"))
    usuarios = get_usuarios()
    empresas = get_empresas()
    return render_template("admin_usuarios.html",
        usuario=session["usuario"], usuarios=usuarios, empresas=empresas)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
