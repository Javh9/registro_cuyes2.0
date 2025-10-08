from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.connection import get_db_connection, get_db_dict_cursor

bp = Blueprint('galpones', __name__, url_prefix='/galpones')

@bp.route('/', methods=['GET', 'POST'])
def listar_galpones():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO galpones (nombre, descripcion) VALUES (%s,%s) RETURNING id", (nombre, descripcion))
            conn.commit()
            cur.close()
            conn.close()
            flash('Galpón creado', 'success')
            return redirect(url_for('galpones.listar_galpones'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')

    try:
        conn = get_db_connection()
        cur = get_db_dict_cursor(conn)
        cur.execute("SELECT * FROM galpones ORDER BY nombre")
        galpones = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        galpones = []
        flash(f'Error leyendo galpones: {e}', 'danger')

    return render_template('galpones.html', galpones=galpones)
