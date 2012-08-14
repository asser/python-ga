import random
import urllib
import tracker

def encode_uri_component(value):
    return self.convert_to_uri_component_encoding(urllib.quote(encoded_value))

def convert_to_uri_component_encoding(encoded_value):
    replace = {
        '%21': '!',
        '%2A': '*',
        '%27': '\'',
        '%28': '(',
        '%29': ')',
    }
    for key in replace:
        encoded_value = encoded_value.replace(key, replace[key])

    return encoded_value

def generate_32bit_random(fr=0, to=0x7fffffff):
    return random.randint(fr, to)

def generate_hash(string):
    """
    Generates a hash for input string

    See  http://code.google.com/p/gaforflash/source/browse/trunk/src/com/google/analytics/core/Utils.as#44
    """
    hash = 1

    if string and len(string) > 0:
        hash = 0

        for pos in xrange(len(string) - 1, 0, -1):
            current = ord(string[pos])
            hash = ((hash << 6) & 0xfffffff) + current + (current << 14)
            leftmost7 = hash & 0xfe00000
            if leftmost7 != 0:
                hash ^= leftmost7 >> 21

    return hash


class X10(object):

    OBJECT_KEY_NUM = 1
    TYPE_KEY_NUM = 2
    LABEL_KEY_NUM = 3
    VALUE_VALUE_NUM = 1

    def __init__(self):
        self.project_data = {}

        self.KEY = 'k'
        self.VALUE = 'v'
        self.SET = ['k', 'v']
        self.DELIM_BEGIN = '('
        self.DELIM_END = ')'
        self.DELIM_SET = '*'
        self.DELIM_NUM_VALUE = '!'

        self.ESCAPE_CHAR_MAP = {
            "'": "'0",
            ")": "'1",
            "*": "'2",
            "!": "'3",
        }

        self.MINIMUM = 1

    def has_project(self, project_id):
        return self.project_data.has_key(project_id)

    def set_key(self, project_id, num, value):
        self.set_internal(project_id, self.KEY, num, value)

    def get_key(self, project_id, num):
        self.get_internal(project_id, self.KEY, num)

    def clear_key(self, project_id):
        self.clear_internal(project_id, self.KEY)

    def set_value(self, project_id, num, value):
        self.set_internal(project_id, self.VALUE, num, value)

    def get_value(self, project_id, num):
        self.get_internal(project_id, self.VALUE, num)

    def clear_value(self, project_id):
        self.clear_internal(project_id, self.VALUE)

    def set_internal(self, project_id, type, num, value):
        """Shared internal implementation for setting an X10 data type."""
        if not self.project_data.has_key(project_id):
            self.project_data[project_id] = {}

        if not self.project_data[project_id].has_key(type):
            self.project_data[project_id][type] = {}

        self.project_data[project_id][type][num] = value

    def get_internal(self, project_id, type, num):
        """Shared internal implementation for getting an X10 data type."""
        try:
            return self.project_data[project_id][type][num]
        except KeyError:
            return None

    def clear_internal(self, project_id, type):
        """
        Shared internal implementation for clearing all X10 data of a type from
        a certain project.
        """
        try:
            del self.project_data[project_id][type]
        except KeyError:
            pass

    def escape_extensible_value(self, value):
        """Escape X10 string values to remove ambiguity for special characters."""
        result = ''

        for c in str(value):
            try:
                result += self.ESCAPE_CHAR_MAP[c]
            except KeyError:
                result += c

        return result

    def render_data_type(self, data):
        """Given a data array for a certain type, render its string encoding."""
        result = []
        
        last_i = 0
        for (i, entry) in sorted(data.items()):
            if entry:
                s = ''
                
                # Check if we need to append the number. If the last number was
                # outputted, or if this is the assumed minimum, then we don't.
                if i != self.MINIMUM and i-1 != last_i:
                    s += i
                    s += self.DELIM_NUM_VALUE

                s = self.escape_extensible_value(entry)
                result.append(s)

            last_i = i

        return self.DELIM_BEGIN + self.DELIM_SET.join(result) + self.DELIM_END

    def render_project(self, project):
        """Given a project dict, render its string encoding."""
        result = ''

        # Do we need to output the type string? As an optimization we do not
        # output the type string if it's the first type, or if the previous type
        # was present.
        need_type_qualifier = False

        for i in xrange(0, len(self.SET)):
            try:
                data = project[self.SET[i]]

                if need_type_qualifier: 
                    result += self.SET[i]
                result += self.render_data_type(data)
                need_type_qualifier = False
            except KeyError:
                need_type_qualifier = True
   
        return result

    def render_url_string(self):
        """
        Generates the URL parameter string for the current internal extensible
        data state
        """
        result = ''

        for (project_id, project) in self.project_data.items():
            result += str(project_id) + self.render_project(project)

        return result


