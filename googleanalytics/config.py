class Config(object):

    def __init__(self, properties={}):

        self.fire_and_forget = False
        self.request_timeout = 1
        self.endpoint_host = 'www.google-analytics.com'
        self.endpoint_path = '/__utm.gif'
        self.anonymize_ip_addresses = False
        self.sitespeed_sample_rate = 1

