import itertools
import logging
import re
import string
import time
from collections import namedtuple
import asyncio

import db_retriever
import db_saver
import elastic

ARTIST_WORDS_TO_IGNORE = ['feat', 'featuring', 'vs', 'ft']
STEP = 5000

logger = logging.getLogger(__name__)


def handle_close_songs(Session, skip_user_input=False, limit=5000):
    asyncio.run(
        handle_close_songs_async(Session,
                                 skip_user_input=skip_user_input,
                                 limit=limit))


async def handle_close_songs_async(Session, skip_user_input=False, limit=5000):
    startTime = time.time()
    session = Session()
    for entries in _gen(session, limit):
        groupStartTime = time.time()
        sorted_entries = sorted(entries,
                                key=lambda entry: (entry.name, entry.artist))
        # Assume sorted
        futures = [
            _handle_group(list(group),
                          session,
                          skip_user_input=skip_user_input)
            for _, group in itertools.groupby(
                sorted_entries, key=lambda entry: (entry.name, entry.artist))
        ]
        await asyncio.gather(*futures)
        groupFinishTime = time.time()
        diff = groupFinishTime - groupStartTime
        logger.error(
            f'Took {time.strftime("%H:%M:%S", time.gmtime(diff))} to correct {STEP} songs'
        )

    finalTime = time.time()
    diff = finalTime - startTime
    logger.error(
        f'Took {time.strftime("%H:%M:%S", time.gmtime(diff))} to correct {limit} songs'
    )


def _gen(session, limit=float('inf')):
    step = STEP
    if limit < step:
        step = limit

    offset = 0
    while offset + step <= limit:
        entries = db_retriever.get_entries_with_song_id_pagination(
            session, -1, limit=step, offset=offset)
        if len(entries) > 0:
            yield entries
        else:
            return
        offset = offset + step


async def _handle_group(group, session, skip_user_input=False):
    entry = group[0]
    await _handle_potential_same_song(entry, session, bypass=skip_user_input)
    for e in group:
        e.song_id = entry.song_id
    await db_saver.commit(session)


async def _handle_potential_same_song(entry, session, bypass=False):
    # Check to see if we have an exact match
    # If we don't, check search and ask
    song_query = db_retriever.get_song_id_query_for(entry.name, entry.artist,
                                                    session)
    song_count = song_query.count()
    db_song = None
    if song_count == 1:
        db_song = song_query.first()
    else:
        results = await elastic.search_name_artist_async(name=entry.name,
                                                         artist=entry.artist)
        if results.count > 0:
            first_result = results.result[0]
            same = further_comparison_checks(entry, first_result)
            if same:
                songId = first_result.meta.id
                db_song = namedtuple('Song', field_names=['id'])
                db_song.id = int(songId)
            else:
                if bypass:
                    return
                should_create_new = _get_input_for_song(entry, first_result)
                if should_create_new.lower().strip() == 'n':
                    songId = first_result.meta.id
                    db_song = namedtuple('Song', field_names=['id'])
                    db_song.id = int(songId)
                else:
                    db_song = await _create_db_async(entry.name, entry.artist,
                                                     session)
        else:
            db_song = await _create_db_async(entry.name, entry.artist, session)

    entry.song_id = db_song.id
    # Not sure if needed
    await db_saver.commit(session)


def further_comparison_checks(entry, search_result):
    # transform
    # compare
    # transform more
    # compare
    comparison_object = SongComparison()
    comparison_object.entry_name = entry.name
    comparison_object.search_name = search_result.name
    comparison_object.entry_artist = entry.artist
    comparison_object.search_artist = search_result.artist

    lower_cased = _strip_and_lower(comparison_object)
    if lower_cased.compare():
        return True
    no_curly_brackets = lower_cased.transform_with(
        lambda piece: re.sub(r'\{[^}]+\}', '', piece).strip())
    if no_curly_brackets.compare():
        return True
    no_punctuation = lower_cased.transform_with(
        lambda f: _strip_punctuation(f))
    if no_punctuation.compare():
        return True
    reduced = no_curly_brackets.transform_with(
        lambda f: _strip_punctuation(f)).transform_with(
            lambda piece: _remove_key_words_remove_spaces(piece))
    if reduced.compare():
        return True
    return False


def _create_db(name, artist, session):
    db_song = db_saver.create_song(name, artist, session)
    elastic.create_searchable_from_song(db_song)
    return db_song


async def _create_db_async(name, artist, session):
    db_song = await db_saver.create_song_async(name, artist, session)
    await elastic.create_searchable_from_song_async(db_song)
    return db_song


def _compare_fields_with(entry, search_result, func):
    return func(entry.name) == func(search_result.name) and func(
        entry.artist) == func(search_result.artist)


def _strip_and_lower(song_comparison):
    return song_comparison.transform_with(lambda piece: piece.strip().lower())


def _strip_punctuation(s):
    return s.translate(str.maketrans('', '', string.punctuation))


def _remove_key_words_remove_spaces(s):
    return ''.join(
        filter(lambda x: x.lower() not in ARTIST_WORDS_TO_IGNORE,
               s.split(' ')))


def _log_entry_result(entry, first_result):
    logger.error(
        f"((\"{entry.name}\", \"{entry.artist}\"), (\"{first_result.name}\", \"{first_result.artist}\"), {first_result.meta.score}),"
    )
    pass


def _get_input_for_song(entry, result):
    return input(
        "Entry:  name= {:<55s} artist= {:<50s}\n".format(
            entry.name, entry.artist) +
        "Result: name= {:<55s} artist= {:<50s}\n".format(
            result.name, result.artist) +
        f"score:{result.meta.score}. Create new song? (y/n) no entry creates a song: "
    )


class SongComparison():
    entry_name = ""
    entry_artist = ""
    search_name = ""
    search_artist = ""

    # def __init__(self, initial_entry, initial_search_result):
    #     # # Originals just in case
    #     # self.initial_entry_name = initial_entry.name
    #     # self.initial_entry_artist = initial_entry.artist
    #     # self.initial_search_name = initial_search_result.name
    #     # self.initial_search_artist = initial_search_result.artist

    #     self.entry_name = initial_entry.name
    #     self.entry_artist = initial_entry.artist
    #     self.search_name = initial_search_result.name
    #     self.search_artist = initial_search_result.artist
    def compare(self):
        return self.entry_name == self.search_name and self.entry_artist == self.search_artist

    # Return new copy with func called on all fields
    def transform_with(self, func):
        new_comparison = SongComparison()
        new_comparison.entry_name = func(self.entry_name)
        new_comparison.entry_artist = func(self.entry_artist)
        new_comparison.search_name = func(self.search_name)
        new_comparison.search_artist = func(self.search_artist)
        return new_comparison


if __name__ == '__main__':
    import Session
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("correcting songs.log"),
            logging.StreamHandler()
        ])

    Session = Session.get_session()
    asyncio.run(handle_close_songs(Session))
