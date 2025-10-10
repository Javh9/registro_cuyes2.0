from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Registrar blueprints
    from routes.galpon import bp as galpon_bp
    from routes.poza import bp as poza_bp
    from routes.animal import bp as animal_bp    # ✅ NUEVO
    from routes.parto import bp as parto_bp      # ✅ NUEVO
    
    app.register_blueprint(galpon_bp, url_prefix='/galpones')
    app.register_blueprint(poza_bp, url_prefix='/pozas')
    app.register_blueprint(animal_bp, url_prefix='/animales')  # ✅ NUEVO
    app.register_blueprint(parto_bp, url_prefix='/partos')     # ✅ NUEVO
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)