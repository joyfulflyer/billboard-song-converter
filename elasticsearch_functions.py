import asyncio
import concurrent.futures
import logging
import time

import db_retriever
import elastic
import Session
from elasticsearch_client.client import global_connect

MIN_SAFE_SCORE = 25
STEP = 2000

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


def _gen(session):
    offset = 0
    while True:
        db_songs = db_retriever.get_songs_except_id_pagination(session,
                                                               -1,
                                                               limit=STEP,
                                                               offset=offset)
        if len(db_songs) > 0:
            yield db_songs
        else:
            return
        offset = offset + STEP


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
    elastic.init_searchable_song()
    asyncio.run(add_existing_songs_async(session))
