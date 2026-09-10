from functools import wraps
from flask import redirect, url_for, session
from db import get_db, columns_set, first_existing


def normalize_role(value):
    value = str(value or '').strip().lower()
    return {
        'recepción': 'recepcion', 'recepcion': 'recepcion',
        'gerencia': 'gerente', 'gerente': 'gerente',
        'dueño': 'dueno', 'dueno': 'dueno', 'dueña': 'dueno',
        'cliente': 'cliente'
    }.get(value, value)


def role_required(*roles):
    allowed = {normalize_role(r) for r in roles}
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not session.get('usuario'):
                return redirect(url_for('login'))
            if normalize_role(session.get('rol')) not in allowed:
                return 'Acceso denegado', 403
            return view(*args, **kwargs)
        return wrapper
    return decorator


def _password_ok(stored, supplied):
    stored = str(stored or '')
    supplied = str(supplied or '')
    if stored == supplied:
        return True
    try:
        from werkzeug.security import check_password_hash
        return check_password_hash(stored, supplied)
    except Exception:
        return False


def login_from_db(usuario, password, requested_role=None):
    db = get_db()
    try:
        cols = columns_set(db, 'usuarios')
        user_col = first_existing(cols, 'usuario', 'username', 'user')
        pass_col = first_existing(cols, 'password', 'contrasena', 'clave')
        id_col = first_existing(cols, 'id_usuario')
        name_col = first_existing(cols, 'nombre', 'nombre_completo')
        active_col = first_existing(cols, 'activo', 'estado', 'estatus')
        client_col = first_existing(cols, 'id_cliente')
        role_col = first_existing(cols, 'rol', 'role')
        role_id_col = first_existing(cols, 'id_rol')
        if not user_col or not pass_col:
            raise RuntimeError('La tabla usuarios no contiene las columnas de usuario y contraseña esperadas.')

        role_select = 'NULL AS __rol'
        join = ''
        if role_col:
            role_select = f'u.`{role_col}` AS __rol'
        elif role_id_col:
            rc = columns_set(db, 'roles')
            rid = first_existing(rc, 'id_rol')
            rn = first_existing(rc, 'nombre', 'rol', 'nombre_rol')
            if rid and rn:
                join = f' LEFT JOIN roles r ON u.`{role_id_col}`=r.`{rid}`'
                role_select = f'r.`{rn}` AS __rol'

        fields = [
            f'u.`{id_col}` AS id_usuario' if id_col else 'NULL AS id_usuario',
            f'u.`{user_col}` AS usuario',
            f'u.`{pass_col}` AS __password',
            f'u.`{name_col}` AS nombre' if name_col else f'u.`{user_col}` AS nombre',
            role_select,
            f'u.`{client_col}` AS id_cliente' if client_col else 'NULL AS id_cliente',
            f'u.`{active_col}` AS __activo' if active_col else '1 AS __activo'
        ]
        sql = f"SELECT {','.join(fields)} FROM usuarios u{join} WHERE u.`{user_col}`=%s LIMIT 1"
        with db.cursor() as cur:
            cur.execute(sql, (usuario,))
            row = cur.fetchone()
        if not row:
            return None
        active = str(row.get('__activo', 1)).strip().lower()
        if active in {'0', 'false', 'inactivo', 'no'}:
            return None
        if not _password_ok(row.get('__password'), password):
            return None
        rol = normalize_role(row.get('__rol'))
        if rol not in {'recepcion', 'gerente', 'dueno', 'cliente'}:
            return None
        if requested_role and normalize_role(requested_role) != rol:
            return None
        return {
            'id_usuario': row.get('id_usuario'),
            'usuario': row.get('usuario', usuario),
            'nombre': row.get('nombre', usuario),
            'rol': rol,
            'id_cliente': row.get('id_cliente')
        }
    finally:
        db.close()
