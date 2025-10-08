from flask import Flask, render_template
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # Blueprints (routes)
    from routes.galpones import bp as galpones_bp
    from routes.partos import bp as partos_bp
    from routes.destetes import bp as destetes_bp

    app.register_blueprint(galpones_bp)
    app.register_blueprint(partos_bp)
    app.register_blueprint(destetes_bp)

    @app.route('/')
    def index():
        # vista simple para comprobar
        return render_template('index.html')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
