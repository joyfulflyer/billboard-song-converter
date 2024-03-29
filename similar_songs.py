import itertools
import logging
import re
import string
import sys
import time
from collections import namedtuple

import db_retriever
import db_saver
import entry_generators

ARTIST_WORDS_TO_IGNORE = ['feat', 'featuring', 'vs', 'ft', 'the']
STEP = 5000
TRANSFORMS = {re.compile(r' and '): '&', re.compile(r' with '): '&'}

logger = logging.getLogger(__name__)


def handle_close_songs(session,
                       skip_user_input=False,
                       limit=5000,
                       force_create_new_songs=False):
    startTime = time.time()
    for entries in entry_generators.entries_without_song_id_steps(
            session, limit):
        groupStartTime = time.time()
        sorted_entries = sorted(entries,
                                key=lambda entry: (entry.name, entry.artist))
        # Assume sorted
        for _, group in itertools.groupby(sorted_entries,
                                          key=lambda entry:
                                          (entry.name, entry.artist)):
            _handle_group(list(group),
                          session,
                          skip_user_input=skip_user_input,
                          force_create_new_songs=force_create_new_songs)

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


def _handle_group(group,
                  session,
                  skip_user_input=False,
                  force_create_new_songs=False):
    entry = group[0]
    _handle_potential_same_song(entry,
                                session,
                                bypass=skip_user_input,
                                force=force_create_new_songs)
    for e in group:
        e.song_id = entry.song_id
    session.commit()


def _handle_potential_same_song(entry, session, bypass=False, force=False):
    pass
#     # Check to see if we have an exact match
#     # If we don't, check search and ask
#     # need to update search if alternate found - if the song id is the same
#     song_query = db_retriever.get_song_id_query_for(entry.name, entry.artist,
#                                                     session)
#     song_count = song_query.count()
#     db_song = None
#     if song_count == 1:
#         db_song = song_query.first()
#     else:
#         results = elastic.search_name_artist(name=entry.name,
#                                              artist=entry.artist)
#         if results.count > 0:
#             first_result = results.result[0]
#             same = further_comparison_checks(entry, first_result)
#             if same:
#                 songId = first_result.meta.id
#                 db_song = namedtuple('Song', field_names=['id'])
#                 db_song.id = int(songId)
#             else:
#                 should_create_new = ''
#                 if bypass:
#                     return

#                 if force:
#                     should_create_new = ''
#                 else:
#                     should_create_new = _get_input_for_song(
#                         entry, results.result)

#                 if should_create_new.lower().strip() == 'n':
#                     songId = first_result.meta.id
#                     db_song = namedtuple('Song', field_names=['id'])
#                     db_song.id = int(songId)
#                 elif should_create_new.isnumeric():
#                     db_song = namedtuple('Song', field_names=['id'])
#                     db_song.id = int(should_create_new)
#                 elif should_create_new.lower().strip() == 'q':
#                     sys.exit(0)
#                 else:
#                     db_song = _create_db(entry.name, entry.artist, session)
#         else:
#             db_song = _create_db(entry.name, entry.artist, session)

#     entry.song_id = db_song.id


def further_comparison_checks(entry, search_result):
    # transform
    # compare
    # transform more
    # compare
    comparison_object = SongComparison()
    comparison_object.entry_name = entry.name
    comparison_object.search_name = search_result.name[0]
    comparison_object.entry_artist = entry.artist
    comparison_object.search_artist = search_result.artist[0]

    lower_cased = _strip_and_lower(comparison_object)
    if lower_cased.compare():
        return True
    no_curly_brackets = lower_cased.transform_with(
        lambda piece: _remove_curly_brackets(piece))
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
    transformed = no_curly_brackets \
            .transform_with(_transform_name_artist) \
            .transform_with(_strip_punctuation) \
            .transform_with(_remove_key_words_remove_spaces)
    if transformed.compare():
        return True
    return False


# def _create_db(name, artist, session):
#     db_song = db_saver.create_song(name, artist, session)
#     elastic.create_searchable_from_song(db_song)
#     return db_song


def _strip_and_lower(song_comparison):
    return song_comparison.transform_with(lambda piece: piece.strip().lower())


def _strip_punctuation(s):
    return s.translate(str.maketrans('', '', string.punctuation))


def _remove_key_words_remove_spaces(s):
    return ''.join(
        filter(lambda x: x.lower() not in ARTIST_WORDS_TO_IGNORE,
               s.split(' ')))


def _remove_curly_brackets(s):
    return re.sub(r'\{[^}]+\}', '', s).strip()


def _log_entry_result(entry, first_result):
    logger.error(
        f"((\"{entry.name}\", \"{entry.artist}\"), (\"{first_result.name}\", \"{first_result.artist}\"), {first_result.meta.score}),"
    )
    pass


# This is probably not the most efficient way to do this
def _transform_name_artist(entry):
    transformer = entry
    # for each key, transform it in to value
    for key, value in TRANSFORMS.items():
        if re.match(key, transformer):
            logger.error(f"Found match {key} for '{transformer}'")
        transformer = re.sub(key, value, transformer)

    return transformer


def _get_input_for_song(entry, results):
    lines = [
        "Entry:  name= {:<55s} artist= {:<50s}\n".format(
            entry.name, entry.artist)
    ]
    for result in results:
        lines.append(
            "Result: name= {:<55s} artist= {:<50s} id= {:<10s}\n".format(
                result.name[0], result.artist[0], result.meta.id))
    lines.append(
        f"Create new song? (y/n) no entry creates a song or a number uses that as an id, q to quit: "
    )
    return input(''.join(lines))


class SongComparison():
    entry_name = ""
    entry_artist = ""
    search_name = ""
    search_artist = ""

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

    session = Session.get_session()()
    handle_close_songs(session, skip_user_input=False)
