# song manipulation generators
# Every function should be a generator that outputs entries for conversion to songs
#
import db_retriever

STEP = 5000


def entries_without_song_id_steps(session, limit=float('inf')):
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


def entries_with_no_tiered_songs_singular(session):
    entries = _all_entries(session)
    for entry in entries:
        yield entry


def _all_entries(session):
    return db_retriever.get_entries_with_no_tiered_song(session).all()