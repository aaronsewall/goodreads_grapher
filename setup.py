import os

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="goodreads_grapher",
    version="0.0.1",
    description="Rating Graphs for your GoodReads Authors and Series",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aaronsewall/goodreads_grapher",
    author="Aaron Sewall",
    author_email="aaronsewall@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    install_requires=[
        "betterreads==0.4.2",
        "matplotlib==3.2.0",
        "pandas==1.0.1",
        "requests-cache==0.5.2",
    ],
    entry_points={
        "console_scripts": ["goodreads_grapher = goodreads_grapher.grapher:main"]
    },
)
