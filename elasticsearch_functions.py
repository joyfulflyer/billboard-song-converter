#! usr/bin/python3

import logging
import time

# from elasticsearch_dsl import Q, Search
# from elasticsearch_dsl.query import Bool, Match

import db_retriever
import db_saver
import song_creator
import concurrent.futures
from elasticsearch_client.client import global_connect
from Session import get_session
import similar_songs
from collections import namedtuple
from elastic import create_searchable_from_song, init_searchable_song, search_name_artist
import elastic
import asyncio

MIN_SAFE_SCORE = 25
STEP = 2000

logger = logging.getLogger(__name__)


def do_entries(Session):
    for i in range(10):
        entries = db_retriever.get_entries(Session, count=100, offset=100 * i)
        for e in entries:
            search = search_name_artist(e.name, e.artist)
            if search.count > 0:
                pass


# continue_songs and search_song are mostly proof of concept
# They have been merged in to song_creator
def continue_songs(Session):
    session = Session()
    entries = db_retriever.get_entries_with_no_song_id_with_session(session)
    for entry in entries:
        # Min score determined experimentially but mostly arbitrarily
        song = search_song(entry, session)
        if song is not None:
            entry.song_id = song.id
            session.commit()


def search_song(entry, session):
    s = search_name_artist(entry.name, entry.artist)
    result = s.result
    count = s.count
    if count == 0:
        db_song = db_saver.create_song(entry.name, entry.artist, session)
        create_searchable_from_song(db_song)
        return db_song
    if result.hits.max_score < MIN_SAFE_SCORE:
        logger.error(f'Manual check for {entry}. Results: {result.hits}')
        return None
    if count > 1:
        # Just take the first for now, but we need to be careful.
        logger.warning(
            f'Too many results for entry {entry}. Results: {result.hits}')
    songId = result.hits[0].meta.id
    song = namedtuple('Song', field_names=['id'])
    song.id = int(songId)
    return song


def add_existing_songs(Session):
    init_searchable_song()
    startTime = time.time()
    db_songs = db_retriever.get_songs_except_id(Session, -1)
    afterDbTime = time.time()
    stamp = afterDbTime
    diff = afterDbTime - startTime
    logging.info(
        f'Took {time.strftime("%M:%S", time.gmtime(diff))} to get from db')
    for i, song in enumerate(db_songs):
        if i != 0 and i % 5000 == 0:
            now = time.time()
            diff = now - stamp
            logging.error(
                f'Took {time.strftime("%H:%M:%S", time.gmtime(diff))} for 5000 sons'
            )
            stamp = now
        create_searchable_from_song(song)
    finalTime = time.time()
    diff = finalTime - afterDbTime
    logging.error(
        f'Took {time.strftime("%M:%S", time.gmtime(diff))} to save songs')


async def add_existing_songs_async(Session):
    loop = asyncio.get_running_loop()
    loop.set_default_executor(concurrent.futures.ThreadPoolExecutor())
    init_searchable_song()
    startTime = time.time()

    for db_songs in _gen(Session):
        afterDbTime = time.time()
        diff = afterDbTime - startTime
        futures = [
            elastic.create_searchable_from_song_async(song)
            for song in db_songs
        ]
        await asyncio.gather(*futures)
        partialTime = time.time()
        diff = partialTime - afterDbTime
        logging.error(
            f'Took {time.strftime("%H:%M:%S", time.gmtime(diff))} for {STEP} songs'
        )
        await asyncio.sleep(0.5)  # To try to prevent timeouts

    finalTime = time.time()
    diff = finalTime - startTime
    logging.error(
        f'Took {time.strftime("%H:%M:%S", time.gmtime(diff))} to save songs')


def _gen(Session):
    offset = 0
    while True:
        db_songs = db_retriever.get_songs_except_id_pagination(Session,
                                                               -1,
                                                               limit=STEP,
                                                               offset=offset)
        if len(db_songs) > 0:
            yield db_songs
        else:
            return
        offset = offset + STEP


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='ElasticSearch functions')
    parser.add_argument(
        '-b',
        '--bootstrap',
        action="store_true",
        help="Elasticsearch - Add existing songs to elasticsearch (bootstrap)")
    parser.add_argument('-c',
                        '--continue_songs',
                        action="store_true",
                        help="Continue adding songs")
    parser.add_argument(
        '--batch',
        type=int,
        help="Batch create songs with total to create, 0 for all",
        default=-1)
    parser.add_argument(
        '-m',
        '--merge',
        action='store_true',
        help='Check if entries with a potential match should be combined')
    parsed = parser.parse_args()
    return parsed


def handle_args(args, Session):
    if args.bootstrap:
        add_existing_songs(Session)
    if args.continue_songs:
        song_creator.batch_all(Session)
    if args.batch > -1:
        if args.batch == 0:
            song_creator.batch_all(Session)
        else:
            song_creator.create_in_batch(Session, args.batch)
    if args.merge:
        similar_songs.handle_close_songs(Session)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("example1.log"),
            logging.StreamHandler()
        ])
    global_connect()
    Session = get_session()
    init_searchable_song()
    parsed = parse_args()
    handle_args(parsed, Session)

    # song_creator.batch_all(Session)

    # continue_songs()
    # add_existing_songs()

#   do_entries()

# first = db_retriever.get_entry(Session, 1)
# second = db_retriever.get_entry(Session, 101)
#
# f_ss = SearchableSong(name=first.name, artist=first.artist)
# print(Search().query("match", title=second.name).query(
#     "match", artist=second.artist).execute())

# It looks like I'll need to use ids to prevent dupes, this means persistance is proably in the db
# for each, search for song, if not found persist song in db and in elasticsearch and use same id for both
#
