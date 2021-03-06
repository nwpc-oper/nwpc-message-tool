# coding: utf-8
from setuptools import setup, find_packages
import codecs
from os import path
import io
import re

with io.open("nwpc_message_tool/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nwpc-message-tool',

    version=version,

    description='Tool for nwpc-message-client.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/nwpc-oper/nwpc-message-tool',

    author='perillaroc',
    author_email='perillaroc@gmail.com',

    license='GPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],

    keywords='nwpc message tool',

    packages=find_packages(exclude=["docs", "tests", "example"]),

    install_requires=[
        "pyyaml",
        "loguru",
        "click",
        "pandas",
        "scipy",
        "tqdm",
        "elasticsearch",
        "pandas",
        "numpy",
        "bokeh",
        "colorcet",
    ],

    extras_require={
        'test': ['pytest'],
        'cov': ['pytest-cov', 'codecov']
    },

    entry_points={
        "console_scripts": [
        ],
    }
)
