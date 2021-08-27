import asyncio
import logging
import sys

from sqlalchemy.exc import ProgrammingError

import elasticsearch_functions
import similar_songs
import song_creator
import tiered_song_creator
from Session import get_session

sys.path.append("/opt/")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _main():
    import argument_parser
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler("log1.log"),
                  logging.StreamHandler()])
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    args = argument_parser.get_args()
    if (args.copy != None):
        import copy_songs
        logger.error(args.copy)
        copy_songs.connect(args.copy[0], args.copy[1])
        return
    session = get_session(timeout=args.wait)()
    limit = float('inf')
    if args.number >= 0:
        limit = args.number
    if args.seed:
        asyncio.run(elasticsearch_functions.add_existing_songs_async(session))
    if args.continue_songs:
        if args.number < 0:  # -1 and -2 are create all here
            logger.info("Creating songs")
            song_creator.batch_all(session)
            logger.info("Created songs")
        else:
            song_creator.create_in_batch(session, args.number)
    if args.merge:
        similar_songs.handle_close_songs(
            session, skip_user_input=args.user_input_disabled, limit=limit)
    if args.force_create:
        similar_songs.handle_close_songs(session,
                                         skip_user_input=False,
                                         limit=limit,
                                         force_create_new_songs=True)
    if args.tier:
        tiered_song_creator.SongCreator(session).batch_all()

    if args.elastic_tier:
        import tiered_song_elastic
        tiered_song_elastic.SongCreator(session).batch_all()

    logger.info("done")


if __name__ == "__main__":
    _main()