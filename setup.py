#!/usr/bin/env python

import os
import sys, os

from setuptools import setup, find_packages

version=file('VERSION').readline().strip()


setup(name='simplesegy',
      version=version,
      description="Seimic data SEG-Y reader",
      long_description="""Stripped down SEGY reader.""",
      classifiers=[
           'License :: OSI Approved :: Apache Software License',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='science geophysics',
      author='Kurt Schwehr',
      author_email='schwehr@gmail.com',
      url='https://github.com/schwehr/simplesegy',
      license='Apache 2.0',
      packages=find_packages(), # exclude=['examples', 'tests']),
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
      segy-validate = simplesegy.cmds.validate:main
      ''',
      package_data = {
        'docs': ['*'],
        '': ['README','LICENSE','Makefile'],
        },
      )

