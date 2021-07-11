from flask import Flask
from .extensions import db, cors
from .routes import api
from .models import Theme

THEMES = {
  'copa_libertadores': {
    'database': 'LibertadoresFinals',
    'title': 'Finales de Copa Libertadores',
  },
  'champions_legue': {
    'database': 'ChampionsFinals',
    'title': 'Finales de Champions Legue',
  },
  'world_cup': {
    'database': 'facts',
    'title': 'Finales Copa del Mundo',
  },
}

def create_themes():
    for key, value in THEMES.items():
        theme = Theme(title=value['title'], name=str(key))
        db.session.add(theme)
        db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    cors.init_app(app)

    with app.app_context():
        try:
            # db.drop_all()
            db.create_all()
            # create_themes()
            app.register_blueprint(api)
        except Exception as e:
            print(f'ERROR: {e}')


        return app

