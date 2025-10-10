from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Registrar blueprints
    from routes.galpon import bp as galpon_bp
    from routes.poza import bp as poza_bp
    from routes.animal import bp as animal_bp
    from routes.parto import bp as parto_bp
    
    app.register_blueprint(galpon_bp, url_prefix='/galpones')
    app.register_blueprint(poza_bp, url_prefix='/pozas')
    app.register_blueprint(animal_bp, url_prefix='/animales')
    app.register_blueprint(parto_bp, url_prefix='/partos')
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # ✅ CORREGIDO: Dashboard antes del return
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)