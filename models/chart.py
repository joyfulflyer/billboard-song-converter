from sqlalchemy import Column, Integer, String

from models.base import Base


class Chart(Base):
    __tablename__ = 'charts'

    id = Column(Integer, primary_key=True)
    chart_type = Column('type', String(128))
    date_string = Column(String(128))
    next_chart_date = Column(String(128))

    def get_year(self):
        return self.date_string.split('-')[0]

    def __repr__(self):
        return "Chart: <id=%r, chart type=%r, date=%r>" % (
            self.id, self.chart_type, self.date_string)
