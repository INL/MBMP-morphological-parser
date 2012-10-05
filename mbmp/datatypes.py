## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT


class Morpheme(object):
    """
    A data class representing a morpheme. Each morpheme specifies
    a token form, a lemma form and its part-of-speech tag.
    """
    def __init__(self, token='', pos=None, lemma=''):
        """
        Constructor.

        Args:
            - token (str): the token representation of a morpheme
            - pos (str): the part-of-speech category of a morpheme
            - lemma (str): the lemma representation of a morpheme

        If lemma is not given (e.g. because it is equal to token), lemma
        if automatically set to token::
        
            >>> m = Morpheme('clapp', 'V', 'clap')
            Morpheme(token='clapp', lemma='clap', pos='V')
        
            >>> m Morpheme('clapp', 'V')
            Morpheme(token='clapp', lemma='clapp', pos='V')
        """
        self.token = token
        self.pos = pos
        self.lemma = lemma
        # if lemma is not specified, default to token
        if not self.lemma:
            self.lemma = self.token

    def __repr__(self):
        return 'Morpheme(token=%s, lemma=%s, pos=%s)' % (
            self.token, self.lemma, self.pos)

    def __str__(self):
        return self.pprint()

    def __eq__(self, other):
        if not isinstance(other, Morpheme):
            return False
        return (self.token == other.token and
                self.lemma == other.lemma and
                self.pos == other.pos)

    def __ne__(self, other):
        return not (self == other)

    def pprint(self, mrepr='tokens-and-lemmas'):
        """
        Return a string representation of the morpheme.
        
        Args:
            - mrepr: Choose a morpheme representation:
                - tokens = token representation
                - lemmas = lemma representation
                - tokens-and-lemmas = token and lemma representation
                    separated by a '=' character (zett=zet)
                    
        Example usage::
            >>> m = Morpheme('clapp', 'V', 'clap')
            >>> m.pprint(mrepr='tokens')
            clapp
            >>> m.pprint(mrepr='lemmas')
            clap
            >>> m.pprint(mrepr='tokens-and-lemmas')
            clapp=clap
        """
        if mrepr == 'tokens-and-lemmas':
            if self.lemma != self.token:
                leaf = '='.join([self.token, self.lemma])
            else:
                leaf = self.token
        elif mrepr == 'lemmas':
            leaf = self.lemma
        else:
            leaf = self.token
        return leaf
