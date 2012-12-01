import unittest
import new_datetime
from googleanalytics import Session

# Monkey patched datetime to provide constant now()
# See http://stackoverflow.com/questions/1049551/dictionaries-with-volatile-values-in-python-unit-tests

import datetime
constant_now = datetime.datetime.now()
old_datetime_class = datetime.datetime
class new_datetime(datetime.datetime):
    @staticmethod
    def now():
        return constant_now

datetime.datetime = new_datetime

class TestSession(unittest.TestCase):

    def test_init(self):
        s = Session()
        self.assertGreaterEqual(s.session_id, 0)
        self.assertLessEqual(s.session_id, 0x7fffffff)
        self.assertEqual(s.track_count, 0)
        self.assertEqual(s.start_time, datetime.datetime.now())

    def test_generate_session_id(self):
        s = Session()
        id = s.generate_session_id()
        self.assertGreaterEqual(id, 0)
        self.assertLessEqual(id, 0x7fffffff)

    def test_from_utmb(self):
        session = Session.from_utmb('93487880.42.10.1347552475')
        self.assertEqual(session.start_time,
                         datetime.datetime.fromtimestamp(float('1347552475')))
        self.assertEqual(session.track_count, 42)


    def test_millisecond_timestamp(self):
        session = Session.from_utmb('93487880.42.10.1347552475123')
        self.assertEqual(session.start_time,
                         datetime.datetime.fromtimestamp(float('1347552475.123')))



if __name__ == '__main__':
    unittest.main()
