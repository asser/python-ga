class Event(object):

    def __init__(self, category=None, action=None, label=None, value=None,
                 non_interaction=False):
        self.category = category
        self.action = action
        self.label = label
        self.value = value
        self.non_interaction = non_interaction

    def validate(self):
        if not self.category or not self.action:
            raise Exception('Events need at least to have a category and '
                            'action defined.')
