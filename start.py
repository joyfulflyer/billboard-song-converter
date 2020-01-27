import logging
import sys

from sqlalchemy.exc import ProgrammingError

import db_retriever as retriever
import elasticsearch_functions
import song_creator
from Session import get_session
import similar_songs
import elasticsearch_functions
import asyncio

sys.path.append("/opt/")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_songs(session):
    logger.info("Creating songs")
    song_creator.batch_all(session)
    logger.info("Created songs")


if __name__ == "__main__":
    import argument_parser
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("example1.log"),
            logging.StreamHandler()
        ])
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    args = argument_parser.get_args()
    session = get_session()()
    if args.seed:
        asyncio.run(elasticsearch_functions.add_existing_songs_async(session))
    if args.continue_songs:
        if args.number < 0:  # -1 and -2 are create all here
            create_songs(session)
        else:
            song_creator.create_in_batch(session, args.number)
    if args.merge:
        limit = float('inf')
        if args.number >= 0:
            limit = args.number
        asyncio.run(
            similar_songs.handle_close_songs_async(
                session, skip_user_input=args.user_input_disabled,
                limit=limit))
