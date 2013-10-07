from common import Request
from googleanalytics.util import X10

class EventRequest(Request):

    X10_EVENT_PROJECT_ID = 5
    type = Request.TYPE_EVENT

    def __init__(self, *args, **kwargs):
        # Remove the page argument for the Request constructor
        page = kwargs.get('page')
        del kwargs['page']
        super(EventRequest, self).__init__(*args, **kwargs)
        self.page = page

    def build_parameters(self):
        p = super(EventRequest, self).build_parameters()

        if self.page:
            p.utmp = self.page['path']
            p.utmdt = self.page['title']

        x10 = X10()

        x10.clear_key(self.X10_EVENT_PROJECT_ID)
        x10.clear_value(self.X10_EVENT_PROJECT_ID)

        # Object / Category
        x10.set_key(self.X10_EVENT_PROJECT_ID, X10.OBJECT_KEY_NUM,
                    self.event.category)
        
        # Event type / Action
        x10.set_key(self.X10_EVENT_PROJECT_ID, X10.TYPE_KEY_NUM,
                    self.event.action)

        if self.event.label:
            # Event Description / Label
            x10.set_key(self.X10_EVENT_PROJECT_ID, X10.LABEL_KEY_NUM,
                        self.event.label)

        if self.event.value:
            x10.set_value(self.X10_EVENT_PROJECT_ID, X10.VALUE_VALUE_NUM,
                          self.event.value)

        p.utme += x10.render_url_string()

        if self.event.non_interaction:
            p.utmni = 1

        return p
