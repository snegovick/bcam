import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "bcam",
    version = "0.3.1-0-gc2d3548",
    author = "Konstantin Kirik (snegovick)",
    author_email = "snegovick@gmail.com",
    description = ("Basic computer-aided manufacturing program."),
    license = "GNU GPL",
    keywords = "CAM, hobby, CNC",
    url = "http://hobbycam.org",
    packages=['bcam'],
    scripts=['bcam-launcher'],
    long_description=read('README.md'),
    dependency_links = ['https://bitbucket.org/snegovick/dxfgrabber/downloads/dxfgrabber-0.7.4.tar.gz#egg=dxfgrabber-0.7.4'],
    install_requires = ['dxfgrabber'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ],
)

