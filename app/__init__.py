from flask import Flask
from .extensions import db, cors, migrate
from .routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    with app.app_context():
        try:
            # db.drop_all()
            # db.create_all()
            app.register_blueprint(api)
        except Exception as e:
            print(f'ERROR: {e}')


        return app

