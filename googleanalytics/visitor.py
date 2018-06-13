import datetime
import util
import re

class Visitor(object):

    def __init__(self):
        now = datetime.datetime.now()
        self._unique_id = None
        self.first_visit_time = now
        self.previous_visit_time = now
        self.current_visit_time = now
        self.visit_count = 1
        self.ip_address = None
        self.user_agent = ''
        self.locale = ''
        self.flash_version = None
        self.java_enabled = None
        self.screen_color_depth = ''
        self.screen_resolution = None

    @classmethod
    def from_utma(cls, value):
        parts = value.split('.')

        if len(parts) != 6:
            raise Exception('The given "__utma" cookie value is invalid.')

        obj = cls()
        obj.unique_id = long(parts[1])
        obj.first_visit_time = datetime.datetime.fromtimestamp(float(parts[2]))
        obj.previous_visit_time = datetime.datetime.fromtimestamp(float(parts[3]))
        obj.current_visit_time = datetime.datetime.fromtimestamp(float(parts[4]))
        obj.visit_count = int(parts[5])

        return obj

    def from_headers(self, headers):
        """
        Will extract information for the "ip_address", "user_agent" and "locale"
        properties from the given HTTP header dictionary.
        """
        try:
            # First IP address is the one of the client
            ip = headers['X_FORWARDED_FOR'].split(',')[0].strip()
        except KeyError:
            ip = headers.get('REMOTE_ADDR')

        if ip:
            # Double-check if the address has a valid format
            if re.match(r'^[\d+]{1,3}\.[\d+]{1,3}\.[\d+]{1,3}\.[\d+]{1,3}$',
                            ip, re.I):
                ip = None

            # Exclude private IP address ranges
            if re.match(r'^(?:127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)', ip):
                ip = None

        self.ip_address = ip

        self.user_agent = headers.get('HTTP_USER_AGENT')

        if 'HTTP_ACCEPT_LANGUAGE' in headers:
            parsed_locales = []
            res = re.findall(
                r'(^|\s*,\s*)([a-zA-Z]{1,8}(-[a-zA-Z]{1,8})*)\s*(;\s*q\s*=\s*(1(\.0{0,3})?|0(\.[0-9]{0,3})))?', 
                headers['HTTP_ACCEPT_LANGUAGE'], re.I)
            for r in res:
                name = r[1].replace('-', '_')
                value = 1 if not r[4] else r[4]
                parsed_locales += [(name, value)]

            self.locale = sorted(parsed_locales, key=lambda x: x[1],
                                 reverse=True)[0][0]

        return self

    def generate_hash(self):
        return util.generate_hash(self.user_agent + self.screen_resolution +
                                  self.screen_color_depth)

    def generate_unique_id(self):
        return ((util.generate_32bit_random() ^ self.generate_hash()) & 0x7fffffff)

    def set_unique_id(self, value):
        if value < 0 or value > 0x7fffffffffffffff:
            raise Exception('Visitor unique ID has to be a 64-bit integer '
                            'between 0 and %d.' % (0x7fffffffffffffff))

        self._unique_id = value

    def get_unique_id(self):
        if not self._unique_id:
            self._unique_id = self.generate_unique_id()

        return self._unique_id
    
    def add_session(self, session):
        start_time = session.start_time
        if start_time != self.current_visit_time:
            self.previous_visit_time = self.current_visit_time
            self.current_visit_time = start_time
            self.visit_count += 1

    unique_id = property(get_unique_id, set_unique_id)

