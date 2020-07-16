#join table linking tiered songs together
from sqlalchemy import Column, Integer, String, ForeignKey

from models.base import Base
from models.tiered_song import Tiered_Song


class Tiered_Song_Link(Base):
    __tablename__ = 'tiered_song_links'

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer,
                     ForeignKey("%s.id" % (Tiered_Song.__tablename__)))

    to_id = Column(Integer, ForeignKey("%s.id" % (Tiered_Song.__tablename__)))

    def __repr__(self):
        return "Song to entry: <id=%r, from id=%r, to id=%r>" % \
            (self.id, self.from_id, self.to_id)
