#!/usr/bin/env python

__author__ = 'Aleksandar Savkov'

from setuptools import setup

setup(name='qsutils',
      version='1.0',
      description='SGE qstat interface',
      author='Aleksandar Savkov',
      author_email='aleksandar@savkov.eu',
      url='https://www.github.com/asavkov/qsutils/',
      package_dir={'': 'src'},
      entry_points={
          'console_scripts': [
              'qsutils=qsutils:main',
          ],
      }
      )
