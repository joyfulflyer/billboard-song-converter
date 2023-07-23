import db_retriever

def entries_from_song_ids(session, songs):
    entries1 = db_retriever.get_entries_with_song_id(session, songs[0])
    entries2 = db_retriever.get_entries_with_song_id(session, songs[1])
    return entries1, entries2
