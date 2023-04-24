from pathlib import Path
from tempfile import gettempdir
from io import BytesIO
# import PIL.Image
import imageio
import base64
import textwrap
from importlib import resources

class Element:
    """Parent class for building blocks on a page"""

    def save(self, outfile):
        raise NotImplementedError

    def html(self, context):
        """Generate HTML for this element

        Args:
            context (dict): extra variables used in generating HTML

        Returns:
            html (str): generated HTML
        """
        raise NotImplementedError


class Img(Element):
    """Generate <img> tag for PNGs or GIFs"""

    def __init__(self, content, gif=False, title=None, width=None, height=None):
        """Initialize Img element

        Args:
            content (str, matplotlib figure, or ndarray): image content

            FIXME: not implemented
            gif (bool): whether content is an animation

            title (str): image title field
            width (int or str): image width in pixels
        """
        self.content = content
        self.title = title
        self.width = width
        self.height = height

    def html(self, context):

        # generate styling
        styles = []
        width = self.width
        if type(width) is int:
            width = f"{width}px"
        if width is not None:
            styles.append(f"width:{width}")
        height = self.height
        if type(height) is int:
            height = f"{height}px"
        if height is not None:
            styles.append(f"width:{width}")

        # if given path to image
        if type(self.content) is str:
            src = self.content

        # if given matplotlib figure
        if type(self.content).__name__ == 'Figure':
            buff = BytesIO()
            self.content.savefig(buff, format='png')
            src = 'data:image/png;base64,{}'.format(
                base64.b64encode(buff.getvalue()).decode()
            )

        # if given numpy array
        if type(self.content).__name__ == 'ndarray':
            buff = BytesIO()
            imageio.imsave(buff, (255 * self.content).astype('uint8'), format='png')
            src = 'data:image/png;base64,{}'.format(
                base64.b64encode(buff.getvalue()).decode()
            )
            styles.append("image-rendering:crisp-edges")

        style = ";".join(styles)
        return f'<img style="{style}" src="{src}"/>'

class Figure(Element):
    """Generate <figure> and <figcaption>"""

    def __init__(self, caption, element, pos='bottom'):
        self.caption = caption
        self.element = element
        self.pos = pos

    def html(self, context):
        el_html = self.element.html(context)
        cap_html = self.caption
        if self.pos == 'bottom':
            return f'<figure class="figure"><figcaption>{cap_html}</figcaption>{el_html}</figure>'

class Grid(Element):
    """Elements in a grid with each row separated by a <br>"""

    def __init__(self, content):
        """Initialize Grid

        Args:
            content (Element or list(Element) or list(list(Element)))
        """
        self.content = content

    def html(self, context):
        row_strs = []
        if type(self.content) is list:
            for row in self.content:
                if type(row) is list:
                    row_strs.append('\n'.join(item.html(context) for item in row))
                elif hasattr(row, 'html'):
                    row_strs.append(row.html(context))
                else:
                    raise ValueError(f"Unsupported object {type(row)}")
        elif hasattr(self.content, 'html'):
            row_strs = [self.content.html(context)]
        else:
            raise ValueError(f"Unsupported object {type(self.content)}")

        result = ''
        for row_str in row_strs:
            result += f'<div class="row">{row_str}</div>'

        return result

class Page(Grid):
    """Header + footer wrapper to make complete HTML page"""

    def __init__(self, content, header=None, footer=None):
        """Intialize page with content

        Args:
            content (Element): dech element with .html() function
            header (str or None): replace default header HTML
            footer (str or None): replace default footer HTML
        """
        self.content = content

        if header is None:
            css = open(resources.files('dech') / 'styles.css').read()
            self.header = textwrap.dedent(f"""\
            <!doctype html>
            <html>
            <head>
                <style>
                {css}
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

    def html(self, context):
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
