from elasticsearch_dsl import Document, Text, Keyword


class SearchableSong(Document):
    name = Text(multi=True,
                fields={
                    'raw': Keyword(),
                    'standard': Text(),
                    'whitespace': Text(analyzer='whitespace'),
                    'simple': Text(analyzer='simple')
                })
    artist = Text(multi=True,
                  fields={
                      'raw': Keyword(),
                      'standard': Text(),
                      'whitespace': Text(analyzer='whitespace'),
                      'simple': Text(analyzer='simple')
                  })

    class Index:
        name = 'song'
