from setuptools import setup, find_packages
from os import path

setup(name="billboard-song-converter",
      version="0.0.1",
      description="Combine chart entries in to songs",
      author="Joyfulflyer",
      packages=find_packages(),
      python_requires='<=3.6, <4',
      install_requires=['Flask', 'Flask-SQLAlchemy', 'PyMySQL', 'SQLAlchemy'])
