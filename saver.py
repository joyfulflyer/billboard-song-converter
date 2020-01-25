import logging

from sqlalchemy import and_

from models.chart import Chart
from models.entry import Entry

logger = logging.getLogger(__name__)


def save_chart(chart, Session, on_saved=None):
    session = Session()
    nextDate = getattr(chart, 'nextDate', '')
    db_chart = Chart(chart_type=chart.name,
                     date_string=chart.date,
                     next_chart_date=nextDate)
    session.add(db_chart)
    try:
        session.commit()
    except Exception as err:
        logger.error("caught a integrety error for chart '{0}'".format(err))
        session.rollback()

    rowId = db_chart.id
    if rowId is None:
        rowId = session.query(Chart.id).filter(
            and_(Chart.chart_type == db_chart.chart_type,
                 Chart.date_string == db_chart.date_string))
    for entry in chart.entries:
        e = Entry(name=entry.title,
                  artist=entry.artist,
                  place=entry.rank,
                  peak_position=entry.peakPos,
                  last_position=entry.lastPos,
                  weeks_on_chart=entry.weeks,
                  chart_id=rowId)
        try:
            session.add(e)
            session.commit()
        except Exception as err:
            logger.error(
                "\n\ncaught a integrety error on add entry '{0}'".format(err))
            session.rollback()
    try:
        session.commit()
    except Exception as err:
        logger.error(
            "caught a integrety error on commit entries '{0}'".format(err))
        session.rollback()
    if on_saved is not None:
        on_saved(chart.date)
