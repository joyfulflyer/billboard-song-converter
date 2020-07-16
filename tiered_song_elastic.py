import db_retriever
import db_saver
import logging
from models.tiered_song import SONG_TYPE_BASIC, SONG_TYPE_ELASTIC
import entry_generators
from collections import namedtuple
import elastic

logger = logging.getLogger(__name__)


class SongCreator():
    def __init__(self, session):
        self.session = session

    def create_in_batch(self, total, batch_size):
        pass

    def batch_all(self, batch_size=1000):
        pass


# these will be tiered songs

    def _match_songs(self, song):
        # check elastic for a close enough song
        # if close enough, link. If not, create new song and in elastic
        # the question always is, how to represent multiple names and artists in elastic search
        # I think I need an array of names and artists in elastic.
        # First pass will be known to be uniques
        results = elastic.search_name_artist(name=song.name,
                                             artist=song.artist)
        result = results.result
        # Default to 'check later'
        es = namedtuple('TieredSong', field_names=['id'])
        # mark to check later
        es.id = int(-1)
        if len(result) == 0:
            es = db_saver.create_tiered_song(self.session, song.name,
                                             song.artist, SONG_TYPE_ELASTIC)
            self._create_song_links(basic_song=song, elastic_song=es)
            elastic.create_searchable_from_song(es)  # hope this works

        pass

    # Link the entries of the basic song to the elastic song
    def _create_entry_links(self, basic_song, elastic_song):
        entries = db_retriever.get_entries_for_tiered_song(
            self.session, basic_song)
        for entry in entries:
            self._create_link(entry, elastic_song)

    # Link a basic and elastic song
    def _create_song_links(self, basic_song, elastic_song):
        song_link = db_saver.create_link_between_tiered_songs(
            self.session, basic_song.id, elastic_song.id)
        self._create_entry_links(basic_song=basic_song,
                                 elastic_song=elastic_song)
        return song_link

    def _create_link(self, entry, tiered_song):
        return db_saver.create_tiered_song_link(self.session,
                                                entry=entry,
                                                tiered_song=tiered_song)

    def _create_tiered_song(self, entry):
        return db_saver.create_tiered_song(self.session, entry.name,
                                           entry.artist, SONG_TYPE_BASIC)
