from pathlib import Path
import textwrap
from importlib import resources

from .img import Img
from .html import HTML
from .paragraph import Paragraph
from .element import Element
from .code import Code

__all__ = ['Img', 'HTML', 'Paragraph', 'Code', 'Page', 'Grid', 'Figure', 'img_sync_js']

img_sync_js = open(resources.files('dech') / 'img_sync.js').read()

class Figure(Element):
    """Generate <figure> and <figcaption>"""

    def __init__(self, caption, element, class_="", pos='bottom'):
        self.caption = caption
        self.element = element
        self.pos = pos
        self.class_ = class_

    def html(self, context={}):
        el_html = self.element.html(context)
        cap_html = self.caption
        if self.pos == 'bottom':
            return f'<figure class="{self.class_}"><figcaption>{cap_html}</figcaption>{el_html}</figure>'


class Grid(Element):
    """Elements in a grid with each row separated by a <br>"""

    def __init__(self, content):
        """Initialize Grid

        Args:
            content (Element or list(Element) or list(list(Element)))
        """
        self.content = content

    def html(self, context={}):
        row_strs = []
        if type(self.content) is list:
            for row in self.content:
                if type(row) is list:
                    row_strs.append('\n'.join(item.html(context) for item in row))
                elif hasattr(row, 'html'):
                    row_strs.append(row.html(context))
                else:
                    raise TypeError(f"Unsupported object {type(row)}")
        elif hasattr(self.content, 'html'):
            row_strs = [self.content.html(context)]
        else:
            raise TypeError(f"Unsupported object {type(self.content)}")

        result = ''
        for row_str in row_strs:
            result += f'<div class="row">{row_str}</div>'

        return result


class Page(Grid):
    """Header + footer wrapper to make complete HTML page"""

    def __init__(self, content, header=None, footer=None, css=None, head_extra=""):
        """Intialize page with content

        Args:
            content (Element): dech element with .html() function
            header (str or None): replace default header HTML
            footer (str or None): replace default footer HTML
            css (str or None): extra css styling to insert into <head>
            head_extra (str or None): extra HTML to insert into <head> such as JS
        """
        self.content = content

        if header is None:
            default_css = open(resources.files('dech') / 'styles.css').read()
            self.header = textwrap.dedent(f"""\
            <!doctype html>
            <html>
            <head>
                <style>
                {default_css}
                {css}
                {head_extra}
                </style>
            </head>
            <body>
            """)
        else:
            self.header = header
        if footer is None:
            self.footer = textwrap.dedent(f"""\
            </html>
            </body>
            """)
        else:
            self.footer = footer

    def html(self, context={}):
        return self.header + super().html(context) + self.footer

    def save(self, outfile):
        """Save page to file

        Args:
            outfile (str): save location
        """
        outfile = Path(outfile)
        context = {'outfile': outfile}
        with open(outfile, 'w') as f:
            f.write(self.html(context))
