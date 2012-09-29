from googleanalytics import util, Config
import abc
import urllib2, urllib
import sys

# urlencode taken from urllib and patched to allow for supplying quote method
def urlencode(query, doseq=0, quote_via=urllib.quote):  # {{{
    """Encode a sequence of two-element tuples or dictionary into a URL query string.

    If any values in the query arg are sequences and doseq is true, each
    sequence element is converted to a separate parameter.

    If the query arg is a sequence of two-element tuples, the order of the
    parameters in the output will match the order of parameters in the
    input.
    """

    try:
        unicode
    except NameError:
        def _is_unicode(x):
            return 0
    else:
        def _is_unicode(x):
            return isinstance(x, unicode)

    if hasattr(query,"items"):
        # mapping objects
        query = query.items()
    else:
        # it's a bother at times that strings and string-like objects are
        # sequences...
        try:
            # non-sequence items should not work with len()
            # non-empty strings will fail this
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
            # zero-length sequences of all types will get here and succeed,
            # but that's a minor nit - since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved for consistency
        except TypeError:
            ty,va,tb = sys.exc_info()
            raise TypeError, "not a valid non-string sequence or mapping object", tb

    l = []
    if not doseq:
        # preserve old behavior
        for k, v in query:
            k = quote_via(str(k))
            v = quote_via(str(v))
            l.append(k + '=' + v)
    else:
        for k, v in query:
            k = quote_via(str(k))
            if isinstance(v, str):
                v = quote_via(v)
                l.append(k + '=' + v)
            elif _is_unicode(v):
                # is there a reasonable way to convert to ASCII?
                # encode generates a string, but "replace" or "ignore"
                # lose information and "strict" can raise UnicodeError
                v = quote_via(v.encode("ASCII","replace"))
                l.append(k + '=' + v)
            else:
                try:
                    # is this a sufficient test for sequence-ness?
                    len(v)
                except TypeError:
                    # not a sequence
                    v = quote_via(str(v))
                    l.append(k + '=' + v)
                else:
                    # loop over the sequence
                    for elt in v:
                        l.append(k + '=' + quote_via(str(elt)))
    return '&'.join(l)
# end urlencode }}}

class HttpRequest(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None):
        if config:
            self.config = config
        else:
            self.config = Config()

    def build_http_request(self):
        parameters = self.build_parameters()

        # Make sure urllib.quote does not have safe='/' as it does per default
        def quote_qs(x):
            return urllib.quote(x, '')
        query_string = urlencode(parameters.to_dict(), quote_via=quote_qs)
        query_string = util.convert_to_uri_component_encoding(query_string)

        use_post = len(query_string) > 2036

        headers = {}

        if self.user_agent:
            headers['User-Agent'] = self.user_agent

        if self.x_forwarded_for:
            headers['X-Forwarded-For'] = self.x_forwarded_for

        url = 'http://%s%s' % (self.config.endpoint_host,
                               self.config.endpoint_path)
        if use_post:
            # Don't ask me why "text/plain", but ga.js says so :)
            headers['Content-Type'] = 'text/plain'
            r = urllib2.Request(url, data=parameters.to_dict(), headers=headers)
        else:
            url += '?%s' % (util.convert_to_uri_component_encoding(
                urlencode(parameters.to_dict(), quote_via=quote_qs)))
            r = urllib2.Request(url, headers=headers)

        return r
        
    @abc.abstractmethod
    def build_parameters(self):
        return


    def _send(self):
        request = self.build_http_request()
        response = None

        if self.config.endpoint_host:
            timeout = self.config.request_timeout

            response = urllib2.urlopen(request, timeout=timeout)

            meta = response.info()
            content = response.read()

        logging_callback = self.config.logging_callback
        if logging_callback:
            logging_callback(request, response)

        return response

    def fire(self):
        # Tore out PHP specific shutdown function code
        self._send()


