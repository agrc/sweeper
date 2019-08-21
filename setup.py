import glob
import io
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup


def read(*names, **kwargs):
    return io.open(join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")).read()


setup(
    name="sweeper",
    version="1.0.0",
    license="MIT",
    description="CLI tool for making good data",
    long_description="",
    author="AGRC",
    author_email="agrc@utah.gov",
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
        'docopt==0.6.*',
    ],
    dependency_links=[],
    extras_require={
        'tests': [
        ]
    },
    entry_points={"console_scripts": ["sweeper = sweeper.sweeper:__main__"]}
)