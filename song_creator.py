import itertools
import logging
import time
from collections import namedtuple

from sqlalchemy import desc
from sqlalchemy.sql.expression import update

import db_retriever
import db_saver
from TooManySongsError import TooManySongsError
from update_commandline import initialize
from update_commandline import increment

logger = logging.getLogger(__name__)


def _process_songs(session, limit):
    entry_query = db_retriever.get_entries_with_no_song_id_with_session(
        session).limit(limit)
    if entry_query.count() == 0:
        logger.info("No more songs")
    else:
        for entry in entry_query:
            _entry_to_song(entry, session)
            increment()


def _entry_to_song(entry, session):
    logger.debug("Getting song id/count")
    song_query = db_retriever.get_song_id_query_for(entry.name, entry.artist,
                                                    session)
    song_count = song_query.count()
    logger.debug("Got song id from db")
    db_song = None
    if song_count > 1:
        song_query = db_retriever.get_song_id_query_for_case_sensitive(entry.name, entry.artist,
                                                        session)
        song_count = song_query.count()
        if song_count != 1:
            query_data = song_query.all()
            raise TooManySongsError("Error finding song! Query: %s\r\nSongs: %s" %
                         (song_query, query_data), query_data)
        else: 
            db_song = song_query.first()
    elif song_count == 0:
        # now we check search
        # results = elastic.search_name_artist(name=entry.name,
        #                                      artist=entry.artist)
        # result = results.result
        # if len(result) > 0:
        #     db_song = namedtuple('Song', field_names=['id'])
        #     # mark to check later
        #     db_song.id = int(-1)
        # else:
        logger.debug("Creating new song")
        db_song = db_saver.create_song(entry.name, entry.artist, session)
            # elastic.create_searchable_from_song(db_song)
            # songId = result[0].meta.id
            # db_song = namedtuple('Song', field_names=['id'])
            # db_song.id = int(songId)
    else:
        db_song = song_query.first()

    if db_song is not None:
        logger.debug("setting song id")
        entry.song_id = db_song.id
        session.commit()
        logger.debug("completed entry")
    else:
        raise RuntimeError("db_song is None")


def _genny(total, batch_size):
    num_left = total
    while num_left > 0:
        yield batch_size
        num_left = num_left - batch_size


def create_in_batch(session, total, batch_size=100):
    start_time = time.time()
    logger.error("Start time: %r" % (start_time, ))
    initialize(total)
    for size in _genny(total, batch_size):
        _process_songs(session, size)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.error("Elapsed time: %s" %
                 (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)), ))


def batch_all(session, batch_size=1000):
    num_unprocessed = db_retriever.get_entries_with_no_song_id_with_session(
        session).count()
    logger.info("%s songs to process" % (num_unprocessed))
    create_in_batch(session, num_unprocessed, batch_size)
    logger.info("Completed processing songs")
