import asyncio
import functools
import logging
from typing import Iterable

from sqlalchemy import desc, exc

from models.chart import Chart
from models.entry import Entry
from models.song import Song
from models.tiered_song import SONG_TYPE_BASIC, Tiered_Song
from models.tiered_song_entry import Tiered_Song_Entry
from models.tiered_song_link import Tiered_Song_Link

logger = logging.getLogger(__name__)


def create_song(name, artist, session):
    new_song = Song(name=name, artist=artist)
    return _commit_and_return(session, new_song)


async def create_song_async(name, artist, session):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, functools.partial(create_song, name, artist, session))


def create_tiered_song(session, name, artist, song_type):
    new_tiered_song = Tiered_Song(name=name,
                                  artist=artist,
                                  song_type=song_type)
    return _commit_and_return(session, new_tiered_song)


def create_tiered_song_link(session, entry, tiered_song):
    new_entry = Tiered_Song_Entry(entry_id=entry.id,
                                  tiered_song_id=tiered_song.id)
    return _commit_and_return(session, new_entry)


def create_link_between_tiered_songs(session, from_id, to_id):
    new_link = Tiered_Song_Link(from_id=from_id, to_id=to_id)
    return _commit_and_return(session, new_link)


def _commit_and_return(session, item):
    session.add(item)
    session.commit()
    return item

def add_to_session(session, item):
    if item is Iterable:
        for i in item:
            session.add(i)
    else:
        session.add(item)
    return session

def commit(session):
    session.commit()
    return session
