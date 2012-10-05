## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

from setuptools import setup

setup(name = 'mbmp',
      version = '0.4',
      description = 'Memory-Based Morphological Parsing',
      author = 'Folgert Karsdorp, INL',
      author_email = 'servicedesk@inl.nl',
      packages = ['mbmp', 'mbmp.classifiers', 'mbmp.parse',
                  'mbmp.server', 'mbmp.train'],
      scripts = ['mbmp/scripts/mbmptrain', 'mbmp/scripts/mbmp'],
      package_data = {'mbmp': [
          'data/celex-chunked.instancebase',
          'data/celex-segmentation.instancebase',
          'data/celex-morphology-lemmatization.instancebase',
          'data/mblem.instancebase',
          'data/wnt-pos-tagging.instancebase',
          'data/chunks.instancebase',
          'data/celex_pcfg.pickle']},
      platforms = 'Mac OS X, GNU Linux',
      install_requires = ['lxml', 'psutil'])
