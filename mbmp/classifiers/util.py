## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

from collections import Iterable

def align(word, max_len=20):
    """
    Convert the input word into the format matching the instancebase

    Args:
        word (str): a string representing a word.
        max_len (int): the maximum length of variables

    Returns:
        An examplar (str) to be classified
    """
    if not isinstance(word, basestring):
        return ValueError('Word %s is nto of type basestring' % word)
    return ','.join(list('%s%s?' % ('='*(max_len-len(word)), word)))

def to_input(parse):
    """
    Transform a parse from MBMA into the input format that can be used
    by :mod:`mbmp.train.mbmptrain`.
    """
    if not isinstance(parse, Iterable):
        raise ValueError('Parse %s is not of type Iterable' % parse)
    if not isinstance(parse[0], Morpheme):
        raise ValueError('Elements of parse %s not of type Morpheme' % parse)
    return '+'.join('%s@%s' % (m.token, m.pos) for m in parse)
