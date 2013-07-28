# Temporary classes 

from utils.core import Singleton

class Index:
    __metaclass__ = Singleton

    default_links = {}
    all_pages     = []
    page_info     = {}

    def resolve_alias(self, path):
        return path
