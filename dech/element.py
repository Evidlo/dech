#!/usr/bin/env python3

class Element:
    """Parent class for building blocks on a page"""

    def save(self, outfile):
        raise NotImplementedError

    def html(self, context={}):
        """Generate HTML for this element

        Args:
            context (dict): extra variables used in generating HTML

        Returns:
            html (str): generated HTML
        """
        raise NotImplementedError
