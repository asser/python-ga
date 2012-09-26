import datetime
import urllib2
import urlparse
from request import Request

class Campaign(object):

    TYPE_DIRECT = 'direct'
    TYPE_ORGANIC = 'organic'
    TYPE_REFERRAL = 'referral'

    def __init__(self, type=None):
        if type:
            self.type = type

            if type == self.TYPE_DIRECT:
                self.name = '(direct)'
                self.source = '(direct)'
                self.medium = '(none)'
            elif type == self.TYPE_REFERRAL:
                self.name = '(referral)'
                self.medium = 'referral'
            elif type == self.TYPE_ORGANIC:
                self.name = '(organic)'
                self.medium = 'organic'
            else:
                raise Exception('Campaign type has to be one of the TYPE_* '
                                'values')

        self.creation_time = datetime.datetime.now()

        self.response_count = 0
        self.id = None
        self.source = None
        self.g_click_id = None
        self.d_click_id = None
        self.name = None
        self.medium = None
        self.term = None
        self.content = None


    def from_utmz(self, value):
        """
        Will extract information for the "track_count" and "start_time"
        properties from the given "__utmz" cookie value.
        """
        params = value.split(Request.CAMPAIGN_DELIMITER)
        parts = params[0].split('.', 5)
        if len(parts) != 5:
            raise Exception('The given "__utmz" cookie value is invalid.')

        self.creation_time = datetime.datetime.fromtimestamp(float(parts[1]))
        self.response_count = int(parts[3])

        param_map = {
            'utmcid': 'id',
            'utmcsr': 'source',
            'utmgclid': 'g_click_id',
            'utmdclid': 'd_click_id',
            'utmccn': 'name',
            'utmcmd': 'medium',
            'utmctr': 'term',
            'utmcct': 'content',
        }
        
        for (key, val) in [x.split('=') for x in [parts[4]] + params[1:]]:
            setattr(self, param_map[key], urllib2.unquote(val))

        return self

    @classmethod
    def create_from_referrer(cls, url):
        obj = cls(cls.TYPE_REFERRAL)
        url_info = urlparse.urlparse(url)
        obj.source = url_info.netloc
        obj.content = url_info.path

        return obj

    def validate(self):
        # NOTE: gaforflash states that id and gClickId must also be specified,
        # but that doesn't seem to be correct
        if not self.source:
            raise Exception('Campaigns need to have at least the "source" '
                            'attribute defined.')

    def increase_response_count(amount = 1):
        self.response_count += amount


