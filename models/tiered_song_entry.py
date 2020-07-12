#join table linking tiered songs and entries
from sqlalchemy import Column, Integer, String, ForeignKey

from models.base import Base
from models.tierd_song import Tiered_Song
from models.entry import Entry


class Tiered_Song_Entry(Base):
    __tablename__ = 'tierd_song_entry'

    id = Column(Integer, primary_key=True)
    tiered_song_id = Column(Integer,
                            ForeignKey("%s.id" % (Tiered_Song.__tablename__)))

    entry_id = Column(Integer, ForeignKey("%s.id" % (Entry.__tablename__)))

    def __repr__(self):
        return "Song to entry: <id=%r, song id=%r, entry id=%r>" % \
            (self.id, self.tiered_song_id, self.entry_id)
