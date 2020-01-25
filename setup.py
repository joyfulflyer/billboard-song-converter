from setuptools import setup, find_packages
from os import path

setup(name="billboard-grabber",
      version="0.2.2",
      description="Get the billboard data and put it in the database",
      author="Joyfulflyer",
      packages=find_packages(),
      python_requires='<=3.6, <4',
      install_requires=[
          'billboard.py', 'Flask', 'Flask-SQLAlchemy', 'PyMySQL', 'SQLAlchemy'
      ])
