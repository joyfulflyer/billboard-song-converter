import logging
import sys
import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import traceback

from models.base import Base

sys.path.append("/opt/")

logger = logging.getLogger(__name__)


# Returns a scoped session maker object
def connect(url):
    logger.error("Creating engine with url <%r>" % (url, ))
    traceback.print_stack()
    engine = create_engine(url)
    session_maker = sessionmaker(bind=engine)
    Session = scoped_session(session_maker)
    return Session


def create_url_from_parts(username, password, host, dbname):
    password = urllib.parse.quote_plus(password)
    url = "mysql+pymysql://%s:%s@%s/%s" % (username, password, host, dbname)
    logger.info("Created mysql url for %s/%s" % (host, dbname))
    return url


def create_tables(Session):
    session = Session()
    Base.metadata.create_all(session.get_bind().engine)
    session.close()