class Request(HttpRequest):
    __metaclass__ = abc.ABCMeta

    TYPE_PAGE = None
    TYPE_EVENT = 'event'
    TYPE_TRANSACTION = 'tran'
    TYPE_ITEM = 'item'
    TYPE_SOCIAL = 'social'
    # This type of request is deprecated in favor of encoding custom variables
    # within the "utme" parameter, but we include it here for completeness
    # See:http://code.google.com/apis/analytics/docs/gaJS/gaJSApiBasicConfiguration.html#_gat.GA_Tracker_._setVar
    TYPE_CUSTOMVARIABLE = 'var'
    X10_CUSTOMVAR_NAME_PROJECT_ID = 8
    X10_CUSTOMVAR_VALUE_PROJECT_ID = 9
    X10_CUSTOMVAR_SCOPE_PROJECT_ID = 11
    CAMPAIGN_DELIMITER = '|'

    def build_http_request(self):
        self.x_forwarded_for = self.visitor.ip_address
        self.user_agent = self.visitor.user_agent

        # Increment session track counter for each request
        self.session.track_count += 1

        if self.session.track_count > 500:
            raise Exception('Google Analytics does not guarantee to process '
                            'more than 500 requests per session.')

        if self.tracker.campaign:
            self.tracker.campaign.response_count += 1

        return super(Request, self).build_http_request()

    def build_parameters(self):
        p = util.ParameterHolder()

        p.utmac = self.tracker.account_id
        p.utmhn = self.tracker.domain_name

        p.utmt = self.type
        p.utmn = util.generate_32bit_random()
        
        # The "utmip" parameter is only relevant if a mobile analytics ID
        # (MO-123456-7) was given,
        # see http://code.google.com/p/php-ga/issues/detail?id=9
        p.utmip = self.visitor.ip_address
        
        p.aip = 1 if self.tracker.config.anonymize_ip_addresses else None
        if p.aip:
            # Anonymize last IP block 
            p.utmip = p.utmip[-p.utmip.rfind('.')] + '.0'

        p.utmhid = self.session.session_id
        p.utms   = self.session.track_count

        p = self.build_visitor_parameters(p)
        p = self.build_customvariables_parameter(p)
        p = self.build_campaign_parameters(p)
        p = self.build_cookie_parameters(p)

        return p

    def build_visitor_parameters(self, p):
        # Ensure correct locale format, see https://developer.mozilla.org/en/navigator.language
        p.utmul = self.visitor.locale.replace('_', '-').lower()

        if self.visitor.flash_version:
            p.utmfl = self.visitor.flash_version

        if self.visitor.java_enabled:
            p.utmje = self.visitor.java_enabled

        if self.visitor.screen_color_depth:
            p.utmsc = self.visitor.screen_color_depth
        p.utmsr = self.visitor.screen_resolution

        return p

    def build_customvariables_parameter(self, p):
        custom_vars = self.tracker.custom_variables

        if custom_vars:
            if len(custom_vars) > 5:
                # See # http://code.google.com/intl/de-DE/apis/analytics/docs/tracking/gaTrackingCustomVariables.html#usage
                raise Exception('The sum of all custom variables cannot exceed '
                                '5 in any given request.')

            # TODO: Implement this

        return p

    def build_cookie_parameters(self, p):
        domain_hash = self.generate_domain_hash()

        p._utma = '.'.join([
            str(domain_hash), 
            str(self.visitor.unique_id),
            self.visitor.first_visit_time.strftime('%s'),
            self.visitor.previous_visit_time.strftime('%s'),
            self.visitor.current_visit_time.strftime('%s'),
            str(self.visitor.visit_count),
        ]) + '.'

        p._utmb = '.'.join([
            str(domain_hash),
            str(self.session.track_count),
            # FIXME: What does "token" mean? I only encountered a value of 10 in # my tests.
            str(10),
            self.session.start_time.strftime('%s')
        ]) + '.'

        p._utmc = domain_hash

        cookies = [ '__utma=%s;' % (p._utma) ]
        if p._utmz:
            cookies.append('__utmz=%s;' % (p._utmz))
        if p._utmv:
            cookies.append('__utmv=%s;' % (p._utmv))

        p.utmcc = '+'.join(cookies)

        return p

    def build_campaign_parameters(self, p):
        campaign = self.tracker.campaign

        if campaign:
            p._utmz = '.'.join([
                str(self.generate_domain_hash()),
                campaign.creation_time.strftime('%s'),
                str(self.visitor.visit_count),
                str(campaign.response_count),
            ]) + '.'

            data = {
                'utmcid':   campaign.id,
                'utmcsr':   campaign.source,
                'utmgclid': campaign.g_click_id,
                'utmdclid': campaign.d_click_id,
                'utmccn':   campaign.name,
                'utmcmd':   campaign.medium,
                'utmctr':   campaign.term,
                'utmcct':   campaign.content,
            }

            p._utmz += self.CAMPAIGN_DELIMITER.join([
                ('%s=%s' % (key, value.replace('+', '%20').replace(' ', '%20')))
                for (key, value) in data.items() if value is not None
            ])

        return p

    def generate_domain_hash(self):
        hash = 1

        if self.tracker.allow_hash:
            hash = util.generate_hash(self.tracker.domain_name)

        return hash

