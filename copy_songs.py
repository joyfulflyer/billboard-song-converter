import Session

SQLITE = 'sqlite'
FIVE_MINS = 5 * 60
MYSQL = 'mysql'


class DB_Connections:

    def __init__(self) -> None:
        pass

    def open_db_connections(self, sqliteFile='temp.sqlite'):
        sqlite_session = Session.get_session(url='sqlite:///%s' % (sqliteFile))
        mysql_session = Session.get_session(timeout=FIVE_MINS)

        return {MYSQL: mysql_session, SQLITE: sqlite_session}

    # first is the copy from, second is copy to. Determine which is which and assign to the appropriate variables
    #then pull from copy from to copy to

    def selectacopy(self, first, second):  # this is a bad name and should be changed
        db_connections = self.open_db_connections()
        self.from_session = self._session_by_type(first, db_connections)
        self.to_session = self._session_by_type(second, db_connections)
        pass

    def _session_by_type(self, session_requested, connections):
        if 'sqlite' in session_requested:
            return connections[SQLITE]
        elif 'mysql' in session_requested:
            return connections[MYSQL]
        raise RuntimeError('Invalid db type')
