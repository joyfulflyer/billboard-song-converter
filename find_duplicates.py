import db_retriever


def find_songs_with_duplicate_names(session):
    songs = db_retriever.get_songs(session)
    for song in songs:
        
        pass
    pass