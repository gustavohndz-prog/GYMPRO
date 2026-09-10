import re
from pathlib import Path
from flask import Response, session, get_flashed_messages

BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / 'templates'

ADMIN_MENU = [
    ('/dashboard', '▣', 'Dashboard', {'recepcion','gerente','dueno'}),
    ('/registro', '＋', 'Registro', {'recepcion'}),
    ('/socios', '♙', 'Socios', {'recepcion','gerente','dueno'}),
    ('/cliente', '⌕', 'Consulta cliente', {'recepcion','gerente','dueno'}),
    ('/membresias', '◆', 'Membresías', {'gerente','dueno'}),
    ('/clases', '▤', 'Clases', {'recepcion'}),
    ('/pos', '$', 'Punto de venta', {'recepcion'}),
    ('/inventario', '▦', 'Inventario', {'gerente'}),
    ('/proveedores', '⌂', 'Proveedores', {'gerente'}),
    ('/promos', '%', 'Promociones', {'gerente'}),
    ('/reportes', '◫', 'Reportes', {'gerente','dueno'}),
    ('/usuarios', '♟', 'Usuarios', {'dueno'}),
    ('/auditoria', '◉', 'Auditoría', {'dueno'}),
    ('/configuracion', '⚙', 'Configuración', {'dueno'}),
    ('/acceso', '✓', 'Acceso', {'recepcion','gerente','dueno'}),
]

CLIENT_MENU = [
    ('/cliente/inicio', '⌂', 'Inicio'),
    ('/cliente/membresia', '◆', 'Membresía'),
    ('/cliente/clases', '▤', 'Clases'),
    ('/cliente/pagos', '$', 'Pagos'),
    ('/cliente/asistencias', '✓', 'Asistencias'),
    ('/cliente/promociones', '%', 'Promociones'),
    ('/cliente/perfil', '♙', 'Perfil'),
]


def _sidebar(path, role):
    items = CLIENT_MENU if role == 'cliente' else [x for x in ADMIN_MENU if role in x[3]]
    rows = []
    for href, icon, label, *_ in items:
        active = ' active' if path == href else ''
        rows.append(f'<a class="menu-item{active}" href="{href}"><i>{icon}</i><span>{label}</span></a>')
    return f'''<aside class="sidebar">
      <div class="brand"><div><strong>GYMPRO</strong><small>Sistema Integral</small></div></div>
      <nav class="menu">{''.join(rows)}</nav>
      <div class="sidebar-footer"><span>{role.title()}</span><a class="menu-item" href="/logout" style="padding:0">Salir</a></div>
    </aside>'''


def _absolute_static(raw):
    raw = re.sub(r'''(?:\.\./)+static/css/g\.css''', '/static/css/g.css', raw, flags=re.I)
    raw = re.sub(r'''(?:\.\./)+static/js/([^"']+)''', r'/static/js/\1', raw, flags=re.I)
    return raw


def render_screen(filename, path):
    raw = _absolute_static((TEMPLATES / filename).read_text(encoding='utf-8'))
    # Carga forzada del CSS original para evitar caché del navegador.
    raw = re.sub(r"<link[^>]+href=[\"']/static/css/g\\.css(?:\?[^\"']*)?[\"'][^>]*>", '<link rel="stylesheet" href="/static/css/g.css?v=20260908">', raw, count=1, flags=re.I)
    if '/static/css/g.css?v=20260908' not in raw:
        raw = raw.replace('</head>', '<link rel="stylesheet" href="/static/css/g.css?v=20260908">\n</head>', 1)

    if filename == 'login.html':
        flashes = get_flashed_messages()
        if flashes:
            msg = ' '.join(str(x) for x in flashes)
            raw = raw.replace('<p id="loginMessage"></p>', f'<p id="loginMessage">{msg}</p>')
        match_login = re.search(r'<body[^>]*>(.*?)</body>', raw, re.I | re.S)
        if match_login:
            body_login = match_login.group(1)
            body_login = re.sub(r'<main\s+class=["\']content["\']>', '<main class="main content">', body_login, count=1, flags=re.I)
            raw = raw[:match_login.start(1)] + body_login + raw[match_login.end(1):]
        return Response(raw, mimetype='text/html')
    role = session.get('rol', '')
    match = re.search(r'<body[^>]*>(.*?)</body>', raw, re.I | re.S)
    if not match:
        return Response(raw, mimetype='text/html')
    body = match.group(1)
    body = re.sub(r'<nav[^>]*>.*?</nav>', '', body, flags=re.I | re.S)
    body = re.sub(r'<main\s+class=["\']content["\']>', '<main class="main"><div class="content">', body, count=1, flags=re.I)
    body = re.sub(r'</main>', '</div></main>', body, count=1, flags=re.I)
    wrapped = f'<div class="app">{_sidebar(path, role)}{body}</div>'
    html = raw[:match.start(1)] + wrapped + raw[match.end(1):]
    return Response(html, mimetype='text/html')
