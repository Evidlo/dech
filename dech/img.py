#!/usr/bin/env python3

from dataclasses import dataclass
from io import BytesIO
import imageio
import base64

from .element import Element
from .common import handle_torch

class Img(Element):
    """Generate <img> tag for PNGs or GIFs"""

    @handle_torch()
    def __init__(self, content, class_="", title=None, width=None, height=None, animation=False,
                 duration=3, rescale=True, vmin=0, vmax=None):
        """Initialize Img element

        Args:
            content (str, matplotlib figure, or ndarray): image content
            class_ (str): custom class to apply
            title (str): image title field
            width (int or str): image width (default units are pixels)
            height (int or str): image height (default units are pixels)
            animation (bool): whether content is an animation
            duration (float): Total animation time in seconds.  Default is 3
            vmin (float): minimum data value for scaling dynamic range.  default 0
            vmax (float): minimum data value for scaling dynamic range.  default `content` max
        """
        self.content = content
        self.class_ = class_
        self.title = title
        self.width = width
        self.height = height
        self.animation = animation
        self.duration = duration
        self.vmin = vmin
        self.vmax = vmax

    def html(self, context={}):

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
            styles.append(f"height:{height}")

        # if given path to image
        if type(self.content) is str:
            src = self.content

        # if given matplotlib figure
        elif type(self.content).__name__ == 'Figure':
            buff = BytesIO()
            self.content.savefig(buff, format='png')
            src = 'data:image/png;base64,{}'.format(
                base64.b64encode(buff.getvalue()).decode()
            )

        # if given numpy array
        elif type(self.content).__name__ == 'ndarray':
            buff = BytesIO()
            styles.append("image-rendering:crisp-edges")
            # rescale image stack to 0-255
            vmax = self.vmax if self.vmax is not None else self.content.max()
            rescaled = (255 * (self.content - self.vmin) / (vmax - self.vmin)).astype('uint8')
            if self.animation:
                buff = gif(rescaled, duration=self.duration)
                src = 'data:image/gif;base64,{}'.format(
                    base64.b64encode(buff.getvalue()).decode()
                )
            else:
                imageio.imsave(buff, rescaled, format='png')
                src = 'data:image/png;base64,{}'.format(
                    base64.b64encode(buff.getvalue()).decode()
                )

        else:
            raise TypeError(f"Unsupported object {type(self.content)}")

        style = ";".join(styles)
        return f'<img class="{self.class_}" style="{style}" src="{src}"/>'



def gif(x, duration=3):
    """Save image sequence as gif

    Args:
        savefile (str): path to save location
        x (torch.Tensor or numpy.ndarray): input data of shape (num_images, width, height)
            or (num_images, width, height, 3) for RGB images
        duration (float): Total animation time in seconds.  Default is 3
    """

    from PIL import Image

    # if grayscale input, convert to RGB
    if len(x.shape) == 3:
        imgs = [Image.fromarray(img, mode='L') for img in x]
    elif len(x.shape) == 4:
        imgs = [Image.fromarray(img, mode='RGB') for img in x]
    else:
        raise ValueError('Invalid size for x')

    buff = BytesIO()
    imgs[0].save(buff, format='gif', save_all=True, append_images=imgs[1:], duration=duration * 1000 // x.shape[0], loop=0)
    return buff
