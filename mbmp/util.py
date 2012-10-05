## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

import re
import collections

try:
    from lxml.etree import Element, tostring
except ImportError:
    print ImportError('xml-functions cannot be used, please install lxml')

from nltk import Tree

# A dictionary with CELEX pos-tags as keys and those of GiGaNT as values
POS_TABLE = {
    'N': 'NOU',
    'A': 'ADJ',
    'Q': 'NUM',
    'V': 'VRB',
    'D': 'DET',
    'O': 'PRO',
    'B': 'ADV',
    'P': 'ADP',
    'Y': 'CON',
    'I': 'INT',
    'Z': 'EXP',
    'E': 'NOU',
    'X': 'UNK',
    'G': 'BRM',
    'C': 'CON',
    'PN': 'NOU'}

# A dictionary with inflection tags in CELEX with
# the conversion to GiGaNT pos-tags
INFLECTION_TABLE = {
    'X': 'X',              # none
    'e': 'N',              # singular
    'm': 'N',              # plural
    'C': 'A',              # comparative
    'i': 'V',              # infinitive
    'p': 'V',              # participle
    't': 'V',              # present tense
    'v': 'V',              # past tense
    'S': 'A',              # superlative
    'd': 'N',              # diminutive
    'E': 'A',              # suffix-e 
    '2': 'V',              # 2nd person
    '3': 'V',              # third person
    'G': 'N',              # genetive
    'D': 'N',              # dative
    'P': 'A',              # positive
    'a': 'V'}              # subjunctive



      
LEAF_REGEX = re.compile('(\w+)\=(\w+)')

def tree_to_xml(tree):
    """
    Convert a NLTK Tree object into xml tree using lxml.
    """
    if tree.height() == 2:
        xml_str = Element('morpheme', pos=tree.node)
        leaf = LEAF_REGEX.search(tree[0])
        if leaf is not None:
            token, lemma = leaf.group(1, 2)
        else:
            token = lemma = tree[0]
        xml_str.set('lemma', lemma)
        xml_str.text = token
    else:
        xml_str = Element('segment', pos=tree.node)
        for child in tree:
            xml_str.append(tree_to_xml(child))
    return xml_str

def xml(treelist, ids=False, encoding='utf-8', xml_decl=True, pp=True):
    """
    Convert a list of Trees into an xml structure.
    """
    if isinstance(treelist, Tree):
        treelist = [treelist]
    elif not isinstance(treelist, collections.Iterable):
        raise ValueError('Input must be a iterator of trees.')
    if not ids:
        treelist = enumerate(treelist)
    root = Element('lexicon')
    # input must be a list of id,tree pairs
    for id, tree in treelist:
        word = Element('word', id=str(id))
        word.append(tree_to_xml(tree))
        root.append(word)
    return tostring(root, pretty_print=pp, encoding=encoding,
                    xml_declaration=xml_decl)

