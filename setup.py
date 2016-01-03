from setuptools import setup

import skog

with open('README.rst') as f:
    desc = f.read()

setup(
    name = "skog",
    version = skog.__version__,
    packages = ['skog'],
    author = "Brendan Molloy",
    author_email = "brendan+pypi@bbqsrc.net",
    description = "Generate visual trees for FreeBSD ports",
    license = "BSD-2-Clause",
    keywords = ["freebsd", "ports", "trees", "visualisation"],
    url = "https://github.com/bbqsrc/skog-python",
    long_description=desc,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ],
    entry_points = {
        'console_scripts': [
            'skog = skog.__main__:main'
        ]
    }
)
