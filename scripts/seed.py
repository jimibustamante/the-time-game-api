from os import environ, path
from dotenv import load_dotenv
import psycopg2

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '../.env.prod'))

database_name = environ.get('DATABASE_NAME')
database_user = environ.get('DATABASE_USER')
database_password = environ.get('DATABASE_PASSWORD')
database_uri = environ.get('DATABASE_URI')
database_port = environ.get('DATABASE_PORT')

print(database_name, database_user, database_password, database_uri, database_port)

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

def run():
    try:
        conn = psycopg2.connect(database=database_name, user=database_user, password=database_password, host=database_uri, port=database_port)
        conn.autocommit = True
        cur = conn.cursor()
        print("""
            ==================
            SEEDING DATABASE
            ==================
        """)
        for key, value in THEMES.items():
            cur.execute("CREATE TABLE IF NOT EXISTS theme (id serial PRIMARY KEY, title varchar, name varchar);")
            cur.execute("""INSERT INTO theme (title, name) VALUES (%s, %s) """, (value['title'], key))

    except psycopg2.Error as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    run()

