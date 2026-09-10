from flask import Flask, request, redirect, url_for, session, flash
from pathlib import Path
from auth import login_from_db, role_required
from page_renderer import render_screen
from routes_api import api

app = Flask(__name__)
app.secret_key = "CAMBIAR_CLAVE_SECRETA"
app.register_blueprint(api)

PAGES = {
    "dashboard":"dashboard.html", "socios":"socios.html", "cliente":"cliente.html", "membresias":"membresias.html",
    "clases":"clases.html", "inventario":"inventario.html", "proveedores":"proveedores.html", "pos":"pos.html",
    "usuarios":"usuarios.html", "promos":"promos.html", "reportes":"reportes.html", "auditoria":"auditoria.html",
    "configuracion":"configuracion.html", "acceso":"acceso.html", "registro":"registro.html",
    "cliente_inicio":"cliente_inicio.html", "cliente_membresia":"cliente_membresia.html", "cliente_clases":"cliente_clases.html",
    "cliente_pagos":"cliente_pagos.html", "cliente_asistencias":"cliente_asistencias.html", "cliente_promociones":"cliente_promociones.html", "cliente_perfil":"cliente_perfil.html"
}

@app.route("/")
def index(): return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        usuario=request.form.get("usuario","").strip(); password=request.form.get("password",""); rol=request.form.get("rol","").lower()
        try:
            user=login_from_db(usuario,password,rol)
            if user:
                session.clear(); session.update(user)
                return redirect(url_for("cliente_inicio") if user["rol"]=="cliente" else url_for("dashboard"))
            flash("Usuario, contraseña o rol incorrectos.")
        except Exception as e:
            flash("No se pudo conectar con la base de datos gimnasio. Verifica XAMPP/MySQL y las credenciales de DB_CONFIG.")
    return render_screen("login.html","/login")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login"))

def make_page(name, roles):
    def view(): return render_screen(PAGES[name], request.path)
    view.__name__ = name
    return role_required(*roles)(view)

# Cada pantalla conserva su HTML/JS; gym.py administra rutas, sesión y menú.
for _name,_roles in {
    "dashboard":("recepcion","gerente","dueno"), "socios":("recepcion","gerente","dueno"), "cliente":("recepcion","gerente","dueno"),
    "membresias":("gerente","dueno"), "clases":("recepcion",), "inventario":("gerente",), "proveedores":("gerente",),
    "pos":("recepcion",), "usuarios":("dueno",), "promos":("gerente",), "reportes":("gerente","dueno"),
    "auditoria":("dueno",), "configuracion":("dueno",), "acceso":("recepcion","gerente","dueno"), "registro":("recepcion",),
    "cliente_inicio":("cliente",), "cliente_membresia":("cliente",), "cliente_clases":("cliente",), "cliente_pagos":("cliente",),
    "cliente_asistencias":("cliente",), "cliente_promociones":("cliente",), "cliente_perfil":("cliente",)
}.items():
    globals()[_name] = make_page(_name,_roles)
    app.add_url_rule("/" + _name.replace("cliente_", "cliente/") if _name.startswith("cliente_") else "/"+_name, _name, globals()[_name])

if __name__ == "__main__":
    app.run(debug=True)
