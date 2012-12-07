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

        # Test that domain names with dots are handled correctly
        campaign = Campaign()
        campaign.from_utmz('1.1354284425.1.1.utmcsr=du113w.dub113.mail.live.com|utmccn=(referral)|utmcmd=referral|utmcct=/mail/InboxLight.aspx')
        self.assertEqual(campaign.source, 'du113w.dub113.mail.live.com')

    def test_create_from_referrer(self):
        campaign = Campaign.create_from_referrer(
            'http://www.google.dk/aclk?sa=L&ai=CKlaN9kBgUPuSBYHL8QOc04D4Dauih'
            'LwCo5zdnDPG16brFggAEAEoAlChytmjB2DRmbmCiAjIAQGpAqf8vOjKUYc-qgQjT'
            '9A1ysTd4R29eLJVCvuARQXfOybpRrnEXTk8pSpxRaCXeIU&sig=AOD64_2LXWpV-'
            '1EajlJobt0MNp0t8o_00g&ved=0CBoQ0Qw&adurl=http://duck-it.dk&rct=j'
            '&q=%22ideas+for+start+up%22'
        )

        self.assertEqual(campaign.source, 'www.google.dk')
        self.assertEqual(campaign.content, '/aclk')

if __name__ == '__main__':
    unittest.main()
