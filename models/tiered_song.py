from sqlalchemy import Column, Integer, String

from models.base import Base


class Tiered_Song(Base):
    __tablename__ = 'tiered_songs'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    artist = Column(String(128), nullable=False)
    song_type = Column(String(256), nullable=True)

    def __repr__(self):
        return "Song: <id=%r, name=%r>" % \
            (self.id, self.name)


SONG_TYPE_BASIC = "basic"  # simple match - name + artist
SONG_TYPE_ELASTIC = "elastic"  # matched with close enough elastic search
SONG_TYPE_MANUAL = "manual"  # manually confirmed to be the same song
# We want basic match songs first then we use those songs and match them to find more 'correct' songs
