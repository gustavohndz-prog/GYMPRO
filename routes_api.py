from datetime import date, datetime
from decimal import Decimal
from flask import Blueprint, request, session, jsonify
from db import get_db, columns_set, first_existing
from auth import role_required

api = Blueprint("api", __name__, url_prefix="/api")


def json_error(message, status=400, detail=None):
    payload = {"ok": False, "error": message}
    if detail:
        payload["detail"] = str(detail)
    return jsonify(payload), status


def clean(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    return v


def clean_rows(rows):
    return [{k: clean(v) for k, v in r.items()} for r in rows]


def select_clients(conn, q="", estado=""):
    cols = columns_set(conn, "clientes")
    idc = first_existing(cols, "id_cliente")
    no = first_existing(cols, "no_socio", "numero_socio")
    nombre = first_existing(cols, "nombre")
    apellido = first_existing(cols, "apellido")
    genero = first_existing(cols, "genero", "sexo")
    fn = first_existing(cols, "fecha_nacimiento")
    tel = first_existing(cols, "telefono", "tel")
    email = first_existing(cols, "email", "correo")
    direccion = first_existing(cols, "direccion")
    ingreso = first_existing(cols, "fecha_ingreso", "fecha_registro")
    fin = first_existing(cols, "fecha_fin", "fecha_vencimiento", "fecha_expiracion")
    estado_col = first_existing(cols, "estado", "estatus")
    mem_id = first_existing(cols, "id_membresia")
    mem_name = first_existing(cols, "tipo_membresia", "membresia")
    aliases = []
    def sel(col, alias):
        return f"c.`{col}` AS `{alias}`" if col else f"NULL AS `{alias}`"
    aliases += [sel(idc,"id_cliente"), sel(no,"no_socio"), sel(nombre,"nombre"), sel(apellido,"apellido"), sel(genero,"genero"), sel(fn,"fecha_nacimiento"), sel(tel,"telefono"), sel(email,"email"), sel(direccion,"direccion"), sel(ingreso,"fecha_ingreso"), sel(fin,"fecha_fin"), sel(estado_col,"estado"), sel(mem_id,"id_membresia")]
    join = ""
    if mem_id and "id_membresia" in columns_set(conn, "membresias"):
        mcols = columns_set(conn, "membresias")
        mid = first_existing(mcols, "id_membresia")
        mn = first_existing(mcols, "nombre")
        join = f" LEFT JOIN membresias m ON c.`{mem_id}`=m.`{mid}`"
        aliases.append(sel("", "_dummy") if False else f"m.`{mn}` AS `membresia`" if mn else "NULL AS `membresia`")
    else:
        aliases.append(sel(mem_name,"membresia"))
    sql = "SELECT " + ",".join(aliases) + " FROM clientes c" + join
    clauses, params = [], []
    if q:
        search_cols = [c for c in [no,nombre,apellido,tel,email] if c]
        if search_cols:
            clauses.append("(" + " OR ".join([f"CAST(c.`{c}` AS CHAR) LIKE %s" for c in search_cols]) + ")")
            params.extend([f"%{q}%"] * len(search_cols))
    if estado and estado_col:
        clauses.append(f"LOWER(CAST(c.`{estado_col}` AS CHAR))=LOWER(%s)")
        params.append(estado)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    if idc: sql += f" ORDER BY c.`{idc}` DESC"
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return clean_rows(cur.fetchall())

@api.get("/health")
def health():
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT DATABASE() AS db")
            row = cur.fetchone()
        db.close()
        return jsonify({"ok": True, "database": row["db"]})
    except Exception as e:
        return json_error("No se pudo conectar a MySQL", 503, e)

@api.get("/socios")
@role_required("recepcion", "gerente", "dueno")
def socios_get():
    try:
        db=get_db(); data=select_clients(db, request.args.get("q", "").strip(), request.args.get("estado", "").strip()); db.close()
        return jsonify({"data": data})
    except Exception as e:
        return json_error("No se pudo consultar clientes", 500, e)

@api.post("/socios")
@role_required("recepcion")
def socios_post():
    payload=request.get_json(silent=True) or request.form.to_dict()
    try:
        db=get_db(); cols=columns_set(db,"clientes")
        mapping={
            "no_socio": first_existing(cols,"no_socio","numero_socio"), "nombre": first_existing(cols,"nombre"),
            "apellido": first_existing(cols,"apellido"), "fecha_nacimiento": first_existing(cols,"fecha_nacimiento"),
            "genero": first_existing(cols,"genero","sexo"), "telefono": first_existing(cols,"telefono","tel"),
            "email": first_existing(cols,"email","correo"), "direccion": first_existing(cols,"direccion"),
            "fecha_ingreso": first_existing(cols,"fecha_ingreso","fecha_registro"), "id_membresia": first_existing(cols,"id_membresia"),
            "tipo_membresia": first_existing(cols,"tipo_membresia","membresia"), "estado": first_existing(cols,"estado","estatus")
        }
        fields=[]; vals=[]
        for key,col in mapping.items():
            if col and key in payload and str(payload[key]).strip() != "":
                fields.append(f"`{col}`"); vals.append(payload[key])
        if mapping["fecha_ingreso"] and not any(f"`{mapping['fecha_ingreso']}`"==f for f in fields):
            fields.append(f"`{mapping['fecha_ingreso']}`"); vals.append(date.today())
        if mapping["estado"] and not any(f"`{mapping['estado']}`"==f for f in fields):
            fields.append(f"`{mapping['estado']}`"); vals.append("Activo")
        required=[mapping[k] for k in ("no_socio","nombre","apellido") if mapping[k]]
        present=set(fields)
        if any(f"`{x}`" not in present for x in required):
            db.close(); return json_error("Faltan campos obligatorios del cliente",400)
        with db.cursor() as cur:
            cur.execute(f"INSERT INTO clientes ({','.join(fields)}) VALUES ({','.join(['%s']*len(vals))})", vals)
            new_id=cur.lastrowid
        db.close(); return jsonify({"ok":True,"id_cliente":new_id})
    except Exception as e:
        return json_error("No se pudo registrar el cliente",500,e)

@api.put("/socios/<int:id_cliente>")
@role_required("recepcion")
def socios_put(id_cliente):
    payload=request.get_json(silent=True) or {}
    try:
        db=get_db(); cols=columns_set(db,"clientes")
        allowed={k:first_existing(cols,*names) for k,names in {
            "no_socio":["no_socio","numero_socio"],"nombre":["nombre"],"apellido":["apellido"],"fecha_nacimiento":["fecha_nacimiento"],
            "genero":["genero","sexo"],"telefono":["telefono","tel"],"email":["email","correo"],"direccion":["direccion"],
            "id_membresia":["id_membresia"],"tipo_membresia":["tipo_membresia","membresia"],"estado":["estado","estatus"],"fecha_fin":["fecha_fin","fecha_vencimiento","fecha_expiracion"]
        }.items()}
        sets=[]; vals=[]
        for k,c in allowed.items():
            if c and k in payload:
                sets.append(f"`{c}`=%s"); vals.append(payload[k])
        if not sets: db.close(); return json_error("No hay campos para actualizar")
        idcol=first_existing(cols,"id_cliente")
        with db.cursor() as cur:
            cur.execute(f"UPDATE clientes SET {','.join(sets)} WHERE `{idcol}`=%s", vals+[id_cliente])
            if cur.rowcount==0: db.close(); return json_error("Cliente no encontrado",404)
        db.close(); return jsonify({"ok":True})
    except Exception as e: return json_error("No se pudo editar el cliente",500,e)

@api.delete("/socios/<int:id_cliente>")
@role_required("recepcion")
def socios_delete(id_cliente):
    try:
        db=get_db(); cols=columns_set(db,"clientes"); idcol=first_existing(cols,"id_cliente"); estado=first_existing(cols,"estado","estatus")
        with db.cursor() as cur:
            if not estado:
                db.close(); return json_error("No se elimina físicamente un cliente: la tabla no tiene estado/estatus para una baja lógica",409)
            cur.execute(f"UPDATE clientes SET `{estado}`=%s WHERE `{idcol}`=%s",("Inactivo",id_cliente))
            if cur.rowcount==0: db.close(); return json_error("Cliente no encontrado",404)
        db.close(); return jsonify({"ok":True,"modo":"inactivo"})
    except Exception as e: return json_error("No se pudo eliminar el cliente",500,e)

@api.get("/cliente/buscar")
@role_required("recepcion","gerente","dueno")
def cliente_buscar():
    q=request.args.get("q","").strip()
    try:
        db=get_db(); rows=select_clients(db,q); db.close(); return jsonify({"data":rows[:20]})
    except Exception as e: return json_error("No se pudo consultar el cliente",500,e)

@api.get("/membresias")
@role_required("recepcion","gerente","dueno")
def membresias_get():
    try:
        db=get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM membresias ORDER BY 1")
            rows=clean_rows(cur.fetchall())
        db.close()
        return jsonify({"data":rows})
    except Exception as e:
        return json_error("No se pudo consultar membresías",500,e)


@api.post("/membresias")
@role_required("gerente")
def membresias_post():
    payload=request.get_json(silent=True) or request.form.to_dict()
    try:
        db=get_db()
        cols=columns_set(db,"membresias")
        mapping={
            "nombre": first_existing(cols,"nombre"),
            "descripcion": first_existing(cols,"descripcion"),
            "duracion": first_existing(cols,"duracion","duracion_dias","dias"),
            "precio": first_existing(cols,"precio","precio_mensual","costo"),
            "estado": first_existing(cols,"estado","estatus")
        }
        if not mapping["nombre"] or not mapping["duracion"] or not mapping["precio"]:
            db.close()
            return json_error("La tabla membresias debe tener nombre, duracion y precio",409)
        fields=[]; vals=[]
        for key,col in mapping.items():
            if col and key in payload and str(payload[key]).strip() != "":
                fields.append(f"`{col}`"); vals.append(payload[key])
        if mapping["estado"] and mapping["estado"] not in [x.strip("`") for x in fields]:
            with db.cursor() as cur:
                cur.execute("SELECT DATA_TYPE, COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='membresias' AND COLUMN_NAME=%s",('gimnasio',mapping["estado"]))
                meta=cur.fetchone() or {}
            dtype=str(meta.get("DATA_TYPE","")).lower()
            ctype=str(meta.get("COLUMN_TYPE","")).lower()
            if "enum" in dtype or "enum(" in ctype:
                default="activa"
            elif dtype in ("tinyint","smallint","mediumint","int","bigint"):
                default=1
            else:
                default="Activa"
            fields.append(f"`{mapping['estado']}`"); vals.append(default)
        required=[mapping["nombre"],mapping["duracion"],mapping["precio"]]
        present={x.strip("`") for x in fields}
        if any(x not in present for x in required):
            db.close()
            return json_error("Nombre, duración y precio son obligatorios",400)
        with db.cursor() as cur:
            cur.execute(f"INSERT INTO membresias ({','.join(fields)}) VALUES ({','.join(['%s']*len(vals))})",vals)
            new_id=cur.lastrowid
        db.close()
        return jsonify({"ok":True,"id_membresia":new_id})
    except Exception as e:
        try: db.close()
        except Exception: pass
        return json_error("No se pudo crear la membresía",500,e)

@api.get("/dashboard")
@role_required("recepcion","gerente","dueno")
def dashboard_get():
    try:
        db=get_db(); out={"socios_activos":0,"membresias_vencer":0,"ventas_mes":0,"clases_hoy":0,"actividad":[]}
        cc=columns_set(db,"clientes"); estado=first_existing(cc,"estado","estatus"); fin=first_existing(cc,"fecha_fin","fecha_vencimiento","fecha_expiracion")
        with db.cursor() as cur:
            if estado: cur.execute(f"SELECT COUNT(*) n FROM clientes WHERE LOWER(CAST(`{estado}` AS CHAR))='activo'"); out["socios_activos"]=cur.fetchone()["n"]
            if fin: cur.execute(f"SELECT COUNT(*) n FROM clientes WHERE `{fin}` BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 7 DAY)"); out["membresias_vencer"]=cur.fetchone()["n"]
            vc=columns_set(db,"ventas"); vd=first_existing(vc,"fecha_venta","fecha","fecha_registro"); vt=first_existing(vc,"total","monto","importe")
            if vd and vt: cur.execute(f"SELECT COALESCE(SUM(`{vt}`),0) total FROM ventas WHERE `{vd}`>=DATE_FORMAT(CURDATE(),'%%Y-%%m-01')"); out["ventas_mes"]=clean(cur.fetchone()["total"])
            cl=columns_set(db,"clases"); cd=first_existing(cl,"fecha","fecha_clase","dia");
            if cd: cur.execute(f"SELECT COUNT(*) n FROM clases WHERE DATE(`{cd}`)=CURDATE()"); out["clases_hoy"]=cur.fetchone()["n"]
        db.close(); return jsonify(out)
    except Exception as e: return json_error("No se pudo cargar el dashboard",500,e)

@api.get("/inventario")
@role_required("gerente")
def inventario_get():
    try:
        db=get_db();
        with db.cursor() as cur: cur.execute("SELECT * FROM productos ORDER BY 1 DESC"); rows=clean_rows(cur.fetchall())
        db.close(); return jsonify({"data":rows})
    except Exception as e:return json_error("No se pudo consultar inventario",500,e)

@api.delete("/productos/<int:id_producto>")
@role_required("gerente")
def productos_delete(id_producto):
    try:
        db=get_db(); cols=columns_set(db,"productos"); idc=first_existing(cols,"id_producto","id"); est=first_existing(cols,"estado","estatus")
        if not idc or not est:
            db.close(); return json_error("No se puede dar de baja el producto porque faltan columnas",409)
        with db.cursor() as cur:
            # Respetamos TINYINT(1) o estados de texto/ENUM.
            cur.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='productos' AND COLUMN_NAME=%s",('gimnasio',est)); meta=cur.fetchone()
            value=0 if (meta or {}).get("DATA_TYPE","").lower() in ("tinyint","smallint","mediumint","int","bigint") else "Inactivo"
            cur.execute(f"UPDATE productos SET `{est}`=%s WHERE `{idc}`=%s",(value,id_producto))
            if cur.rowcount==0: db.close(); return json_error("Producto no encontrado",404)
        db.close(); return jsonify({"ok":True})
    except Exception as e:return json_error("No se pudo dar de baja el producto",500,e)

@api.get("/proveedores")
@role_required("gerente")
def proveedores_get():
    try:
        db=get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM proveedores ORDER BY 1 DESC")
            rows=clean_rows(cur.fetchall())
        db.close()
        return jsonify({"data":rows})
    except Exception as e:
        return json_error("No se pudo consultar proveedores",500,e)


@api.post("/proveedores")
@role_required("gerente")
def proveedores_post():
    payload=request.get_json(silent=True) or request.form.to_dict()
    try:
        db=get_db()
        cols=columns_set(db,"proveedores")

        mapping={
            "nombre": first_existing(cols,"nombre","razon_social","empresa","proveedor"),
            "producto": first_existing(cols,"producto","productos","producto_abastece"),
            "contacto": first_existing(cols,"contacto","nombre_contacto","persona_contacto"),
            "telefono": first_existing(cols,"telefono","tel","telefono_contacto"),
            "email": first_existing(cols,"email","correo","correo_electronico"),
            "direccion": first_existing(cols,"direccion","domicilio"),
            "estado": first_existing(cols,"estado","estatus")
        }

        fields=[]
        vals=[]
        for key,col in mapping.items():
            if col and key in payload and str(payload[key]).strip() != "":
                fields.append(f"`{col}`")
                vals.append(payload[key])

        if mapping["estado"] and mapping["estado"] not in [f.strip("`") for f in fields]:
            # Soporta tanto estados de texto como TINYINT(1).
            with db.cursor() as cur:
                cur.execute("""
                    SELECT DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA=%s AND TABLE_NAME='proveedores' AND COLUMN_NAME=%s
                """, ('gimnasio', mapping["estado"]))
                meta=cur.fetchone() or {}
            estado_default=1 if str(meta.get("DATA_TYPE","")).lower() in ("tinyint","smallint","mediumint","int","bigint") else "Activo"
            fields.append(f"`{mapping['estado']}`")
            vals.append(estado_default)

        required=[]
        if mapping["nombre"]:
            required.append(mapping["nombre"])
        if any(f"`{x}`" not in fields for x in required):
            db.close()
            return json_error("El nombre del proveedor es obligatorio",400)

        if not fields:
            db.close()
            return json_error("No se encontraron columnas compatibles en proveedores",400)

        placeholders=','.join(['%s']*len(fields))
        sql=f"INSERT INTO proveedores ({','.join(fields)}) VALUES ({placeholders})"
        with db.cursor() as cur:
            cur.execute(sql, vals)
            new_id=cur.lastrowid
        db.close()
        return jsonify({"ok":True,"id":new_id})
    except Exception as e:
        try: db.close()
        except Exception: pass
        return json_error("No se pudo guardar el proveedor",500,e)

@api.get("/promociones")
@role_required("gerente","cliente")
def promociones_get():
    try:
        db=get_db();
        with db.cursor() as cur: cur.execute("SELECT * FROM promociones ORDER BY 1 DESC"); rows=clean_rows(cur.fetchall())
        db.close(); return jsonify({"data":rows})
    except Exception as e:return json_error("No se pudo consultar promociones",500,e)

@api.post("/promociones")
@role_required("gerente")
def promociones_post():
    payload=request.get_json(silent=True) or {}
    try:
        db=get_db(); cols=columns_set(db,"promociones"); data={}
        candidates={"nombre":["nombre"],"descripcion":["descripcion"],"tipo":["tipo","tipo_promocion"],"valor":["valor","descuento"],"inicio":["fecha_inicio","inicio"],"fin":["fecha_fin","fin"],"estado":["estado","estatus"]}
        for k,names in candidates.items():
            c=first_existing(cols,*names)
            if c and k in payload:
                value=payload[k]
                # La interfaz usa nombres amigables; MySQL usa los valores del ENUM.
                if k=="tipo":
                    value={"porcentaje":"descuento","monto":"otro","descuento":"descuento","2x1":"2x1","membresia":"membresia","otro":"otro"}.get(str(value).strip().lower(), str(value).strip().lower())
                elif k=="estado":
                    value={"activa":"activa","inactiva":"inactiva","activo":"activa","inactivo":"inactiva"}.get(str(value).strip().lower(), str(value).strip().lower())
                data[c]=value
        if not data:return json_error("No se encontraron columnas compatibles en promociones")
        with db.cursor() as cur:
            cur.execute(f"INSERT INTO promociones ({','.join('`'+k+'`' for k in data)}) VALUES ({','.join(['%s']*len(data))})",list(data.values()))
        db.close(); return jsonify({"ok":True})
    except Exception as e:return json_error("No se pudo guardar la promoción",500,e)

@api.post("/clases/cancelar")
@role_required("recepcion")
def cancelar_clase():
    payload=request.get_json(silent=True) or {}
    try:
        db=get_db(); cols=columns_set(db,"cancelaciones_clases"); data={}
        for k,names in {"id_clase":["id_clase"],"fecha":["fecha","fecha_cancelacion"],"motivo":["motivo","descripcion"],"id_usuario":["id_usuario"]}.items():
            c=first_existing(cols,*names)
            if c and (k in payload or k=="id_usuario"): data[c]=session.get("id_usuario") if k=="id_usuario" else payload.get(k)
        if not data:return json_error("No se encontraron columnas compatibles en cancelaciones_clases")
        with db.cursor() as cur: cur.execute(f"INSERT INTO cancelaciones_clases ({','.join('`'+k+'`' for k in data)}) VALUES ({','.join(['%s']*len(data))})",list(data.values()))
        db.close(); return jsonify({"ok":True})
    except Exception as e:return json_error("No se pudo registrar la cancelación",500,e)

@api.post("/reservas")
@role_required("cliente")
def reservas_post():
    payload=request.get_json(silent=True) or {}
    try:
        db=get_db(); cols=columns_set(db,"reservas_clases"); data={}
        for k,names in {"id_clase":["id_clase"],"id_cliente":["id_cliente"],"fecha_reserva":["fecha_reserva","fecha"]}.items():
            c=first_existing(cols,*names)
            if c:data[c]=session.get("id_cliente") if k=="id_cliente" else (date.today() if k=="fecha_reserva" and not payload.get(k) else payload.get(k))
        if not data:return json_error("No se encontraron columnas compatibles en reservas_clases")
        with db.cursor() as cur: cur.execute(f"INSERT INTO reservas_clases ({','.join('`'+k+'`' for k in data)}) VALUES ({','.join(['%s']*len(data))})",list(data.values()))
        db.close(); return jsonify({"ok":True})
    except Exception as e:return json_error("No se pudo registrar la reserva",500,e)

@api.get("/clases")
@role_required("recepcion","cliente")
def clases_get():
    try:
        db=get_db();
        with db.cursor() as cur: cur.execute("SELECT * FROM clases ORDER BY 1 DESC"); rows=clean_rows(cur.fetchall())
        db.close(); return jsonify({"data":rows})
    except Exception as e:return json_error("No se pudieron consultar las clases",500,e)

@api.get("/usuarios")
@role_required("dueno")
def usuarios_get():
    try:
        db=get_db();
        with db.cursor() as cur: cur.execute("SELECT * FROM usuarios ORDER BY 1 DESC"); rows=clean_rows(cur.fetchall())
        db.close(); return jsonify({"data":rows})
    except Exception as e:return json_error("No se pudieron consultar usuarios",500,e)

@api.get("/reportes/<tipo>")
@role_required("gerente","dueno")
def reporte(tipo):
    """Genera datos reales para la pantalla de reportes y sus gráficas."""
    tipo=tipo.lower().strip()
    if tipo not in ("ventas","inventario","membresias"):
        return json_error("Reporte no válido",404)
    try:
        db=get_db()
        desde=request.args.get("desde","").strip()
        hasta=request.args.get("hasta","").strip()
        result={"data":[],"graficas":{}}
        with db.cursor() as cur:
            if tipo=="ventas":
                vc=columns_set(db,"ventas"); dc=columns_set(db,"detalles_venta"); pc=columns_set(db,"productos")
                vdate=first_existing(vc,"fecha_venta","fecha","fecha_registro")
                vtotal=first_existing(vc,"total","monto","importe")
                did=first_existing(dc,"id_detalle_venta","id_detalle")
                dvid=first_existing(dc,"id_venta")
                dpid=first_existing(dc,"id_producto")
                dqty=first_existing(dc,"cantidad")
                dsub=first_existing(dc,"subtotal","importe")
                pid=first_existing(pc,"id_producto","id")
                pname=first_existing(pc,"nombre","producto")
                if not vdate or not dvid or not dpid or not dqty or not pid or not pname:
                    db.close(); return json_error("No están disponibles las columnas necesarias para generar el reporte de ventas",409)
                clauses=[]; params=[]
                if desde:
                    clauses.append(f"v.`{vdate}` >= %s"); params.append(desde)
                if hasta:
                    clauses.append(f"v.`{vdate}` < DATE_ADD(%s, INTERVAL 1 DAY)"); params.append(hasta)
                where=(" WHERE "+" AND ".join(clauses)) if clauses else ""
                select_total=f"COALESCE(SUM(v.`{vtotal}`),0)" if vtotal else "0"
                cur.execute(f"SELECT {select_total} AS total FROM ventas v{where}",params)
                result["total_ventas"]=clean(cur.fetchone()["total"])
                subtotal_expr=f"SUM(d.`{dsub}`)" if dsub else f"SUM(d.`{dqty}` * p.`{first_existing(pc,'precio_venta','precio') or '0'}`)"
                cur.execute(f"SELECT p.`{pname}` AS producto, SUM(d.`{dqty}`) AS unidades, {subtotal_expr} AS importe FROM detalles_venta d JOIN ventas v ON d.`{dvid}`=v.`{first_existing(vc,'id_venta','id') or 'id_venta'}` JOIN productos p ON d.`{dpid}`=p.`{pid}`{where} GROUP BY p.`{pname}` ORDER BY unidades DESC",params)
                top=clean_rows(cur.fetchall())
                result["graficas"]["productos_mas_vendidos"]=top
                result["data"]=top
                if vdate:
                    cur.execute(f"SELECT DATE(v.`{vdate}`) AS periodo, COALESCE(SUM(v.`{vtotal}`),0) AS total FROM ventas v{where} GROUP BY DATE(v.`{vdate}`) ORDER BY periodo",params)
                    result["graficas"]["ventas_por_dia"]=clean_rows(cur.fetchall())
            elif tipo=="inventario":
                pc=columns_set(db,"productos"); pid=first_existing(pc,"id_producto","id"); pname=first_existing(pc,"nombre","producto"); stock=first_existing(pc,"stock_actual","existencia","stock"); minimum=first_existing(pc,"stock_minimo","minimo"); price=first_existing(pc,"precio_venta","precio"); state=first_existing(pc,"estado","estatus")
                if not pid or not pname or not stock:
                    db.close(); return json_error("No están disponibles las columnas necesarias para inventario",409)
                cur.execute("SELECT * FROM productos ORDER BY 1 DESC")
                rows=clean_rows(cur.fetchall())
                result["data"]=rows
                low=[]
                if minimum:
                    cur.execute(f"SELECT `{pname}` AS producto, `{stock}` AS stock, `{minimum}` AS minimo FROM productos WHERE `{stock}` <= `{minimum}` ORDER BY `{stock}`")
                    low=clean_rows(cur.fetchall())
                result["graficas"]["stock_bajo"]=low
                result["graficas"]["stock_por_producto"]= [{"producto":r.get(pname),"stock":r.get(stock)} for r in rows]
            else:
                cc=columns_set(db,"clientes"); mc=columns_set(db,"membresias")
                cid=first_existing(cc,"id_cliente","id"); cmid=first_existing(cc,"id_membresia"); ctype=first_existing(cc,"tipo_membresia","membresia"); cestado=first_existing(cc,"estado","estatus")
                mid=first_existing(mc,"id_membresia","id"); mname=first_existing(mc,"nombre")
                if cmid and mid and mname:
                    sql=f"SELECT m.`{mname}` AS membresia, COUNT(*) AS cantidad FROM clientes c LEFT JOIN membresias m ON c.`{cmid}`=m.`{mid}` GROUP BY m.`{mname}` ORDER BY cantidad DESC"
                elif ctype:
                    sql=f"SELECT c.`{ctype}` AS membresia, COUNT(*) AS cantidad FROM clientes c GROUP BY c.`{ctype}` ORDER BY cantidad DESC"
                else:
                    sql="SELECT 'Sin membresía' AS membresia, COUNT(*) AS cantidad FROM clientes"
                cur.execute(sql)
                result["graficas"]["membresias_por_tipo"]=clean_rows(cur.fetchall())
                if cestado:
                    cur.execute(f"SELECT `{cestado}` AS estado, COUNT(*) AS cantidad FROM clientes GROUP BY `{cestado}` ORDER BY cantidad DESC")
                    result["graficas"]["socios_por_estado"]=clean_rows(cur.fetchall())
                cur.execute("SELECT * FROM clientes ORDER BY 1 DESC")
                result["data"]=clean_rows(cur.fetchall())
        db.close()
        return jsonify(result)
    except Exception as e:
        try: db.close()
        except Exception: pass
        return json_error("No se pudo generar el reporte",500,e)


def current_client_id(conn):
    if session.get("id_cliente"):
        return session["id_cliente"]
    cols=columns_set(conn,"clientes"); idc=first_existing(cols,"id_cliente")
    if not idc:return None
    candidates=[]; no=first_existing(cols,"no_socio","numero_socio"); email=first_existing(cols,"email","correo");
    if no:candidates.append((no,session.get("usuario")))
    if email:candidates.append((email,session.get("usuario")))
    with conn.cursor() as cur:
        for col,val in candidates:
            if not val:continue
            cur.execute(f"SELECT `{idc}` id FROM clientes WHERE `{col}`=%s LIMIT 1",(val,)); row=cur.fetchone()
            if row:return row["id"]
    return None

@api.get("/cliente/me")
@role_required("cliente")
def cliente_me():
    try:
        db=get_db(); cid=current_client_id(db)
        if not cid: db.close(); return json_error("El usuario cliente no está relacionado con un registro en clientes",404)
        rows=select_clients(db); data=next((x for x in rows if x.get("id_cliente")==cid),None); db.close()
        if not data:return json_error("Cliente no encontrado",404)
        session["id_cliente"]=cid; return jsonify({"data":data})
    except Exception as e:return json_error("No se pudo cargar el perfil del cliente",500,e)

@api.put("/cliente/perfil")
@role_required("cliente")
def cliente_perfil_put():
    payload=request.get_json(silent=True) or {}
    try:
        db=get_db(); cid=current_client_id(db); cols=columns_set(db,"clientes"); idc=first_existing(cols,"id_cliente")
        if not cid:return json_error("No se pudo identificar al cliente",404)
        sets=[];vals=[]
        for k,names in {"nombre":["nombre"],"apellido":["apellido"],"fecha_nacimiento":["fecha_nacimiento"],"telefono":["telefono","tel"],"email":["email","correo"],"direccion":["direccion"]}.items():
            c=first_existing(cols,*names)
            if c and k in payload:sets.append(f"`{c}`=%s");vals.append(payload[k])
        if not sets:return json_error("No hay campos compatibles para actualizar")
        with db.cursor() as cur:cur.execute(f"UPDATE clientes SET {','.join(sets)} WHERE `{idc}`=%s",vals+[cid])
        db.close();return jsonify({"ok":True})
    except Exception as e:return json_error("No se pudo actualizar el perfil",500,e)

@api.get("/cliente/pagos")
@role_required("cliente")
def cliente_pagos_get():
    try:
        db=get_db(); cid=current_client_id(db)
        if not cid:return json_error("No se pudo identificar al cliente",404)
        cols=columns_set(db,"pagos_membresias"); idcli=first_existing(cols,"id_cliente")
        if not idcli:return json_error("La tabla pagos_membresias no contiene id_cliente",500)
        with db.cursor() as cur:cur.execute(f"SELECT * FROM pagos_membresias WHERE `{idcli}`=%s ORDER BY 1 DESC",(cid,));rows=clean_rows(cur.fetchall())
        db.close();return jsonify({"data":rows})
    except Exception as e:return json_error("No se pudieron consultar pagos",500,e)

@api.get("/cliente/asistencias")
@role_required("cliente")
def cliente_asistencias_get():
    try:
        db=get_db(); cid=current_client_id(db)
        if not cid:return json_error("No se pudo identificar al cliente",404)
        cols=columns_set(db,"asistencia_clases"); idcli=first_existing(cols,"id_cliente");
        if not idcli:return json_error("La tabla asistencia_clases no contiene id_cliente",500)
        with db.cursor() as cur:cur.execute(f"SELECT * FROM asistencia_clases WHERE `{idcli}`=%s ORDER BY 1 DESC",(cid,));rows=clean_rows(cur.fetchall())
        db.close();return jsonify({"data":rows})
    except Exception as e:return json_error("No se pudieron consultar asistencias",500,e)

@api.get("/cliente/clases")
@role_required("cliente")
def cliente_clases_get():
    return clases_get()

@api.post("/ventas")
@role_required("recepcion")
def ventas_post():
    payload = request.get_json(silent=True) or {}
    detalles = payload.get("detalles") or []
    if not detalles:
        return json_error("La venta no contiene productos")

    db = None
    try:
        db = get_db()
        db.begin()
        vc = columns_set(db, "ventas")
        dc = columns_set(db, "detalles_venta")
        pc = columns_set(db, "productos")

        vid_col = first_existing(vc, "id_venta")
        if not vid_col:
            raise RuntimeError("La tabla ventas no contiene id_venta")

        prod_id_col = first_existing(pc, "id_producto", "id")
        prod_name_col = first_existing(pc, "producto", "nombre", "nombre_producto")
        prod_price_col = first_existing(pc, "precio_venta", "precio", "precio_unitario")
        prod_stock_col = first_existing(pc, "stock_actual", "stock", "existencia")
        if not prod_id_col or not prod_price_col or not prod_stock_col:
            raise RuntimeError("La tabla productos no tiene id, precio y stock compatibles")

        # Si el usuario escribe el número de socio, resolverlo a id_cliente.
        cliente = payload.get("cliente")
        id_cliente = None
        if cliente not in (None, ""):
            cc = columns_set(db, "clientes")
            cid = first_existing(cc, "id_cliente")
            cno = first_existing(cc, "no_socio", "numero_socio")
            if not cid:
                raise RuntimeError("La tabla clientes no contiene id_cliente")
            with db.cursor() as cur:
                if str(cliente).isdigit():
                    # Primero se intenta como id_cliente; si no existe, como no_socio.
                    cur.execute(f"SELECT `{cid}` AS id_cliente FROM clientes WHERE `{cid}`=%s LIMIT 1", (int(cliente),))
                    row = cur.fetchone()
                    if not row and cno:
                        cur.execute(f"SELECT `{cid}` AS id_cliente FROM clientes WHERE `{cno}`=%s LIMIT 1", (str(cliente),))
                        row = cur.fetchone()
                elif cno:
                    cur.execute(f"SELECT `{cid}` AS id_cliente FROM clientes WHERE `{cno}`=%s LIMIT 1", (str(cliente),))
                    row = cur.fetchone()
                else:
                    row = None
            if not row:
                raise ValueError("El cliente/socio indicado no existe")
            id_cliente = row["id_cliente"]

        # Recalcular precios y validar stock directamente desde MySQL.
        lineas = []
        total = Decimal("0.00")
        with db.cursor() as cur:
            for item in detalles:
                try:
                    pid = int(item.get("id"))
                    cantidad = int(item.get("cantidad", 0))
                except (TypeError, ValueError):
                    raise ValueError("Hay un producto o cantidad inválida en la venta")
                if cantidad <= 0:
                    raise ValueError("La cantidad de cada producto debe ser mayor que cero")

                cur.execute(
                    f"SELECT `{prod_id_col}` AS id_producto, "
                    + (f"`{prod_name_col}` AS nombre, " if prod_name_col else "'' AS nombre, ")
                    + f"`{prod_price_col}` AS precio, `{prod_stock_col}` AS stock "
                    + f"FROM productos WHERE `{prod_id_col}`=%s FOR UPDATE",
                    (pid,)
                )
                prod = cur.fetchone()
                if not prod:
                    raise ValueError(f"El producto #{pid} no existe")
                stock = int(prod["stock"] or 0)
                if cantidad > stock:
                    raise ValueError(f"No hay suficiente stock de {prod['nombre']}. Disponible: {stock}")
                precio = Decimal(str(prod["precio"] or 0))
                subtotal = precio * cantidad
                total += subtotal
                lineas.append((pid, cantidad, precio, subtotal, stock))

            # Registrar cabecera de venta.
            user_id = session.get("id_usuario")
            fecha_col = first_existing(vc, "fecha_venta", "fecha", "fecha_registro")
            total_col = first_existing(vc, "total", "monto", "importe")
            metodo_col = first_existing(vc, "metodo_pago", "metodo", "forma_pago")
            user_col = first_existing(vc, "id_usuario")
            client_col = first_existing(vc, "id_cliente")
            estado_col = first_existing(vc, "estado")

            fields, vals = [], []
            if user_col and user_id is not None:
                fields.append(f"`{user_col}`"); vals.append(user_id)
            if client_col and id_cliente is not None:
                fields.append(f"`{client_col}`"); vals.append(id_cliente)
            if fecha_col:
                fields.append(f"`{fecha_col}`"); vals.append(datetime.now())
            if total_col:
                fields.append(f"`{total_col}`"); vals.append(total)
            if metodo_col:
                metodo = str(payload.get("metodo_pago") or "efectivo").strip().lower()
                if metodo not in {"efectivo", "tarjeta", "transferencia"}:
                    raise ValueError("Método de pago no válido")
                fields.append(f"`{metodo_col}`"); vals.append(metodo)
            if estado_col:
                fields.append(f"`{estado_col}`"); vals.append("completada")

            if not fields:
                raise RuntimeError("No se encontraron columnas compatibles en ventas")
            cur.execute(
                f"INSERT INTO ventas ({','.join(fields)}) VALUES ({','.join(['%s'] * len(vals))})",
                vals
            )
            venta_id = cur.lastrowid

            # Registrar detalle y descontar inventario.
            did = first_existing(dc, "id_detalle_venta")
            dventa = first_existing(dc, "id_venta")
            dprod = first_existing(dc, "id_producto", "producto_id")
            dqty = first_existing(dc, "cantidad", "cantidad_vendida")
            dprice = first_existing(dc, "precio_unitario", "precio")
            ddesc = first_existing(dc, "descuento")
            dsub = first_existing(dc, "subtotal", "importe")

            if not dventa or not dprod or not dqty or not dprice or not dsub:
                raise RuntimeError("La tabla detalles_venta no tiene las columnas necesarias")

            for pid, cantidad, precio, subtotal, stock in lineas:
                df, dv = [], []
                for col, val in [(dventa, venta_id), (dprod, pid), (dqty, cantidad), (dprice, precio)]:
                    df.append(f"`{col}`"); dv.append(val)
                if ddesc:
                    df.append(f"`{ddesc}`"); dv.append(Decimal("0.00"))
                df.append(f"`{dsub}`"); dv.append(subtotal)
                cur.execute(
                    f"INSERT INTO detalles_venta ({','.join(df)}) VALUES ({','.join(['%s'] * len(dv))})",
                    dv
                )
                cur.execute(
                    f"UPDATE productos SET `{prod_stock_col}`=`{prod_stock_col}`-%s WHERE `{prod_id_col}`=%s",
                    (cantidad, pid)
                )

        db.commit()
        return jsonify({"ok": True, "id_venta": venta_id, "total": float(total)})
    except Exception as e:
        if db:
            try: db.rollback()
            except Exception: pass
        return json_error("No se pudo registrar la venta", 500, e)
    finally:
        if db:
            try: db.close()
            except Exception: pass

@api.get("/categorias-productos")
@role_required("gerente")
def categorias_productos_get():
    try:
        db=get_db(); cols=columns_set(db,"categorias_productos")
        idc=first_existing(cols,"id_categoria","id_categoria_producto")
        name=first_existing(cols,"nombre","categoria","nombre_categoria")
        if not idc or not name:
            db.close(); return json_error("No se encontraron las columnas de categorías de productos",500)
        with db.cursor() as cur:
            cur.execute(f"SELECT `{idc}` AS id_categoria, `{name}` AS nombre FROM categorias_productos ORDER BY `{name}`")
            rows=clean_rows(cur.fetchall())
        db.close(); return jsonify({"data":rows})
    except Exception as e: return json_error("No se pudieron consultar categorías",500,e)

@api.get("/productos")
@role_required("recepcion","gerente")
def productos_get():
    try:
        db=get_db(); cols=columns_set(db,"productos")
        q=request.args.get("q","").strip(); estado=request.args.get("estado","").strip(); stock=request.args.get("stock","").strip()
        idc=first_existing(cols,"id_producto","id")
        prod=first_existing(cols,"producto","nombre","nombre_producto")
        catid=first_existing(cols,"id_categoria","id_categoria_producto")
        desc=first_existing(cols,"descripcion")
        precio=first_existing(cols,"precio_venta","precio","precio_unitario")
        stockc=first_existing(cols,"stock_actual","stock","existencia")
        minc=first_existing(cols,"stock_minimo","minimo_stock","stock_min")
        est=first_existing(cols,"estado","estatus")
        if not idc or not prod:
            db.close(); return json_error("La tabla productos no tiene las columnas mínimas esperadas",500)
        selects=[f"p.`{idc}` AS id_producto",f"p.`{prod}` AS producto"]
        selects += [f"p.`{precio}` AS precio_venta" if precio else "NULL AS precio_venta", f"p.`{stockc}` AS stock_actual" if stockc else "0 AS stock_actual", f"p.`{minc}` AS stock_minimo" if minc else "0 AS stock_minimo", f"p.`{est}` AS estado" if est else "1 AS estado", f"p.`{desc}` AS descripcion" if desc else "NULL AS descripcion"]
        join=""
        if catid:
            cc=columns_set(db,"categorias_productos"); cid=first_existing(cc,"id_categoria","id_categoria_producto"); cn=first_existing(cc,"nombre","categoria","nombre_categoria")
            if cid and cn:
                join=f" LEFT JOIN categorias_productos c ON p.`{catid}`=c.`{cid}`"; selects.append(f"c.`{cn}` AS categoria"); selects.append(f"p.`{catid}` AS id_categoria")
        sql="SELECT "+", ".join(selects)+" FROM productos p"+join
        clauses=[];params=[]
        if q:
            clauses.append(f"(CAST(p.`{prod}` AS CHAR) LIKE %s OR "+(f"CAST(p.`{desc}` AS CHAR) LIKE %s" if desc else "0=1")+")")
            params += [f"%{q}%"] + ([f"%{q}%"] if desc else [])
        if estado and est:
            clauses.append(f"LOWER(CAST(p.`{est}` AS CHAR))=LOWER(%s)"); params.append(estado)
        if stock=="bajo" and stockc and minc:
            clauses.append(f"p.`{stockc}` <= p.`{minc}`")
        if clauses: sql += " WHERE " + " AND ".join(clauses)
        sql += f" ORDER BY p.`{idc}` DESC"
        with db.cursor() as cur:
            cur.execute(sql,params); rows=clean_rows(cur.fetchall())
        for row in rows:
            if isinstance(row.get("estado"), (int,float)):
                row["estado"] = "Activo" if row["estado"] else "Inactivo"
        db.close(); return jsonify({"data":rows})
    except Exception as e:return json_error("No se pudieron consultar productos",500,e)

@api.post("/productos")
@role_required("gerente")
def productos_post():
    payload=request.get_json(silent=True) or request.form.to_dict()
    try:
        db=get_db(); cols=columns_set(db,"productos")
        mapping={
            "producto":first_existing(cols,"producto","nombre","nombre_producto"),
            "id_categoria":first_existing(cols,"id_categoria","id_categoria_producto"),
            "descripcion":first_existing(cols,"descripcion"),
            "precio_venta":first_existing(cols,"precio_venta","precio","precio_unitario"),
            "stock_actual":first_existing(cols,"stock_actual","stock","existencia"),
            "stock_minimo":first_existing(cols,"stock_minimo","minimo_stock","stock_min"),
            "estado":first_existing(cols,"estado","estatus")
        }
        fields=[];vals=[]
        for key,col in mapping.items():
            if col and key in payload and str(payload[key]).strip()!='': fields.append(f"`{col}`"); vals.append(payload[key])
        if mapping["estado"] and mapping["estado"] not in [x.strip('`') for x in fields]:
            fields.append(f"`{mapping['estado']}`")
            estado_val = payload.get("estado", "Activo")
            # El DER usa TINYINT(1) para estado; si la BD usa texto/ENUM conservamos Activo/Inactivo.
            with db.cursor() as cur:
                cur.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='productos' AND COLUMN_NAME=%s", (db.get_host_info().split(' ')[0] if False else 'gimnasio', mapping['estado']))
                meta=cur.fetchone()
            tipo=(meta or {}).get("DATA_TYPE","").lower()
            if tipo in ("tinyint","smallint","mediumint","int","bigint"):
                estado_val = 1 if str(estado_val).lower() in ("1","true","activo","activa") else 0
            vals.append(estado_val)
        else:
            # Si el formulario envía estado, normalizarlo cuando la columna sea numérica.
            if mapping["estado"] and mapping["estado"] in [x.strip('`') for x in fields]:
                idx=[x.strip('`') for x in fields].index(mapping["estado"])
                with db.cursor() as cur:
                    cur.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='productos' AND COLUMN_NAME=%s", ('gimnasio', mapping['estado']))
                    meta=cur.fetchone()
                if (meta or {}).get("DATA_TYPE","").lower() in ("tinyint","smallint","mediumint","int","bigint"):
                    vals[idx]=1 if str(vals[idx]).lower() in ("1","true","activo","activa") else 0
        if not mapping["producto"] or mapping["producto"] not in [x.strip('`') for x in fields]: db.close(); return json_error("El producto es obligatorio",400)
        with db.cursor() as cur:
            cur.execute(f"INSERT INTO productos ({','.join(fields)}) VALUES ({','.join(['%s']*len(vals))})",vals); new_id=cur.lastrowid
        db.close(); return jsonify({"ok":True,"id_producto":new_id})
    except Exception as e:return json_error("No se pudo registrar el producto",500,e)

@api.put("/productos/<int:id_producto>")
@role_required("gerente")
def productos_put(id_producto):
    payload=request.get_json(silent=True) or {}
    try:
        db=get_db(); cols=columns_set(db,"productos"); idc=first_existing(cols,"id_producto","id")
        mapping={"producto":first_existing(cols,"producto","nombre","nombre_producto"),"id_categoria":first_existing(cols,"id_categoria","id_categoria_producto"),"descripcion":first_existing(cols,"descripcion"),"precio_venta":first_existing(cols,"precio_venta","precio","precio_unitario"),"stock_actual":first_existing(cols,"stock_actual","stock","existencia"),"stock_minimo":first_existing(cols,"stock_minimo","minimo_stock","stock_min"),"estado":first_existing(cols,"estado","estatus")}
        sets=[];vals=[]
        for k,c in mapping.items():
            if c and k in payload: sets.append(f"`{c}`=%s"); vals.append(payload[k])
        if not sets: db.close(); return json_error("No hay campos para actualizar")
        with db.cursor() as cur:
            cur.execute(f"UPDATE productos SET {','.join(sets)} WHERE `{idc}`=%s",vals+[id_producto])
            if cur.rowcount==0: db.close(); return json_error("Producto no encontrado",404)
        db.close(); return jsonify({"ok":True})
    except Exception as e:return json_error("No se pudo editar el producto",500,e)

