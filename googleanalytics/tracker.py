from config import Config
from request import *
import re

VERSION = '5.2.5' # As of 25.02.2012

class Tracker(object):

    def __init__(self, account_id, domain_name, config=None):
        if config:
            self.config = config
        else:
            self.config = Config()
        self.account_id = account_id
        self.domain_name = domain_name
        self.allow_hash = True
        self.custom_variables = []
        self._campaign = None

    def get_account_id(self):
        return self._account_id

    def set_account_id(self, value):
        if not re.match(r'^(UA|MO)-[0-9]*-[0-9]*$', value):
            raise Exception('%s is not a valid Google Analytics account ID.' %
                            (value))

        self._account_id = value
    account_id = property(get_account_id, set_account_id)

    def add_custom_variable(self, custom_variable):
        # Ensure that all required parameters are set
        custom_variable.validate()

        index = custom_variable.index
        self.custom_variables[index] = custom_variable

    def del_custom_variable(index):
        del self.custom_variables[index]

    def get_campaign(self):
        return self._campaign 

    def set_campaign(self, campaign=None):
        if campaign:
            # Ensure that all required parameters are set
            campaign.validate()

        self._campaign = campaign
    campaign = property(get_campaign, set_campaign)

    def track_page_view(self, page, session, visitor):
        request = PageviewRequest(self.config)
        request.page = page
        request.session = session
        request.visitor = visitor
        request.tracker = self
        request.fire()

    def track_event(self, event, session, visitor, page=None):
        # Ensure that all required parameters are set
        event.validate()

        request = EventRequest(self.config, page=page)
        request.event = event
        request.session = session
        request.visitor = visitor
        request.tracker = self
        request.fire()

    def track_transaction(self, transaction, session, visitor):
        # Ensure that all required parameters are set
        transation.validate()

        request = TransactionRequest(self.config)
        request.transaction = transaction
        request.session = session
        request.visitor = visitor
        request.tracker = self
        request.fire()

    def track_social(self, social_interaction, page, session, visitor):
        request = SocialInteractionRequest(self.config)
        request.social_interaction = social_interaction
        request.page = page
        request.session = session
        request.visitor = visitor
        request.tracker = tracker
        request.fire()

