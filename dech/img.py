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
    def __init__(self, content, title=None, width=None, height=None, animation=False,
                 duration=100):
        """Initialize Img element

        Args:
            content (str, matplotlib figure, or ndarray): image content
            title (str): image title field
            width (int or str): image width (default units are pixels)
            height (int or str): image height (default units are pixels)
            animation (bool): whether content is an animation
            duration (int): delay in ms between frames
        """
        self.content = content
        self.title = title
        self.width = width
        self.height = height
        self.animation = animation
        self.duration = duration

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
            rescaled = (self.content * 255 / self.content.max()).astype('uint8')
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
        return f'<img style="{style}" src="{src}"/>'



def gif(x, duration=100):
    """Save image sequence as gif

    Args:
        savefile (str): path to save location
        x (torch.Tensor or numpy.ndarray): input data of shape (num_images, width, height)
            or (num_images, width, height, 3) for RGB images
        duration (int): delay in ms between frames
    """

    from PIL import Image

    # if grayscale input, convert to RGB
    if len(x.shape) == 3:
        imgs = [Image.fromarray(img, mode='L') for img in x]
    elif len(x.shape) == 4:
        imgs = [Image.fromarray(img, mode='RGB') for img in x]
    else:
        raise ValueError('Invalid size for x')

    # duration is the number of milliseconds between frames
    buff = BytesIO()
    imgs[0].save(buff, format='gif', save_all=True, append_images=imgs[1:], duration=duration, loop=0)
    return buff
