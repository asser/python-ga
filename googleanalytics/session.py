import datetime
import util

class Session:

    def __init__(self):
        self.session_id = self.generate_session_id()
        self.track_count = 0
        self.start_time = datetime.datetime.now()

    @classmethod
    def from_utmb(cls, value):
        pass

    def generate_session_id(self):
        return util.generate_32bit_random()

