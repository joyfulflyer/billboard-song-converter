from song_creator_base import SongCreator as song_creator_base
import logging
import db_saver
import db_retriever

logger = logging.getLogger(__name__)

# creates tiered songs for each source
# go through tiered songs
# for each create a song for each source (us or uk charts)
# every song should create at least 1 new song
# link entries to the corresponding song


class SongCreator(song_creator_base):
    def create_in_batch(self, total, batch_size):
        raise NotImplementedError

    def batch_all(self, batch_size):
        for song in self._song_generator():
            entries = self._get_entries(song)
            charts = self._get_unique_charts_for_song(song)
            new_songs = self._create_songs_for_each_chart(charts)
            self._link_old_and_new_songs(song, new_songs)
            self._link_entries_to_new_songs(entries, new_songs)
            self.commit()

    def _song_generator(self):
        songs = db_retriever.get_songs_with_no_chart_song(self.session)
        return

    def _get_unique_charts_for_song(self, song):
        # we can do this in database or do it in application
        # plusses and minuses to each.
        # if round-trip is truly the bottleneck we should do it in application
        # get entries for song
        # either find separate or
        return []

    def _get_entries(self, song):
        return []

    def _create_songs_for_each_chart(self, charts):
        return []

    def _link_entries_to_new_songs(self, entries, new_songs):
        pass

    def _link_old_and_new_songs(self, old_song, new_song_array):
        pass

    def commit(self):
        db_retriever.finish_transaction(self.session)
