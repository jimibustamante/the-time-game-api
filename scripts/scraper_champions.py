from os import environ, path
from dotenv import load_dotenv
import psycopg2
import requests
import lxml.html as html

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '../.env.prod'))

database_name = environ.get('DATABASE_NAME')
database_user = environ.get('DATABASE_USER')
database_password = environ.get('DATABASE_PASSWORD')
database_uri = environ.get('DATABASE_URI')
database_port = environ.get('DATABASE_PORT')

print(database_name, database_user, database_password, database_uri, database_port)

CHAMPIONS_URL = 'https://en.wikipedia.org/wiki/List_of_European_Cup_and_UEFA_Champions_League_finals'
XPATH_MAIN_TABLE = '/html/body/div[3]/div[3]/div[5]/div[1]/table[3]/tbody'
XPATH_YEAR = './th/a/text()'
XPATH_INFO_LINK = './th/a/@href'


def run():
    try:
        conn = psycopg2.connect(database=database_name, user=database_user, password=database_password, host=database_uri, port=database_port)
        cur = conn.cursor()
        cur.execute("SELECT * FROM theme WHERE name LIKE %s", ('champions_legue',))
        theme = cur.fetchone()
        theme_id = theme[0]

        response = requests.get(CHAMPIONS_URL)
        if response.status_code == 200:
            page = response.content.decode('utf-8')
            parsed = html.fromstring(page)
            rows = parsed.xpath(XPATH_MAIN_TABLE + '/tr[not(@class)]')
            for row in rows:
                if len(row.xpath(XPATH_YEAR)) == 0:
                    continue
                year = row.xpath(XPATH_YEAR)[0]
                info_link = row.xpath(XPATH_INFO_LINK)[0]
                winner = row.xpath('./td/a/text()')[0]
                loser = row.xpath('./td/a/text()')[2]
                description = winner
                year = int(str(year).split('–')[0])
                info_link = info_link
                name = f'{winner} - {loser}'
                print(f'year: {year}\ninfo_link: {info_link}\nname: {name}\ndescription: {description}')
                cur.execute("""INSERT INTO fact (theme_id, year, info_link, name, description) VALUES (%s, %s, %s, %s, %s)""", (theme_id, year, info_link, name, description))
                conn.commit()

        else:
            raise ValueError(f'Error: {response.status_code}')

    except ValueError as value_error:
        print(value_error)

    cur.close()
    conn.close()


if __name__ == '__main__':
    run()

