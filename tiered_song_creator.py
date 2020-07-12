import db_retriever
import db_saver
import logging
from models.tierd_song import SONG_TYPE_BASIC
import entry_generators

logger = logging.getLogger(__name__)


class SongCreator():
    def __init__(self, session):
        self.session = session

    def create_in_batch(self, total, batch_size):
        pass

    def batch_all(self, batch_size):
        pass

    def process_songs(self):
        for entry in entry_generators.entries_with_no_tiered_songs_singular(
                self.session):
            self._entry_to_tiered_song(entry)

    def _entry_to_tiered_song(self, entry):
        tiered_song = db_retriever.get_tierd_song_for(self.session, entry.name,
                                                      entry.artist)
        if tiered_song is None:
            tiered_song = self._create_tiered_song(entry)
        self._create_link(entry, tiered_song)

    def _create_link(self, entry, tiered_song):
        return db_saver.create_tiered_song_link(self.session,
                                                entry=entry,
                                                tiered_song=tiered_song)

    def _create_tiered_song(self, entry):
        return db_saver.create_tiered_song(self.session, entry.name,
                                           entry.artist, SONG_TYPE_BASIC)
