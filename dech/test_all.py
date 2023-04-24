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


def test_page(tmp_path):
    Page([]).save(tmp_path / "test.html")
    Page([Img('/tmp/test.png')]).save(tmp_path / "test.html")
