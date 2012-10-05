## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

"""
Memory-Based Morphological Parsing

This package consists of an implementation and extensions of Memory-Based
Morphological Analysis (MBMA) as described by Van den Bosch & Daelemans
(1999). MBMA is extended with a specialized CKY Parser that returns all
possible derivations for a given analysis of MBMA. In addition to an
implementation of 'standard' MBMA, this package contains a class to perform
morphological segmentation (MBMS), i.e. the segmentation of words into
morphemes. Furthermore, the package provides a Memory-Based Morphological
Chunker (MBMC), which is used to analyze words into hierarchical
structures in an alternative way. Lastly, the package can be used to
lemmatize word forms (MBLEM) and to assign part-of-speech tags to lemmas
(MBPT).

All classes (MBMA, MBMS, MBMC, MBLEM, MBPT) extend the
abstract MBClassifier interface. The Memory-Based Classifier sets up an
instance of TimblServer and connects to this server via a client (see
TimblClient).
"""

#----------------------------------------------------------------------------
# METADATA
#----------------------------------------------------------------------------

__author__ = 'Folgert Karsdorp, INL'
__licence__ = 'see LICENCE.TXT'
__version__ = '0.4'
__maintainer__ = 'INL'
__maintainer_email__ = 'servicedesk@inl.nl'
__copyright__ = 'Copyright (C) 2011 INL'


#----------------------------------------------------------------------------
# TOP-LEVEL MODULES
#----------------------------------------------------------------------------

# Import top-level functionality into top-level namespace

from mbmp.datatypes import Morpheme
from mbmp.config import *
from mbmp.util import xml
from mbmp.mbmp_exceptions import ConnectionError, ServerConnectionError
from mbmp.client import TimblClient

#----------------------------------------------------------------------------
# PACKAGES
#----------------------------------------------------------------------------

# Processing packages -- these define __all__ carefully.

import mbmp.classifiers
import mbmp.server
import mbmp.parse
import mbmp.train

from mbmp.classifiers import *
from mbmp.server import *
from mbmp.parse import *
from mbmp.train import *



