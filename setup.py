#!/usr/bin/env python

from setuptools import setup

setup(name='dataset_lib',
      packages=['dataset_lib',
                'dataset_lib.config',
                'dataset_lib.datasets',
                'dataset_lib.utils',
                ],
      version='0.1.0',
      install_requires=[
            'numpy',
            'pyYAML',
            'planner@git+https://github.com/anenriquez/mrta_planner.git@master#egg=planner',
      ],
      description='Datasets for MRTA',
      author='Angela Enriquez Gomez',
      author_email='angela.enriquez@smail.inf.h-brs.de',
      package_dir={'': '.'}
      )
