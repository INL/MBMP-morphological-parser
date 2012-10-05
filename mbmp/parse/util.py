## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

import re

from nltk.grammar import Nonterminal, Production


def post_process_tree(tree, lexical_tags=True):
    remove_lexical_tags(tree)

def remove_lexical_tags(tree):
    """
    Remove the lexical tags from lexical trees in TREE
    (i.e. PRE:ver becomes PRE).

    Args:
        - tree: a hierarchical Tree object
    """
    for subtree in tree.subtrees():
        if ':' in subtree.node:
            subtree.node = re.sub(':.*', '', subtree.node)

def nonterminals(items):
    """
    Return a list of Nonterminals from a list of strings.

    Args:
        - items (ist): a list of Nonterminals
    """
    return [Nonterminal(item) for item in items]

def make_grammar(parse, mrepr='tokens-and-lemmas'):
    """
    Return a list of Productions on the basis of an output parse of L{MBMA}.
    MBMA returns parses in the following format::
    
        [('V|*V', 'ver'), ('V', 'eis'), ('INFLtWB', 't')]
        
    This is transformed into the following list of productions::
    
        [PRE:ver -> 'ver', V -> PRE:ver V, V -> 'eis', INFL:t -> 't', V -> V INFL:t]

    Args:
        - parse (list): a parse return by :func:`mbmp.MBMA.classify`

    Returns:
        list -- a list of Productions.
    """
    prods = []
    for morph in parse:
        pos, lemma = morph.pos, morph.lemma
        if pos.endswith('WB'):
            pos = pos[:-2]
        leaf = morph.pprint(mrepr)
        # tags with '|' split all non-lexical lemmas from lexical ones
        if '|' in pos:
            superpos, pos = pos.split('|')
            if pos.startswith('INFL'):
                nonterminalpos = 'INFL:%s' % lemma
                nonterms = [Nonterminal(nonterminalpos), Nonterminal(pos[-1])]
            elif pos.endswith('INFL'):
                nonterminalpos = 'INFL:%s' % lemma
                nonterms = [Nonterminal(pos[0]), Nonterminal(nonterminalpos)]
            elif pos.startswith('*'): # it's a prefix
                nonterminalpos = 'PRE:%s' % lemma
                nonterms = nonterminals([nonterminalpos]+list(pos[1:]))
            elif pos.endswith(('*', '*WB')): # it's a suffix
                pos = pos[:pos.find('*')]
                nonterminalpos = 'SUF:%s' % lemma
                nonterms = nonterminals((list(pos)+[nonterminalpos]))
            else: # it's a linking element
                nonterminalpos = 'LE:%s' % lemma
                leidx = pos.find('*')
                nonterms = nonterminals(
                    list(pos[:leidx])+[nonterminalpos]+list(pos[leidx+1:]))
            if 'x' in pos:
                prods.append(Production(Nonterminal('x'), [leaf]))
            prods.append(Production(Nonterminal(nonterminalpos), [leaf]))
            if nonterms:
                prods.append(Production(Nonterminal(superpos), nonterms))
        else:
            prods.append(Production(Nonterminal(pos), [leaf]))
    return prods
