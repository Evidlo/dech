#!/usr/bin/env python3

from setuptools import find_packages, setup

with open("README.md") as f:
    README = f.read()

version = {}
# manually read version from file
with open("dech/version.py") as file:
    exec(file.read(), version)

setup(
    # some basic project information
    name="dech",
    version=version["__version__"],
    license="GPL3",
    description="Declaratively generate simple HTML pages in Python",
    long_description=README,
    long_description_content_type='text/markdown',
    author="Evan Widloski",
    author_email="evan_github@widloski.com",
    url="https://github.com/evidlo/dech",
    # your project's pip dependencies
    install_requires=[
        # consider specifying version as well
    ],
    include_package_data=True,
    # automatically look for subfolders with __init__.py
    packages=find_packages(),
    # if you want your code to be able to run directly from command line
    # entry_points={
    #     'console_scripts': [
    #         'myscript = dech.dech:main',
    #     ]
    # },
)
