from elasticsearch import Elasticsearch
import logging

from elasticsearch_dsl import connections

logger = logging.getLogger(__name__)


def global_connect(host='localhost'):
    logger.error(f'Connecting to host:{host}')
    connections.create_connection(hosts=[{
        'host': host,
        'port': 9200
    }],
                                  timeout=20)


def connect_elasticsearch():
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    return _es


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)