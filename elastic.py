import asyncio
import concurrent.futures
import functools
import logging
from collections import namedtuple

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match

from database.config import Config
from elasticsearch_client.client import global_connect
from elasticsearch_client.song import SearchableSong

MIN_SAFE_SCORE = 25
MIN_SCORE_FOR_INQUERY = 18

logger = logging.getLogger(__name__)

# if Config.elasticsearch_host is not None:
#     global_connect(Config.elasticsearch_host)
# else:
#     logger.error("Unable to connect to elasticsearch, no host")


def create_searchable_from_song(song):
    song_dict = {'entries': [(song.name, song.artist)], 'songId': song.id}
    create_searchable_from_song_dict(song_dict)


def create_searchable_from_song_dict(song_dict):
    '''
    Input should look like: {
        entries : [(name, artist)],
        songId: songId
    }
    '''
    names = list(map(lambda entry: entry[0], song_dict['entries']))
    artists = list(map(lambda entry: entry[1], song_dict['entries']))
    searchable = SearchableSong(name=names, artist=artists)
    searchable.meta.id = song_dict['songId']
    searchable.save()


async def create_searchable_from_song_dict_async(song_dict):
    await asyncio.get_running_loop().run_in_executor(
        None, functools.partial(create_searchable_from_song_dict, song_dict))


def search_name_artist(name, artist):
    s = Search().query(Match(name=name)).query(
        Match(artist={
            "query": artist,
            "boost": 0.5
        })).extra(min_score=MIN_SCORE_FOR_INQUERY)
    Result = namedtuple("SearchResult", ["result", "count"])
    result = s.execute().hits
    count = s.count()
    return Result(result=result, count=count)


async def search_name_artist_async(name, artist):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, functools.partial(search_name_artist, name, artist))


def init_searchable_song():
    SearchableSong.init()
