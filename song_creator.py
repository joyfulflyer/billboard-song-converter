import itertools
import logging
import time
from collections import namedtuple

from sqlalchemy import desc

import db_retriever
import db_saver
import elastic

logger = logging.getLogger(__name__)


def _process_songs(session, limit):
    entry_query = db_retriever.get_entries_with_no_song_id_with_session(
        session).limit(limit)
    if entry_query.count() == 0:
        logger.info("No more songs")
    else:
        for entry in entry_query:
            _entry_to_song(entry, session)


def _entry_to_song(entry, session):
    song_query = db_retriever.get_song_id_query_for(entry.name, entry.artist,
                                                    session)
    song_count = song_query.count()
    db_song = None
    if song_count > 1:
        raise ValueError("Too many songs! Query: %s\r\nSongs: %s" %
                         (song_query, song_query.all()))
    elif song_count == 0:
        # now we check search
        results = elastic.search_name_artist(name=entry.name,
                                             artist=entry.artist)
        result = results.result
        if len(result) > 0:
            db_song = namedtuple('Song', field_names=['id'])
            # mark to check later
            db_song.id = int(-1)
        else:
            db_song = db_saver.create_song(entry.name, entry.artist, session)
            elastic.create_searchable_from_song(db_song)
            # songId = result[0].meta.id
            # db_song = namedtuple('Song', field_names=['id'])
            # db_song.id = int(songId)
    else:
        db_song = song_query.first()

    if db_song is not None:
        entry.song_id = db_song.id
        session.commit()


def _genny(total, batch_size):
    num_left = total
    while num_left > 0:
        yield batch_size
        num_left = num_left - batch_size


def create_in_batch(session, total, batch_size=100):
    start_time = time.time()
    logger.error("Start time: %r" % (start_time, ))
    for size in _genny(total, batch_size):
        _process_songs(session, size)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.error("Elapsed time: %s" %
                 (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)), ))


def batch_all(session, batch_size=1000):
    num_unprocessed = db_retriever.get_entries_with_no_song_id_with_session(
        session).count()
    create_in_batch(session, num_unprocessed, batch_size)
    logger.info("Completed processing songs")
