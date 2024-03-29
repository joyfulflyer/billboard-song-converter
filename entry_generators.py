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

        # step is lower of limit and batch size

    offset = 0
    while offset <= limit:
        entries = entry_func(session=session, step=step, offset=offset)
        if len(entries) > 0:
            yield entries
        else:
            return
        offset = offset + step


def _calculate_step(limit, batch_size):
    step = batch_size
    if limit < step:
        step = limit
    return step


# Gives list of steps
def _step_2(limit, step):
    offset = 0
    while offset <= limit:
        yield offset
        offset = offset + step


# Returns individual entries.
def entries_with_no_tiered_songs_singular(session,
                                          limit=float('inf'),
                                          batch_size=STEP):
    step = _calculate_step(limit, batch_size)
    for offset in _step_2(limit, step):
        if offset > limit:
            return
        entries = _get_entries_with_no_tiered_song_limited_offset(
            session, step, offset)
        if len(entries) == 0:
            return
        for entry in entries:
            yield entry


def get_items(session,
              limit=float('inf'),
              batch_size=STEP,
              retrieve_function=db_retriever.get_entries,
              return_full_batch=True):
    return _get_entries_by_step(session=session,
                                limit=limit,
                                batch_size=batch_size,
                                entry_function=retrieve_function,
                                return_full_batch=return_full_batch)


def get_entries(session, limit=float('inf'), batch_size=STEP):
    return _get_entries_by_step(session,
                                limit,
                                batch_size,
                                db_retriever.get_entries,
                                return_full_batch=True)


# copied from entries_with_no_tierd_songs_singular to be made more generic
def _get_entries_by_step(session,
                         limit=float('inf'),
                         batch_size=STEP,
                         entry_function=None,
                         return_full_batch=False):
    if not callable(entry_function):
        raise Exception('Function required')
    step = _calculate_step(limit, batch_size)
    for offset in _step_2(limit, step):
        if offset > limit:
            return
        entries = entry_function(session, step, offset)
        if len(entries) == 0:
            return
        if return_full_batch:
            yield entries
        else:
            for entry in entries:
                yield entry


def _get_entries_with_no_tiered_song_limited_offset(session, step, offset):
    return db_retriever.get_entries_with_no_tiered_song(session,
                                                        limit=step,
                                                        offset=offset)


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
