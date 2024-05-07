#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
setup.py
A module that installs sweeper as a module
"""

import glob
from os.path import basename, splitext
from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="ugrc-sweeper",
    version="2.0.0",
    license="MIT",
    description="CLI tool for making good data",
    long_description=(Path(__file__).parent / "readme.md").read_text(),
    long_description_content_type="text/markdown",
    author="UGRC",
    author_email="ugrc-developers@utah.gov",
    url="https://github.com/agrc/sweeper",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(i))[0] for i in glob.glob("src/*.py")],
    python_requires=">=3",
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
    keywords=[],
    install_requires=[
        "agrc-supervisor==3.*",
        "agrc-usaddress==0.*",
        "beautifulsoup4==4.*",
        "docopt==0.*",
        "html5lib==1.*",
        "xxhash==3.*",
    ],
    dependency_links=[],
    extras_require={
        "tests": [
            "pytest-cov==5.*",
            "pytest-instafail==0.5.*",
            "pytest-mock==3.*",
            "pytest-watch==4.*",
            "pytest==8.*",
            "ruff==0.*",
        ],
    },
    setup_requires=[
        "pytest-runner",
    ],
    entry_points={"console_scripts": ["sweeper = sweeper.__main__:main"]},
)
