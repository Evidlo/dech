#!/usr/bin/env python3

from dataclasses import dataclass
from io import BytesIO
import imageio
import base64
import math

from .element import Element
from .common import handle_torch

class Img(Element):
    """Generate <img> tag for PNGs or GIFs"""

    @handle_torch()
    def __init__(self, content, class_="", title=None, width=None, height=None, animation=False,
                 duration=3, rescale='frame', format=None):
        """Initialize Img element

        Args:
            content (str, matplotlib figure, or ndarray): image content
            class_ (str): custom class to apply
            title (str): image title field
            width (int or str): image width (default units are pixels)
            height (int or str): image height (default units are pixels)
            animation (bool): whether content is an animation
            duration (float): Total animation time in seconds.  Default is 3
            format (str or None): override Pillow save format
        """
        self.content = content
        self.class_ = class_
        self.title = title
        self.width = width
        self.height = height
        self.animation = animation
        self.duration = duration
        self.rescale = rescale
        self.format = format

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
            format = self.format or 'png'
            self.content.savefig(buff, format=format)
            src = 'data:image/{};base64,{}'.format(
                format,
                base64.b64encode(buff.getvalue()).decode()
            )

        # if given numpy array
        elif type(self.content).__name__ == 'ndarray':
            buff = BytesIO()
            styles.append("image-rendering:crisp-edges")
            if self.animation:
                format = self.format or 'gif'
                buff = gif(self.content, duration=self.duration, rescale=self.rescale, format=format)
                src = 'data:image/{};base64,{}'.format(
                    format,
                    base64.b64encode(buff.getvalue()).decode()
                )
            else:
                format = self.format or 'png'
                imageio.imsave(buff, self.content.astype('uint8'), format=format)
                src = 'data:image/{};base64,{}'.format(
                    format,
                    base64.b64encode(buff.getvalue()).decode()
                )

        elif self.content is None:
            src = ''

        else:
            raise TypeError(f"Unsupported object {type(self.content)}")

        style = ";".join(styles)
        return f'<img class="{self.class_}" style="{style}" src="{src}"/>'

def rescale_max(x, rescale):
    """Rescale a stack of images by the global max or max in each image

    Args:
        x (torch.Tensor or numpy.ndarray): input data of shape (num_images, width, height)
            or (num_images, width, height, 3) for RGB images
        rescale (str): if 'frame', rescale max of each image to 255.  If 'sequence',
            rescale max of whole image sequence to 255. (default 'frame')
    """
    import numpy as np
    axes = tuple(range(len(x.shape)))

    x[x < np.finfo(float).eps] = 0

    # handle intensity scaling
    if rescale == 'frame':
        # scale each frame separately
        # x *= np.expand_dims(255 / np.max(x, axes[1:]), axes[1:])
        maxx = np.max(x, axes[1:])
        x *= np.expand_dims(np.divide(255, maxx, where=(maxx != 0)), axes[1:])
    elif rescale == 'sequence':
        # x *= 255 / np.max(x)
        maxx = np.max(x)
        x *= np.divide(255, maxx, where=(maxx != 0))

    return x

def gif(x, duration=3, rescale='frame', format='gif'):
    """Save image sequence as gif

    Args:
        savefile (str): path to save location
        x (torch.Tensor or numpy.ndarray): input data of shape (num_images, width, height)
            or (num_images, width, height, 3) for RGB images
        duration (float): Total animation time in seconds.  Default is 3
        rescale (str): if 'frame', rescale max of each image to 255.  If 'sequence',
            rescale max of whole image sequence to 255. (default 'frame')
    """
    # frame duration in ms
    frame_duration = lambda frames: duration / len(frames)

    # minimum allowable gif frame duration is 20ms
    if frame_duration(x) < 20e-3:
        x = x[::math.ceil(20e-3 / frame_duration(x))]

    from PIL import Image

    x = rescale_max(x, rescale)

    # if grayscale input, convert to RGB
    if len(x.shape) == 3:
        imgs = [Image.fromarray(img.astype('uint8'), mode='L') for img in x]
    elif len(x.shape) == 4:
        imgs = [Image.fromarray(img.astype('uint8'), mode='RGB') for img in x]
    else:
        raise ValueError('Invalid size for x')

    buff = BytesIO()
    # duration is the number of milliseconds between frames
    imgs[0].save(
        buff, save_all=True, append_images=imgs[1:],
        duration=int(1000 * frame_duration(x)), loop=0,
        quality=100, format=format
    )
    return buff
