import asyncio
import logging
import functools

from sqlalchemy import desc, exc

from models.chart import Chart
from models.entry import Entry
from models.song import Song

logger = logging.getLogger(__name__)


def create_song(name, artist, Session):
    with Session() as session:
        new_song = Song(name=name, artist=artist)
        session.add(new_song)
        session.commit()
        return new_song


async def create_song_async(name, artist, Session):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, functools.partial(create_song, name, artist, Session))


# whoops
# async def commit(session):
#     loop = asyncio.get_running_loop()
#     await loop.run_in_executor(None, session.commit)
