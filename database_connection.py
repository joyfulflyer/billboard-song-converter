import time
import logging
import sys
import urllib.parse

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import traceback

from models.base import Base

sys.path.append("/opt/")

logger = logging.getLogger(__name__)


# Returns what I understand to be a session maker object
def connect(url):
    logger.error("Creating engine with url <%r>" % (url, ))
    traceback.print_stack()
    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    return Session


def create_url_from_parts(username, password, host, dbname, db_type="mysql+pymysql"):
    password = urllib.parse.quote_plus(password)
    url = "%s://%s:%s@%s/%s" % (db_type, username, password, host, dbname)
    logger.info("Created mysql url for %s/%s" % (host, dbname))
    return url


def create_tables(Session):
    session = Session()
    Base.metadata.create_all(session.get_bind().engine)
    session.close()


def wait_for_db_connection(Session, timeout=180):
    start_time = time.time()
    end_time = start_time + time.time()
    while end_time > time.time():
        sleep_time = 5
        try:
            logger.info("Attempting connection")
            Session().execute('show tables')
            logger.info("Connection successful")
            return True
        except exc.OperationalError as err:
            logger.info(f"Unable to connect: {err}")
            logger.info(f"Sleeping for {sleep_time}")
            time.sleep(sleep_time)
            # no exponential backoff
    return False
