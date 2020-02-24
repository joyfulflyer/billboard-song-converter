import asyncio
import concurrent.futures
import logging
import time
from itertools import groupby
from collections import namedtuple

import db_retriever
import elastic
import Session
from elasticsearch_client.client import global_connect

MIN_SAFE_SCORE = 25
STEP = 5000

logger = logging.getLogger(__name__)


async def add_existing_songs_async(session):
    loop = asyncio.get_running_loop()
    loop.set_default_executor(concurrent.futures.ThreadPoolExecutor())
    elastic.init_searchable_song()
    startTime = time.time()

    for db_songs in _gen(session):
        afterDbTime = time.time()
        diff = afterDbTime - startTime
        futures = [
            elastic.create_searchable_from_song_dict_async(song)
            for song in db_songs
        ]
        await asyncio.gather(*futures)
        partialTime = time.time()
        diff = partialTime - afterDbTime
        logging.error(
            f'Took {time.strftime("%H:%M:%S", time.gmtime(diff))} for {STEP} songs'
        )
        await asyncio.sleep(0.1)  # To try to prevent timeouts

    finalTime = time.time()
    diff = finalTime - startTime
    logging.error(
        f'Took {time.strftime("%H:%M:%S", time.gmtime(diff))} to save songs')


def _gen(session):
    offset = 0

    while True:
        db_songs = db_retriever.get_songs_with_alternate_entries_except_id_pagination(
            session, -1, limit=STEP, offset=offset)
        dict_songs = _convert_to_grouped_dict(db_songs)
        if len(dict_songs) > 0:
            yield dict_songs
        else:
            return
        offset = offset + STEP


def _convert_to_grouped_dict(db_songs):
    """
    {
        songId,
        entries: [ (name, artist) ]
    }
    """
    def song_id_key(song):
        return (song.song_id, song.name, song.artist)

    sorted_db_songs = sorted(db_songs, key=song_id_key)
    grouped = groupby(sorted_db_songs, key=lambda song: song.song_id)
    expanded = map(lambda song: {
        'songId': song[0],
        'entries': list(song[1])
    }, grouped)
    pruned = list(
        map(
            lambda song: {
                'songId':
                song['songId'],
                'entries':
                list(map(lambda entry: (entry[0], entry[1]), song['entries']))
            }, expanded))
    return pruned


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("example1.log"),
            logging.StreamHandler()
        ])
    global_connect()
    session = Session.get_session()()
    for i in range(200):
        a = db_retriever.get_songs_with_alternate_entries_except_id_pagination(
            session, -1, limit=1, offset=i)
        if len(a) > 1:
            print(a)
            break
    # elastic.init_searchable_song()
    # asyncio.run(add_existing_songs_async(session))
