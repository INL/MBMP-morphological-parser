## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

"""
Implementation of various Memory-based Classifiers, such as
Memory-based Morphological Analysis and Memory-based Lemmatization.
"""

from mbmp.classifiers.api import MBClassifier
from mbmp.classifiers.util import align, to_input
from mbmp.config import *
from mbmp.parse import MbmaCKYParser
from mbmp.parse.util import make_grammar
from mbmp.datatypes import Morpheme


class MBMA(MBClassifier):
    """
    Memory-Based Morphological Analyzer. MBMA is a Memory-Based Classifier
    that attempts to analyze words into their component parts. The classifier
    splits the word into its containing morphemes and assigns a Part of
    Speech tag to them. On the basis of the Part of Speech tags, MBMA uses a
    special kind of :class:`mbmp.parse.CKYParser`
    (:class:`mbmp.parse.MbmaCKYParser`) to construct hierarchical
    morphological analyses.
    """
    def __init__(self, host=HOST, port=PORT, settings=MBMA_CONFIG,
                 parser=MbmaCKYParser):
        MBClassifier.__init__(self, host, port, settings)
        if parser is not None:
            self.parser = parser()

    def classify(self, word):
        """
        For each letter of WORD, classify its corresponding part-of-speech
        tag.

            >>> classifier.classify('schoenlepel')
            [Morpheme(token='schoen', lemma='schoen', pos='N'),
             Morpheme(token='lepel', lemma='lepel', pos='N')]

        Args:
            - word (str): a string representing a word.
        Returns:
            A list of (tag, leaf) pairs.
        """
        parse = []
        classes = self._classify(word)
        if classes[0] == '0':
            classes[0] = 'UNK'
        for i, inst in enumerate(classes):
            # split outcomes without POS or lemmatization operation
            # from those who have
            if inst == '0':
                parse[-1].token += word[i]
                parse[-1].lemma += word[i]
            # lemmatization operation up ahead
            elif ':' in inst:
                # first collect the part-of-speech tag
                if '@' in inst:
                    inst, pos = inst.split('@')
                    parse.append(Morpheme(pos=pos))
                parse[-1].token += word[i]
                parse[-1].lemma += word[i]
                # apply the lemmatization operation
                for tag in inst.split('+'):
                    if tag.startswith('INS'):
                        # outcomes can contain diacritics, decode them
                        parse[-1].lemma += tag[tag.find(':')+1:].decode('utf-8')
                    elif tag.startswith('DEL'):
                        parse[-1].lemma = parse[-1].lemma[:-1]   
            else:
                parse.append(Morpheme(pos=inst, token=word[i], lemma=word[i]))
        return parse

    def pprint_parse(self, parse):
        """
        Return a pretty print of the classification.

        Each (Tag, Leaf) pair is
        printed as (Tag Leaf), i.e. the output for a word such as
        'aandeelhoudersvergadering' could be::

            >>> classifier.pprint_parse(p)
            (ADP aan) (NOU deel) (VRB houd) (SUF er)
            (LE s)
            (VRB vergader) (SUF ing)

        Args:
            - parse: the return value of :func:`mbmp.MBMA.classify` for a given word.
        Returns:
            A string representation of parse.
        """
        return ' '.join('(%s %s)' % (m.pos, m.lemma) for m in parse)

    def trees(self, parse, nbest=1, post_process=False, filter=None, mrepr='tokens'):
        """
        Return a genartor of pretty printed Tree structures of the
        classification.
        
        The output for a word such as `aandeelhoudersvergadering` is::
        
            >>> trees = classifier.trees(results)
            >>> for tree in trees:
            ...    print tree
            (NOU
               (NOU (NOU (ADP aan) (NOU deel)) (VRB houd) (SUF er))
               (LE s)
               (NOU (VRB vergader) (SUF ing)))

        Args:
            - parse: the return value of :func:`mbmp.MBMA.classify` for a given word.
            - nbest (int): specify how many parses should be returned
            - post_process (bool): perform some cleaning operation after parsing
            - filter (function): a function used to filter certain trees
            (function must return True or False)
            - mrepr (str): specify how the leaves should be represented in the
            Tree: options are: token forms ('tokens'), lemma forms
            ('lemmas') and tokens and lemmas ('tokens-and-lemmas')
        Yields:
            the nbest parses
        
        """
        self.parser.set_grammar(make_grammar(parse, mrepr))
        return self.parser.nbest_parse(
            [m.pprint(mrepr) for m in parse], nbest, post_process, filter)


class MBMS(MBClassifier):
    """
    Memory-Based Morphological Segmentizer. MBMS is a Memory-Based Classifier
    that attempts to analyze words into their component parts. The classifier
    splits words into their containing segments. No Part of Speech is
    assigned to the segments.
    """
    def __init__(self, host=HOST, port=PORT, settings=MBMS_CONFIG, **kwargs):
        MBClassifier.__init__(self, host, port, settings)

    def classify(self, word):
        """
        For each letter of WORD, classify whether it is the start of a
        segment or not. Returns a list of letters of WORD in which letters
        starting a new segment are preceded by the separation tag.
        """
        classes = self._classify(word)
        parse = []
        for i, inst in enumerate(classes):
            # '0' outcomes means that no segment is predicted.
            if inst != '0':
                parse.append(inst)
            parse.append(word[i])
        return parse

    def pprint_parse(self, parse):
        """
        Return a pretty print of the classified segmentations.
        The segmentation tag is used as the separator of the segments, i.e.
        if the segment tag '+' is used, the output for a word such as
        `verlanglijstje` is::
        
            >>> parse = classifier.classify('verlanglijstje')
            >>> print classifier.pprint_parse(parse)
            ver+lang+lijst+je

        Args:
            - parse: the return value of :func:`mbmp.MBMA.classify` for a
                given word.
        Returns:
            A string representation of parse.
        """
        return ''.join(parse)

    def segmentize(self, word):
        return self.pprint_parse(self.classify(word))


