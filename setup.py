#!/usr/bin/env python

from setuptools import setup

setup(name='mrta_datasets',
      version='0.1.0',
      install_requires=[
            'numpy',
            'pyYAML',
      ],
      description='Datasets and structs for MRTA',
      author='Angela Enriquez Gomez',
      author_email='angela.enriquez@smail.inf.h-brs.de',
      package_dir={'': '.'}
      )
