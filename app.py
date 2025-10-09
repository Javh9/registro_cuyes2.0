from flask import Flask, render_template
import os
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Registrar blueprints
    from routes.galpones import bp as galpones_bp
    from routes.pozass import bp as pozas_bp
    from routes.animales import bp as animales_bp
    from routes.partos import bp as partos_bp
    from routes.destetes import bp as destetes_bp
    from routes.clasificacion import bp as clasificacion_bp
    from routes.movimientos import bp as movimientos_bp
    from routes.ventas import bp as ventas_bp
    from routes.gastos import bp as gastos_bp
    from routes.notificaciones import bp as notificaciones_bp
    from routes.balances import bp as balances_bp
    
    app.register_blueprint(galpones_bp, url_prefix='/galpones')
    app.register_blueprint(pozas_bp, url_prefix='/pozas')
    app.register_blueprint(animales_bp, url_prefix='/animales')
    app.register_blueprint(partos_bp, url_prefix='/partos')
    app.register_blueprint(destetes_bp, url_prefix='/destetes')
    app.register_blueprint(clasificacion_bp, url_prefix='/clasificacion')
    app.register_blueprint(movimientos_bp, url_prefix='/movimientos')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(gastos_bp, url_prefix='/gastos')
    app.register_blueprint(notificaciones_bp, url_prefix='/notificaciones')
    app.register_blueprint(balances_bp, url_prefix='/balances')
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)