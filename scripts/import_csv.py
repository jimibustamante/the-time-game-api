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


def run():
    try:
        conn = psycopg2.connect(database=database_name, user=database_user, password=database_password, host=database_uri, port=database_port)
        cur = conn.cursor()
        cur.execute("SELECT * FROM theme WHERE name LIKE %s", ('copa_libertadores',))
        theme = cur.fetchone()
        theme_id = theme[0]
        with open('./file.csv', 'r', encoding='utf-8') as file:
            attributes_names = {}
            for index, line in enumerate(file):
                items = line.split(';')
                items = [i.replace('\n', '').replace('\ufeff', '') for i in items]
                if index == 0:
                    attributes_names = items
                    doc_name_index = items.index('year')
                    print(f'doc_name_index: {doc_name_index}')
                else:
                    data = dict(zip(attributes_names, items))
                    print(theme_id, data['year'], data['info_link'], data['name'], data['description'])
                    cur.execute("""INSERT INTO fact (theme_id, year, info_link, name, description) VALUES (%s, %s, %s, %s, %s) """, (theme_id, data['year'], data['info_link'], data['name'], data['description']))
                    conn.commit()
        cur.close()
        conn.close()    
        
    except ImportError as error:
        print(error)
        print('Something went wrong...')
    

if __name__ == '__main__':
    run()
