import logging

from sqlalchemy import desc, exc

from models.chart import Chart
from models.entry import Entry
from models.song import Song

logger = logging.getLogger(__name__)


def get_latest_chart(Session, chart_type):
    session = Session()
    q = session.query(Chart) \
        .filter_by(chart_type=chart_type) \
        .order_by(desc(Chart.date_string))
    try:
        return q.first()
    except exc.ProgrammingError as err:
        logger.error(err)
        return None


def get_chart_types(Session, default=[]):
    session = Session()
    chart_types = default
    try:
        raw_chart_types = session.query(Chart.chart_type) \
            .distinct().all()
        chart_types = list(map(lambda x: x[0], raw_chart_types))
    except exc.ProgrammingError as err:
        logger.error(err)
    return chart_types


def get_entries(Session, count=10, offset=0):
    session = Session()
    raw_entries = session.query(Entry).limit(count).offset(offset).all()
    return raw_entries


def get_entry(Session, id):
    session = Session()
    return session.query(Entry).filter_by(id=id).first()


def get_songs(Session):
    session = Session()
    return session.query(Song).all()


# default to lots
def get_songs_except_id(Session, id, limit=2000000):
    session = Session()
    return session.query(Song).filter(Song.id != id).limit(limit).all()


def get_songs_except_id_pagination(session, id, limit=200000, offset=0):
    return session.query(Song).filter(
        Song.id != id).limit(limit).offset(offset).all()


def get_entries_with_song_id_pagination(session, id, limit=200000, offset=0):
    return session.query(Entry).filter_by(song_id=id).order_by(
        Entry.name, Entry.artist).limit(limit).offset(offset).all()


def get_entries_with_song_id(session, id, limit=200000):
    return session.query(Entry).filter_by(song_id=id).order_by(
        Entry.name, Entry.artist).limit(limit).all()


# Wrapper around get_entry_with_no_song_id injecting an instantiated session object
def get_all_entries_with_no_song_id(Session):
    session = Session()
    return get_entries_with_no_song_id_with_session(session).all()


def get_entries_with_no_song_id(Session, limit=1000):
    session = Session()
    return get_entries_with_no_song_id_with_session(session).limit(limit).all()


def get_entries_with_no_song_id_with_session(session):
    noSong = session.query(Entry).filter(Entry.song_id.is_(None))
    return noSong


def get_song_id_query_for(name, artist, session):
    return session.query(Song.id).join(Entry).filter(
        Entry.name == name,
        Entry.artist == artist).filter(Entry.song_id != -1).group_by(Song.id)