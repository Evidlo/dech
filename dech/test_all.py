#!/usr/bin/env python3

from dech import *

def test_img():
    h = Img('/tmp/test.png').html()
    assert h == '<img src="/tmp/test.png"/>'
