import unittest
import datetime
from googleanalytics import Visitor, Session

class TestVisitor(unittest.TestCase):

    def test_from_utma(self):
        visitor = Visitor.from_utma(
            '93487880.1228187775.1345905697.1345905697.1347552475.2')
        self.assertEqual(visitor.unique_id, 1228187775)
        self.assertEqual(visitor.first_visit_time,
                         datetime.datetime.fromtimestamp(float('1345905697')))
        self.assertEqual(visitor.previous_visit_time,
                         datetime.datetime.fromtimestamp(float('1345905697')))
        self.assertEqual(visitor.current_visit_time,
                         datetime.datetime.fromtimestamp(float('1347552475')))
        self.assertEqual(visitor.visit_count, 2)

    def test_64bit_visitor(self):
        "Tests that the Visitor.from_utma method is able to handle 64-bit visitor IDs"
        visitor = Visitor.from_utma(
            '26821871.3028119289228160000.1235579004.1367328504.1367394766.237'
        )
        self.assertEqual(visitor.unique_id, 3028119289228160000)
        
    def test_session(self):
        session = Session()
        visitor = Visitor.from_utma(
            '93487880.1228187775.1345905697.1345905697.1347552475.2')
        visitor.add_session(session)

        self.assertEqual(visitor.previous_visit_time,
                         datetime.datetime.fromtimestamp(float('1347552475')))
        self.assertEqual(visitor.visit_count, 3)
        self.assertEqual(visitor.current_visit_time, session.start_time)

    def test_headers(self):
        headers = {
            'REMOTE_ADDR': '77.66.19.249',
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS '
                'X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405',
            'HTTP_ACCEPT_LANGUAGE': 'da,sv,en',
        }
        visitor = Visitor.from_utma(
            '93487880.1228187775.1345905697.1345905697.1347552475.2'
        ).from_headers(headers)

        self.assertEqual(visitor.user_agent, headers['HTTP_USER_AGENT'])
        self.assertEqual(visitor.locale, 'da')
        self.assertEqual(visitor.ip_address, headers['REMOTE_ADDR'])


if __name__ == '__main__':
    unittest.main()
