import copy_songs_db_connection
import db_retriever


def connect(first, second):
    connections =  copy_songs_db_connection.open_connections(first, second)
    from_entries = db_retriever.get_entries(connections.from_session)
    print(from_entries)

