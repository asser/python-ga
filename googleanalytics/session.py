import datetime
import util

class Session(object):

    def __init__(self):
        self.session_id = self.generate_session_id()
        self.track_count = 0
        self.start_time = datetime.datetime.now()

    @classmethod
    def from_utmb(cls, value):
        parts = value.split('.')
        if len(parts) != 4:
            raise Exception('The given "__utmb" cookie value is invalid.')

        obj = cls()
        obj.track_count = int(parts[1])

        # XXX: Sometimes the __utmb cookie contains microsecond-timestamps
        start_time = float(parts[3])
        if len(parts[3]) >= 13:
            start_time = start_time / 1e3
        obj.start_time = datetime.datetime.fromtimestamp(start_time)
        return obj

    def generate_session_id(self):
        return util.generate_32bit_random()

