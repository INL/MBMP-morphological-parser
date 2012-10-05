## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

"""
Configuration for mbmp. All options can be changed here or they
can be overwritten in an interactive session or in your own
scripts.
"""

import os


# the path where the module resides
MODULE = os.path.dirname(os.path.abspath(__file__))

# the path pointing relative to MODULE where data resides
DATA = os.path.join(MODULE, 'data')

# the server address
HOST = 'localhost'

# the port used for the timblserver
PORT = 50202
MBLEM_PORT = 50204

# Default string encoding used
ENCODING = 'utf-8'

# the path pointing to the PCFG used by the probabilistic parser
PCFG = os.path.join(DATA, 'celex_pcfg.pickle')

#////////////////////////////////////////////////////////////////////////////
# Configuration for the different classifiers
#////////////////////////////////////////////////////////////////////////////

MBMA_CONFIG = dict(
    # the number of connections allowed by the TimblServer
    C = '10',
    # weighting meassure
    w = '1', # default Gain Ratio (See timbl for options)
    # The algorithm used
    a = '0', # default IB1 (original MBMA uses IGTree -a1)
    # the number of k's used in the classification
    k = '1',
    # We use inverse distance weighting
    #d = 'ID',
    # instancebase used by MBMA
    i = os.path.join(DATA, 'celex-morphology-lemmatization.instancebase'))

MBMC_CONFIG = dict(
    # the number of connections allowed by the TimblServer
    C = '10',
    # weighting meassure
    w = '1', # default Gain Ratio (See timbl for options)
    # The algorithm used
    a = '0', # default IB1
    # the number of k's used in the classification
    k = '1',
    # instancebase used by MBMC
    i = os.path.join(DATA, 'chunks.instancebase'))

MBMS_CONFIG = dict(
    # the number of connections allowed by the TimblServer
    C = '10',
    # weighting meassure
    w = '2', # default Gain Ratio (See timbl for options)
    # The algorithm used
    a = '0', # default IB1
    # the number of k's used in the classification
    k = '1',
    # instancebase used by MBMS
    i = os.path.join(DATA, 'celex-segmentation.instancebase'))
    
MBLEM_CONFIG = dict(
    # the number of connections allowed by the TimblServer
    C = '10',
    # weighting meassure
    w = '1', # default Gain Ratio (See timbl for options)
    # The algorithm used
    a = '0', # default IB1
    # the number of k's used in the classification
    k = '1',
    # instancebase used by MBMS
    i = os.path.join(DATA, 'mblem.instancebase'))

MBPT_CONFIG = dict(
    # the number of connections allowed by the TimblServer
    C = '10',
    # weighting meassure
    w = '1', # default Gain Ratio (See timbl for options)
    # The algorithm used
    a = '0', # default IB1
    # the number of k's used in the classification
    k = '1',
    # instancebase used by MBMS
    i = os.path.join(DATA, 'wnt-pos-tagging.instancebase'))

    
__all__ = ['MBMA_CONFIG', 'MBMC_CONFIG', 'MBMS_CONFIG', 'MBLEM_CONFIG',
           'MBPT_CONFIG', 'PCFG', 'HOST', 'PORT', 'MBLEM_PORT']
