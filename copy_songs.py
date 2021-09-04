import copy_songs_db_connection
import db_retriever
import entry_generators
import db_saver
from models.entry import Entry
from models.base import Base


def connect(first, second):
    connections =  copy_songs_db_connection.open_connections(first, second)
    to_session = connections.to_session()
    create_tables(connections.to_session)
    for entry in entry_generators.get_entries(connections.from_session, limit=100):
        converted = copy_entry(entry)
        db_saver.add_to_session(session=to_session, item=converted)
        db_saver.commit(to_session)


def copy_entry(entry):
    e = Entry()
    e.id = entry.id
    e.name = entry.name
    e.artist = entry.artist
    e.place = entry.place
    e.peak_position = entry.peak_position
    e.last_position = entry.last_position
    e.weeks_on_chart = entry.weeks_on_chart
    e.chart_id = entry.chart_id
    e.song_id = entry.song_id
    return e

def create_tables(Session):
    session = Session()
    Base.metadata.create_all(session.get_bind().engine)
    session.close()
