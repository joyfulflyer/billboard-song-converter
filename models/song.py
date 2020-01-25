from sqlalchemy import Column, Integer, String

from models.base import Base


class Song(Base):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    artist = Column(String(128), nullable=False)
    spotify_id = Column(Integer, nullable=True)
    search_term = Column(String(256), nullable=True)
    search_results = Column(Integer, nullable=True)

    def __repr__(self):
        return "Song: <id=%r, name=%r, spotify_id=%r>" % \
            (self.id, self.name, self.spotify_id)
