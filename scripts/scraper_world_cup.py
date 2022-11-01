from os import environ, path
from dotenv import load_dotenv
import psycopg2
import requests
import lxml.html as html

basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '../.env.prod'))
load_dotenv(path.join(basedir, '../.env'))

database_name = environ.get('DATABASE_NAME')
database_user = environ.get('DATABASE_USER')
database_password = environ.get('DATABASE_PASSWORD')
database_uri = environ.get('DATABASE_URI')
database_port = environ.get('DATABASE_PORT')

print(database_name, database_user, database_password, database_uri, database_port)

CHAMPIONS_URL = 'https://es.wikipedia.org/wiki/Anexo:Finales_de_la_Copa_Mundial_de_F%C3%BAtbol'
XPATH_MAIN_TABLE = '/html/body/div[3]/div[3]/div[5]/div[1]/table/tbody'
XPATH_YEAR = './th/a/text()'
XPATH_INFO_LINK = './th/a/@href'


def run():
    try:
        conn = psycopg2.connect(database=database_name, user=database_user, password=database_password, host=database_uri, port=database_port)
        cur = conn.cursor()
        cur.execute("SELECT * FROM theme WHERE name LIKE %s", ('copa_libertadores',))
        theme = cur.fetchone()
        theme_id = theme[0]
        response = requests.get(CHAMPIONS_URL)
        print(response)
        if response.status_code == 200:
            page = response.content.decode('utf-8')
            parsed = html.fromstring(page)
            rows = parsed.xpath(XPATH_MAIN_TABLE + '/tr[not(@class)]')
            print(f"Rows: {rows}")
            for i in range(rows):
                if i == 0:
                    continue
                row = rows[i]
                year = row.xpath(XPATH_YEAR)
                print(f"YEAR: {year}")

        else:
            raise ValueError(f"Error: {response.status_code}")

    except ValueError as value_error:
        print(value_error)

    cur.close()
    conn.close()


if __name__ == '__main__':
    run()

