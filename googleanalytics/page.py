class Page(object):

    REFERRER_INTERNAL = 0

    def __init__(self, path):
        self.path = path

    def set_path(self, path):
        if path and path[0] != '/':
            raise Exception('The page path should always start with a slash '
                            '("/").')

        self.path = path

