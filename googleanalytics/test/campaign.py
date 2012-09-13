import unittest
import datetime
from googleanalytics import Campaign

class TestCampaign(unittest.TestCase):

    def test_from_utmz(self):
        campaign = Campaign()
        campaign.from_utmz('93487880.1346057154.6.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)')
        self.assertEqual(campaign.creation_time,
                         datetime.datetime.fromtimestamp(float('1346057154')))
        self.assertEqual(campaign.response_count, 4)
        self.assertEqual(campaign.id, None)
        self.assertEqual(campaign.source, 'google')
        self.assertEqual(campaign.name, '(organic)')
        self.assertEqual(campaign.medium, 'organic')
        self.assertEqual(campaign.term, '(not provided)')

if __name__ == '__main__':
    unittest.main()
