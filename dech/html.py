#!/usr/bin/env python3

from .element import Element

class HTML(Element):

    def __init__(self, content):
        """Raw HTML

        Args:
            content (str): HTML content
        """
        self.content = content

    def html(self, context={}):
        """Generate HTML for this element"""

        return self.content
