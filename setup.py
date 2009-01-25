from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='simplesegy',
      version=version,
      description="Seimic data reader",
      long_description="""\
Stripped down SEGY reader.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='science geophysics',
      author='Kurt Schwehr',
      author_email='kurt@ccom.unh.edu',
      url='http://vislab-ccom.unh.edu/~schwehr/software/simplesegy',
      license='Python',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
