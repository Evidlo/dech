# DECH

DECH is a library for DEClaratively generating HTML pages in Python.  This may be useful for generating summary report pages containing images/tables from scientific scripts.

## Install

    pip install dech
    
## Example Usage

``` python
from dech import *
import matplotlib.pyplot as plt
import numpy as np

img1 = np.random.random((100, 100))

plt.figure('plot1')
plt.plot(np.random.random(10))
plt.figure('plot2')
plt.plot(np.random.random(10))

Page(
    [
        [
            Figure('Example 1', Img('/tmp/example.gif')),
            Figure('Example 2', Img('/tmp/example.gif')),
            Figure('Example 3', Img('/tmp/example.gif')),
        ],
        [
            Figure('Matplotlib 1', Img(plt.figure('plot1'), width=300)),
            Figure('Matplotlib 2', Img(plt.figure('plot2'), width=300)),
        ],
        [
            Figure('Numpy Array', Img(img1, width=300)),
        ],
]).save('/tmp/display.html')
```

![](example.png)

