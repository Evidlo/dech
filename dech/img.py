#!/usr/bin/env python3

from dataclasses import dataclass
from .element import Element
from io import BytesIO
import imageio
import base64

class Img(Element):
    """Generate <img> tag for PNGs or GIFs"""

    def __init__(self, content, title=None, width=None, height=None, animation=False,
                 rescale='frame', duration=100):
        """Initialize Img element

        Args:
            content (str, matplotlib figure, or ndarray): image content
            title (str): image title field
            width (int or str): image width (default units are pixels)
            height (int or str): image height (default units are pixels)
            animation (bool): whether content is an animation
            rescale (str): if 'frame', rescale max of each image in animation to 255.
                If 'sequence', rescale max of whole image sequence to 255. (default 'frame')
            duration (int): delay in ms between frames
        """
        self.content = content
        self.title = title
        self.width = width
        self.height = height
        self.animation = animation
        self.rescale = rescale
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
            styles.append("image-rendering:crisp-edges")
            if self.animation:
                buff = gif(self.content, rescale=self.rescale, duration=self.duration)
                src = 'data:image/gif;base64,{}'.format(
                    base64.b64encode(buff.getvalue()).decode()
                )
            else:
                imageio.imsave(buff, (255 * self.content).astype('uint8'), format='png')
                src = 'data:image/png;base64,{}'.format(
                    base64.b64encode(buff.getvalue()).decode()
                )

        style = ";".join(styles)
        return f'<img style="{style}" src="{src}"/>'


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


def gif(x, rescale='frame', duration=100):
    """Save image sequence as gif

    Args:
        savefile (str): path to save location
        x (torch.Tensor or numpy.ndarray): input data of shape (num_images, width, height)
            or (num_images, width, height, 3) for RGB images
        rescale (str): if 'frame', rescale max of each image to 255.  If 'sequence',
            rescale max of whole image sequence to 255. (default 'frame')
        duration (int): delay in ms between frames
    """

    from PIL import Image

    x = rescale_max(x, rescale)

    # if grayscale input, convert to RGB
    if len(x.shape) == 3:
        imgs = [Image.fromarray(img.astype('uint8'), mode='L') for img in x]
    elif len(x.shape) == 4:
        imgs = [Image.fromarray(img.astype('uint8'), mode='RGB') for img in x]
    else:
        raise ValueError('Invalid size for x')

    # duration is the number of milliseconds between frames
    buff = BytesIO()
    imgs[0].save(buff, format='gif', save_all=True, append_images=imgs[1:], duration=duration, loop=0)
    return buff
