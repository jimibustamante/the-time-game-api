import firebase_admin
from firebase_admin import credentials, firestore
from os import environ, path
from dotenv import load_dotenv
import psycopg2

basedir = path.abspath(path.dirname(__file__))
cred = credentials.Certificate(path.join(basedir, '../servicesAccountKey.json'))
firebase_admin.initialize_app(cred)

db = firestore.client()

load_dotenv(path.join(basedir, '../.env.prod'))

database_name = environ.get('DATABASE_NAME')
database_user = environ.get('DATABASE_USER')
database_password = environ.get('DATABASE_PASSWORD')
database_uri = environ.get('DATABASE_URI')
database_port = environ.get('DATABASE_PORT')

def run():
    try:
        conn = psycopg2.connect(database=database_name, user=database_user, password=database_password, host=database_uri, port=database_port)
        cur = conn.cursor()
        cur.execute("SELECT * FROM theme WHERE name LIKE %s", ('world_cup',))
        theme = cur.fetchone()
        theme_id = theme[0]
        print(theme_id)

        facts = db.collection(u'facts')
        print(facts)
        for doc in facts.stream():
            # print(f'{doc.id} => {doc.to_dict()}')
            fact = doc.to_dict()
            name = fact.get('name')
            year = fact.get('year')
            info_link = fact.get('infoLink')
            description = fact.get('description')

            print(f'theme: {theme_id}\nyear: {year}\ninfo_link: {info_link}\nname: {name}\ndescription: {description}')
            cur.execute("""INSERT INTO fact (theme_id, year, info_link, name, description) VALUES (%s, %s, %s, %s, %s)""", (theme_id, year, info_link, name, description))
            conn.commit()
    except ImportError as error:
        print(error)
        print('Something went wrong...')


if __name__ == '__main__':
    run()

