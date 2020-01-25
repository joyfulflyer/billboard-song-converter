import database_connection
from config import Config as config


def get_session(url=None):
    if url is None:
        url = database_connection.create_url_from_parts(
            username=config.username,
            password=config.password,
            host=config.host,
            dbname=config.db_name)
    Session = database_connection.connect(url)
    return Session