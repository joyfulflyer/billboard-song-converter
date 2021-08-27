import logging
import database_connection
from config import Config as config

_session_makers = {}
logger = logging.getLogger(__name__)

def get_session(url=None, timeout=0):
    if url is None:
        url = database_connection.create_url_from_parts(
            username=config.username,
            password=config.password,
            host=config.host,
            dbname=config.db_name)
    if url not in _session_makers:
        Session = database_connection.connect(url)
        if timeout and not database_connection.wait_for_db_connection(
                Session, timeout):
            raise Exception('Unavailalble')
        _session_makers[url] = Session
    return _session_makers[url]


# proxy for more descriptive name
def get_session_maker(url=None):
    return get_session(url)