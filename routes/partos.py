from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.connection import get_db_connection, get_db_dict_cursor
from datetime import datetime

bp = Blueprint('partos', __name__, url_prefix='/partos')

@bp.route('/', methods=['GET', 'POST'])
def listar_partos():
    if request.method == 'POST':
        galpon_id = request.form.get('galpon_id')
        poza_id = request.form.get('poza_id')
        fecha = request.form.get('fecha') or datetime.utcnow().date()
        nh = int(request.form.get('nacidos_hembras') or 0)
        nm = int(request.form.get('nacidos_machos') or 0)
        muertos = int(request.form.get('muertos') or 0)
        obs = request.form.get('observaciones', '')
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO partos (galpon_id, poza_id, fecha, nacidos_hembras, nacidos_machos, muertos, observaciones)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (galpon_id, poza_id, fecha, nh, nm, muertos, obs))
            conn.commit()
            cur.close()
            conn.close()
            flash('Parto registrado', 'success')
            return redirect(url_for('partos.listar_partos'))
        except Exception as e:
            flash(f'Error registro parto: {e}', 'danger')

    # GET: listar partos recientes y opciones de galpon/poza
    try:
        conn = get_db_connection()
        cur = get_db_dict_cursor(conn)
        cur.execute("SELECT p.*, g.nombre as galpon_nombre, z.nombre as poza_nombre FROM partos p LEFT JOIN galpones g ON p.galpon_id=g.id LEFT JOIN pozas z ON p.poza_id=z.id ORDER BY fecha DESC LIMIT 100")
        partos = cur.fetchall()
        cur.execute("SELECT id,nombre FROM galpones ORDER BY nombre")
        galpones = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        partos = []
        galpones = []
        flash(f'Error leyendo partos: {e}', 'danger')

    return render_template('partos.html', partos=partos, galpones=galpones)
