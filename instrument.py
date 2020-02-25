import time
import logging

logger = logging.getLogger(__name__)


# Log how long a function takes to run
def instrument(func):
    def wrapper(*args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        endtime = time.time()
        diff = endtime - startTime
        logger.info(
            f'Took {time.strftime("%H:%M:%S", time.gmtime(diff))} to get songs'
        )
        return result

    return wrapper