class MBMC(MBClassifier):
    """
    Memory-Based Morphological Chunker. MBMC is a Memory-Based Classifier
    that attempts to analyze words into their component parts. The classifier
    tries to return hierarchical morphological parses on the basis of
    identified chunks.
    """
    def __init__(self, host=HOST, port=PORT, settings=MBMC_CONFIG, **kwargs):
        MBClassifier.__init__(self, host, port, settings)

    def classify(self, word):
        """
        For each letter of WORD, classify its corresponding chunk tag.
        Returns a list of lists of leaf,part-of-speech,chunk-tag combinations.

        Args:
            - word (str): a string representing a word.
        Returns:
            A list of (tag, leaf) pairs.
        """
        parse = []
        for i, inst in enumerate(self._classify(word)):
            if inst != '0':
                parse.append((inst, []))
            parse[-1][1].append(word[i])
        return [[''.join(w)]+t.split('/') for t, w in parse]

    def pprint_parse(self, chunks):
        """
        Return a pretty print of the classified chunks.
        A word such as ondankbaar is printed as::

            on/PRE/O dank/VRB/B-VRB baar/SUF/I-VRB

        Args:
            - chunks: the return value of :func:`mbmp.MBMC.classify` for
                a given word
        Returns:
            A string representation of parse separated by '/'
        """
        return ' '.join('/'.join(c) for c in chunks)

    def trees(self, chunks, top_node='W'):
        """
        Return all valid chunks as NLTK trees, i.e. a chunk parse such as::
        
            ver/PRE/B-VRB beter/ADJ/I-VRB baar/SUF/O
            
        is transformed into::
        
            (VRB (PRE ver) (ADJ beter)) (SUF baar)
            
        This method requires NLTK to be installed (see http://www.nltk.org).

        Args:
            - chunks: the return value of :func:`MBMC.classify` for a given word
            - top_node (str): the label of the top node.
        Returns:
            A hierarchical :class:`Tree`
        """
        try:
            from nltk import Tree
        except ImportError:
            print 'Please install NLTK (www.nltk.org)'
            raise

        stack = [Tree(top_node, [])]
        for word, pos, chunk in chunks:
            if chunk.startswith('O'):
                state = 'O'
            else:
                state, chunk = chunk.split('-')
            mismatch_I = state == 'I' and chunk != stack[-1].node
            if state in 'BO' or mismatch_I:
                if len(stack) == 2: stack.pop()
            if state == 'B':
                chunk = Tree(chunk, [])
                stack[-1].append(chunk)
                stack.append(chunk)
            stack[-1].append(Tree(pos, [word]))
        return stack[0]


class MBLEM(MBClassifier):
    """
    Memory-Based Lemmatizer. MBLEM is a Memory-Based Classifier
    that attempts to lemmatize word forms. On the basis of a training file
    with transformation rules to convert a wordform to a lemma, the
    classifier tries to predect on a character basis the correct
    transformation.
    """
    def __init__(self, host=HOST, port=MBLEM_PORT, settings=MBLEM_CONFIG, **kwargs):
        MBClassifier.__init__(self, host, port, settings)

    def classify(self, word):
        """
        For each letter of WORD, predict whether it can stay (same as in
        LEMMA), must be deleted (not in LEMMA) or whether a character from
        LEMMA must be inserted (not in WORD).

        Args:
            - word (str): a string representing a word.
        Returns:
            a list of characters representing the predicted lemma.
        """
        parse = []
        for i, inst in enumerate(self._classify(word)):
            # default add character to parse
            parse.append(word[i]) 
            # if predicted character is not the same as source
            if inst != '0': 
                for tag in inst.split('+'):
                    if tag.startswith('INS'):
                        # outcomes can contain diacritics, decode them
                        parse.append(tag[tag.find(':')+1:].decode('utf-8')) 
                    elif tag.startswith('DEL'):
                        parse = parse[:-1]
        return parse

    def lemmatize(self, word):
        """
        Lemmatize a word::

            >>> lemmatizer = MBLEM()
            >>> lemmatizer.lemmatize('zochten')
            zoeken

        Args: 
            - word (str): a string representing a word.
        Returns:
            the lemmatized form of the input word.
        """
        return self.pprint_parse(self.classify(word))
        
    def pprint_parse(self, results):
        return ''.join(results)


class MBPT(MBClassifier):
    """
    Memory-Based Part-of-speech Tagger. MBPT is a Memory-Based Classifier
    that attempts to predict the part-of-speech category of words.
    """
    def __init__(self, host=HOST, port=PORT, settings=MBPT_CONFIG, **kwargs):
        MBClassifier.__init__(self, host, port, settings)

    def _classify(self, word):
        return self.client.query(align(word, max_len=53))

    def classify(self, word):
        """
        Predict the part-of-speech category of a word::

            >>> tagger = MBPT()
            >>> tagger.classify('stier')
            NOU

        Args:
            - word (str): a string representing a word.
        Returns:
            the part-of-speech category of a word.
        """
        return self._classify(word)

    def pprint(self, word, sep='\t'):
        """
        Return a pretty print of the word and its part-of-speech category::

            >>> tagger = MBPT()
            >>> tagger.pprint('stier')
            stier   NOU

        Args:
            - word (str): a string representing a word.
            - sep (str): the separator used to separate the word from the
            - part-of-speech category.
        Returns:
            the word and its part-of-speech category as a string.
        """
        return '%s%s%s' % (word, sep, self.classify(word))