class ParameterHolder(object):

    def __init__(self):
        self.utmwv = tracker.VERSION
        self.utmac = None
        self.utmhn = None
        self.utmt  = None
        self.utms  = None
        self.utmn  = None
        self.utmcc = None
        self.utme  = ''
        self.utmni = None
        self.aip   = None
        self.utmu  = None
        self.utmp  = None
        self.utmdt = None
        self.utmcs = '-'
        self.utmr  = '-'
        self.utmip = None
        self.utmul = None
        self.utmfl = '-'
        self.utmje = '-'
        self.utmsc = None
        self.utmsr = None
        self._utma = None
        self.utmhid = None
        self._utmb = None
        self._utmc = None

        # E-Commerce parameters
        self.utmipc = None
        "Product Code. This is the sku code for at given product, e.g. '989898ajssi'"

        self.utmipn = None
        "Product Name, e.g. 'T-shirt'"

        self.utmipr = None
        "Unit Price. Value is set to numbers only, e.g. 19.95"

        self.utmiqt = None
        "Unit Quantity, e.g. 4"

        self.utmiva = None
        "Variations on an item, e.g. 'white', 'black', 'green' etc."

        self.utmtid = None
        "Order ID, e.g. 'a2343898'"

        self.utmtst = None
        "Affiliation"

        self.utmtto = None
        "Total Cost, e.g. 20.00"

        self.utmttx = None
        "Tax cost, e.g. 4.23"

        self.utmtsp = None
        "Shipping Cost, e.g. 3.95"

        self.utmtci = None
        "Billing City, e.g. 'Cologne'"

        self.utmtrg = None
        "Billing Region, e.g. 'North Rhine-Westphalia'"

        self.utmtco = None
        "Billing Country, e.g. 'Germany'"

        # Campaign parameters
        self.utmcn = None
        """
        Starts a new campaign session. Either utmcn or utmcr is present on any
        given request, but newer both at the same time. Changes the campaign
        tracking data; but does not start a new session. Either 1 or not set.

        Found in gaforflash but not in ga.js, so we do not use it, but it will
        stay here for documentation completeness.
        """

        self.utmcr = None
        """
        Indicates a repeat campaign visit. This is set when any subsequent
        clicks occur on the same link. Either utmcn or utmcr is present on any
        given request, but never both at the same time. Either 1 or not set.

        Found in gaforflash but not in ga.js, so we do not use it, but it will
        stay here for documentation completeness.
        """

        self.utmcid = None
        "Campaign ID, a.k.a. 'utm_id' query parameter for ga.js"

        self.utmcsr = None
        "Source, a.k.a. 'utm_source' query parameter for ga.js"

        self.utmgclid = None
        "Google AdWords Click ID, a.k.a. 'gclid' query parameter for ga.js"

        self.utmdclid = None
        "Not known for sure, but expected to be a DoubleClick Ad Click ID"

        self.utmccn = None
        "Name, a.k.a. 'utm_campaign' query parameter for ga.js"

        self.utmcmd = None
        "Medium, a.k.a. 'utm_medium' query parameter for ga.js"

        self.utmctr = None
        "Terms/Keywords, a.k.a. 'utm_term' query parameter for ga.js"

        self.utmcct = None
        "Ad Content Description, a.k.a. 'utm_content' query parameter for ga.js"

        self.utmcvr = None
        "Unknown so far. Found it in ga.js."

        self._utmz = None
        """
        Campaign tracking cookie parameter.
        
        This cookie stores the type of referral used by the visitor to reach
        your site, whether via a direct method, a referring link, a website
        search, or a campaign such as an ad or an email link.

        It is used to calculate search engine traffic, ad campaigns and page
        navigation within your own site.
        The cookie is updated with each page view to your site.

        Expiration:
        6 months from set/update.

        Format:
        __utmz=<domainHash>.<campaignCreation>.<campaignSessions>.<responseCount>.<campaignTracking>
        """
        self._utmz  = None

        # Social tracking parameters
        self.utmsn = None
        self.utmsa = None
        self.utmsid = None

        # Google Website Optimizer (GWO) parameters
        self._utmx = None
        # TODO: Implementation needed
        """
	    Deprecated custom variables cookie parameter.
	    
	    This cookie parameter is no longer relevant as of migration from setVar() to
	    setCustomVar() and hence not supported by this library, but will stay here for
	    documentation completeness.
	    
	    The __utmv cookie passes the information provided via the setVar() method,
	    which you use to create a custom user segment.
	    
	    Expiration:
	    2 years from set/update.
	    
	    Format:
	    __utmv=<domainHash>.<value>
        """

        # Custom Variables parameters (deprecated)
        self._utmv = None
        # TODO: Implementation needed?
        """
	    Deprecated custom variables cookie parameter.
	    
	    This cookie parameter is no longer relevant as of migration from setVar() to
	    setCustomVar() and hence not supported by this library, but will stay here for
	    documentation completeness.
	    
	    The __utmv cookie passes the information provided via the setVar() method,
	    which you use to create a custom user segment.
	    
	    Expiration:
	    2 years from set/update.
	    
	    Format:
	    __utmv=<domainHash>.<value>
	    
	    http://code.google.com/p/gaforflash/source/browse/trunk/src/com/google/analytics/data/UTMV.as
        """

    def to_dict(self):
        return dict((name, getattr(self, name)) for name in self.__dict__ if not
                    name.startswith('_') and getattr(self, name) is not None)
