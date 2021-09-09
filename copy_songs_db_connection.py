from database import Session
import logging

SQLITE = 'sqlite'
FIVE_MINS = 5 * 60
MYSQL = 'mysql'
logger = logging.getLogger(__name__)


class DB_connection:
    def __init__(self, from_session, to_session) -> None:
        self.from_session = from_session
        self.to_session = to_session


def open_connections(first, second) -> None:
    db_connections = open_db_connections()
    from_session = _session_by_type(first, db_connections)
    to_session = _session_by_type(second, db_connections)
    return DB_connection(from_session, to_session)


def open_db_connections(sqliteFile='temp.sqlite'):
    logger.info('getting sqlite with url %s' % (sqliteFile))
    sqlite_session = Session.get_session(url='sqlite:///%s' % (sqliteFile))
    logger.info('getting mysql with defaults')
    mysql_session = Session.get_session(timeout=FIVE_MINS)

    return {MYSQL: mysql_session, SQLITE: sqlite_session}


# first is the copy from, second is copy to. Determine which is which and assign to the appropriate variables
#then pull from copy from to copy to


def _session_by_type(session_requested, connections):
    if 'sqlite' in session_requested:
        return connections[SQLITE]
    elif 'mysql' in session_requested:
        return connections[MYSQL]
    raise RuntimeError('Invalid db type')


def get_db_connection():

    pass
