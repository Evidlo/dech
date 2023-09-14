#!/usr/bin/env python3

from .element import Element

class Paragraph(Element):

    def __init__(self, content, class_=""):
        """Initialize Paragraph element

        Args:
            content (str): text content
            class_ (str): custom class to apply
        """
        self.content = content
        self.class_ = class_

    def html(self, context={}):
        """Generate HTML for this element"""
       
        return f'<p class="{self.class_}">{self.content}</p>'
