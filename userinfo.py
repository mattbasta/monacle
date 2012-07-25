
class UserInfo(object):
    """
    nickname: What we're to call the user
    latitude
    longitude
    """

    def __init__(self, session):
        self.session = session
        self.load_data()

    def load_data(self):
        pass

    def commit(self):
        pass
