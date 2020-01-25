import logging
import urllib.parse
from os import environ, path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_db_type_from_variable():
    type = "sqlite:///"
    if 'DB_TYPE' in environ and "mysql" in environ['DB_TYPE']:
        type = "mysql+pymysql://"
    return type


def create_url_from_parts(username, password, host, dbname):
    url = ""
    base = get_db_type_from_variable()
    if "sqlite" in base:
        db_path = path.abspath(path.join(path.dirname(__file__), 'charts.db'))
        url = base + db_path
    elif "mysql" in base:
        password = urllib.parse.quote_plus(password)
        url = "%s%s:%s@%s/%s" % (base, username, password, host, dbname)
    print("DB url: %r" % (url, ))
    return url


class Config:
    username = environ.get('DB_USERNAME')
    password = environ.get('PASS')
    host = environ.get('DB_HOST')
    db_name = environ.get('DATABASE')
    elasticsearch_host = environ.get('ELASTICSEARCH_HOST')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


#    SQLALCHEMY_DATABASE_URI=create_url_from_parts(username,
#                                                  password,
#                                                  host,
#                                                  db_name)


class TestConfig(Config):
    ENV = "development"
