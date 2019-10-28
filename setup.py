#!/usr/bin/env python

from setuptools import setup

setup(name='dataset_lib',
      packages=['dataset_lib', 'dataset_lib.utils',
                'dataset_lib.datasets.non_overlapping_tw.generic_task.random',
                'dataset_lib.datasets.overlapping_tw.generic_task.random'],
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
