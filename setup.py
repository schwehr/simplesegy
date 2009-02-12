#!/usr/bin/env python

from setuptools import setup, find_packages
import sys, os

version=file('VERSION').readline().strip()

setup(name='simplesegy',
      version=version,
      description="Seimic data SEG-Y reader",
      long_description="""\
Stripped down SEGY reader.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='science geophysics',
      author='Kurt Schwehr',
      author_email='kurt@ccom.unh.edu',
      url='http://vislab-ccom.unh.edu/~schwehr/software/simplesegy/',
      license='PSF',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Cheetah>=2.0',
      ],
      entry_points = '''
      [console_scripts]
      segy-metadata = simplesegy.cmds.metadata:main
      segy-info = simplesegy.cmds.info:main
      segy-slice = simplesegy.cmds.slice:main
      ''',
      package_data = {
        'docs': ['*'],
        '': ['README','LICENSE','Makefile'],
        },
      )

