from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.connection import get_db_connection, get_db_dict_cursor
from datetime import datetime

bp = Blueprint('destetes', __name__, url_prefix='/destetes')

@bp.route('/', methods=['GET', 'POST'])
def listar_destetes():
    if request.method == 'POST':
        parto_id = request.form.get('parto_id')
        fecha = request.form.get('fecha') or datetime.utcnow().date()
        dh = int(request.form.get('destetados_hembras') or 0)
        dm = int(request.form.get('destetados_machos') or 0)
        muertos = int(request.form.get('muertos') or 0)
        destino_g = request.form.get('galpon_destino')
        destino_p = request.form.get('poza_destino')
        obs = request.form.get('observaciones', '')
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO destetes (parto_id, fecha, destetados_hembras, destetados_machos, muertos, galpon_destino, poza_destino, observaciones)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (parto_id, fecha, dh, dm, muertos, destino_g, destino_p, obs))
            conn.commit()
            cur.close()
            conn.close()
            flash('Destete registrado', 'success')
            return redirect(url_for('destetes.listar_destetes'))
        except Exception as e:
            flash(f'Error registro destete: {e}', 'danger')

    try:
        conn = get_db_connection()
        cur = get_db_dict_cursor(conn)
        cur.execute("SELECT d.*, p.fecha as fecha_parto FROM destetes d LEFT JOIN partos p ON d.parto_id = p.id ORDER BY d.fecha DESC LIMIT 100")
        destetes = cur.fetchall()
        cur.execute("SELECT id,nombre FROM galpones ORDER BY nombre")
        galpones = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        destetes = []
        galpones = []
        flash(f'Error leyendo destetes: {e}', 'danger')

    return render_template('destetes.html', destetes=destetes, galpones=galpones)
