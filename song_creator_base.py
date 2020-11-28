class SongCreator():
    def __init__(self, session):
        self.session = session

    def create_in_batch(self, total, batch_size):
        raise NotImplementedError

    def batch_all(self, batch_size):
        raise NotImplementedError
