import copy_songs_db_connection
import db_retriever
import entry_generators
import db_saver
from models.entry import Entry
from models.song import Song
from models.base import Base
from models.chart import Chart
import logging

logger = logging.getLogger(__name__)


def connect(first, second):
    connections = copy_songs_db_connection.open_connections(first, second)
    create_tables(connections.to_session)
    convert_charts(connections)
    convert_entries(connections)
    convert_songs(connections)

def convert_entries(connections):
    logger.info('saving entries')
    to_session = connections.to_session()
    for entry in entry_generators.get_entries(connections.from_session):
        for e in entry:
            converted = copy_entry(e)
            db_saver.add_to_session(session=to_session, item=converted)
        db_saver.commit(to_session)
    logger.info('completed saving entries')

def convert_songs(connections):
    logger.info('saving songs')
    to_session = connections.to_session()
    for song in db_retriever.get_songs(connections.from_session):
        converted = Song()
        converted.id = song.id
        converted.name = song.name
        converted.artist = song.artist
        converted.spotify_id = song.spotify_id
        converted.search_term = song.search_term
        converted.search_results = song.search_results
        db_saver.add_to_session(session=to_session, item=converted)
    db_saver.commit(to_session)
    logger.info('Completed saving songs')


def convert_charts(connections):
    logger.info('saving charts')
    to_session = connections.to_session()
    for chart in db_retriever.get_charts(connections.from_session):
        converted = copy_chart(chart)
        db_saver.add_to_session(session=to_session, item=converted)
    db_saver.commit(to_session)
    logger.info('completed saving charts')
    pass

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


def copy_chart(chart):
    converted = Chart()
    converted.id = chart.id
    converted.chart_type = chart.chart_type
    converted.date_string = chart.date_string
    if chart.next_chart_date is not None:
        converted.next_chart_date = chart.next_chart_date
    return converted


def create_tables(Session):
    session = Session()
    Base.metadata.create_all(session.get_bind().engine)
    session.close()
