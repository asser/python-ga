from common import Request
from googleanalytics.util import X10
import math

class PageviewRequest(Request):
    
    X10_SITESPEED_PROJECT_ID = 14

    type = Request.TYPE_PAGE

    def build_parameters(self):
        p = super(PageviewRequest, self).build_parameters()

        p.utmp = self.page.path
        p.utmdt = self.page.title

        if self.page.charset:
            p.utmcs = self.page.charset

        if self.page.referrer:
            p.utmr = self.page.referrer

        if self.page.load_time:
            # Sample sitespeed measurements
            if p.utmn % 100 < self.config.sitespeed_sample_rate:
                x10 = X10()

                x10.clear_key(self.X10_SITESPEED_PROJECT_ID)
                x10.clear_value(self.X10_SITESPEED_PROJECT_ID)

                # Taken from ga.js code
                key = max(min(math.floor(self.page.load_time / 100.0), 5000), 0) * 100
                x10.set_key(self.X10_SITESPEED_PROJECT_ID, X10.OBJECT_KEY_NUM, key)

                x10.set_value(self.X10_SITESPEED_PROJECT_ID, X10.VALUE_VALUE_NUM, self.page.load_time)

                p.utme = x10.render_url_string()

        return p
