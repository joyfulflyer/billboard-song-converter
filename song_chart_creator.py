from song_creator_base import SongCreator as song_creator_base
import logging

logger = logging.getLogger(__name__)

# creates tiered songs for each source


class SongCreator(song_creator_base):
    def create_in_batch(self, total, batch_size):
        raise NotImplementedError

    def batch_all(self, batch_size):
        for song in self._song_generator:
            entries = self._get_entries(song)
            charts = self._get_unique_charts_for_song(song)

            # get unique charts for song
            # separate out uk and us
            # create song for each
            # link correct entries to each song
            pass

    def _song_generator(self):
        pass

    def _get_unique_charts_for_song(self, song):
        # we can do this in database or do it in application
        # plusses and minuses to each.
        # if round-trip is truly the bottleneck we should do it in application
        # get entries for song
        # either find separate or
        pass

    def _separate():
        pass