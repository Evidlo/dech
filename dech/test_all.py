#!/usr/bin/env python3

from dech import *
import numpy as np
import matplotlib.pyplot as plt

def test_img():
    # test path string input
    h = Img('/tmp/test.png').html()
    assert 'src="/tmp/test.png"' in h

    # test numpy array input
    # grayscale
    Img(np.random.random((10, 10)), width='1em').html()
    # color
    Img(np.random.random((10, 10, 3))).html()
    # animated grayscale
    Img(np.random.random((10, 10, 10)), animation=True).html()
    # animated color
    Img(np.random.random((10, 10, 10, 3)), animation=True).html()
    Img(np.random.random((10, 10, 10, 3)), rescale=True, animation=True).html()
    Img(np.random.random((10, 10, 10, 3)), duration=100, animation=True).html()

    # test matplotlib figure input
    plt.figure('test')
    plt.plot(np.random.random(10))
    Img(plt.figure('test')).html()

def test_html():
    svg_data = """
    <svg width="400" height="180">
    <rect x="50" y="20" rx="20" ry="20" width="150" height="150"
    style="fill:red;stroke:black;stroke-width:5;opacity:0.5" />
    </svg>"""

    s = HTML(svg_data)


def test_paragraph():
    text = """
    some text here
    foobar
    """
    p = Paragraph(text)


def test_code():
    text = """
    some text here
    foobar
    """
    c = Code(text)

def test_page(tmp_path):
    Page([]).save(tmp_path / "test.html")
    Page([Img('/tmp/test.png')]).save(tmp_path / "test.html")
