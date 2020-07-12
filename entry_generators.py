import db_retriever
from instrument import instrument

STEP = 5000


# Applies a step function to the entry func
# entry_func returns lists (or generators) of entries
# Iterate over this to get lists to iterate over
# We're mostly generating a step and an offset but using those to get the lists of entries
def _step_generator(session, entry_func, limit, batch_size):
    step = batch_size
    if limit < step:
        step = limit

    offset = 0
    while offset + step <= limit:
        entries = entry_func(session=session, step=step, offset=offset)
        if len(entries) > 0:
            yield entries
        else:
            return
        offset = offset + step


# Returns individual entries.
def entries_with_no_tiered_songs_singular(session,
                                          limit=float('inf'),
                                          batch_size=STEP):
    for entries in _step_generator(
            session, _get_entries_with_no_tiered_song_limited_offset, limit,
            batch_size):
        for entry in entries:
            yield entry


def _get_entries_with_no_tiered_song_limited_offset(session, step, offset):
    return db_retriever.get_entries_with_no_tiered_song(session,
                                                        limit=step,
                                                        offset=offset)
