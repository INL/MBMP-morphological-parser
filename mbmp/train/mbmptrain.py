## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

import argparse
import codecs
import os
import subprocess
import sys
import textwrap
import csv

from nltk import Tree

from mbmp.train.util import unicode_csv_reader
from mbmp.train.transform import rewrite_string, edit_distance


def timbl_instancebase(filepath):
    """
    Create a timbl instancebase from a trainingfile. Default output is 
    original file plus instancebase as extension.

    Args:
        - filepath (str): the path to the trainingfile
    """
    out = open(os.devnull, 'w')
    timbl = subprocess.Popen(
        ['timbl', '-f', filepath, '-I', filepath+'.instancebase'],
        stderr = out, stdout=out)
    return True

def make_instances(item, tags, right=5, left=5, sep=','):
    """
    Convert a item into a windowed representation as described in
    Van den Bosch and Daelemans (1999):

    Args:
        - item (str): a string representing a word
        - tags (list): a list of tags per character of ITEM
        - right (int): context on the right side of a focus letter.
        - left (int): context on the left side of a focus letter.
        - sep (str): the separator used to separate variables in the window.
    Yields:
        a window per character of item

    """
    for i in xrange(len(item)):
        inst = []
        for j in xrange(i, i + 1 + right + left):
            if j < left or j >= len(item) + left:
                inst.append('_')
            else:
                # if the item contains elements that are the same
                # as 'sep', choose another symbol ('C')
                if item[j-left] == sep:
                    inst.append('C')
                else:
                    inst.append(item[j-left])
        inst.append(tags[i])
        yield sep.join(inst)

def format_testitem(item, size=5, sep=','):
    """
    Create a window with empty outcome slots ('?') for a test item::

        >>> for window in format_testitem('aardigheidje'):
        ...     print window
        _,_,_,_,_,a,a,r,d,i,g,?
        _,_,_,_,a,a,r,d,i,g,h,?
        _,_,_,a,a,r,d,i,g,h,e,?
        _,_,a,a,r,d,i,g,h,e,i,?
        _,a,a,r,d,i,g,h,e,i,d,?
        a,a,r,d,i,g,h,e,i,d,j,?
        a,r,d,i,g,h,e,i,d,j,e,?
        r,d,i,g,h,e,i,d,j,e,_,?
        d,i,g,h,e,i,d,j,e,_,_,?
        i,g,h,e,i,d,j,e,_,_,_,?
        g,h,e,i,d,j,e,_,_,_,_,?
        h,e,i,d,j,e,_,_,_,_,_,?

    Args:
        - item (str): a string representing a word
        - sep (str): the separator used to separate variables in the window.
    Yields:
        a complete window for word in which all outcomes are marked as '?'
    """
    return make_instances(item, '?'*len(item), left=size, right=size, sep=sep)

def make_tagged_instances(inst, fn, size=5, sep='+', tagsep='@', windowsep=','):
    """
    Create a window for a word with the given tags::

        >>> for window in make_tagged_instances('gezellig@A+heid@N|A*', get_tags):
        ...     print window
        _,_,_,_,_,g,e,z,e,l,l,A
        _,_,_,_,g,e,z,e,l,l,i,0
        _,_,_,g,e,z,e,l,l,i,g,0
        _,_,g,e,z,e,l,l,i,g,h,0
        _,g,e,z,e,l,l,i,g,h,e,0
        g,e,z,e,l,l,i,g,h,e,i,0
        e,z,e,l,l,i,g,h,e,i,d,0
        z,e,l,l,i,g,h,e,i,d,_,0
        e,l,l,i,g,h,e,i,d,_,_,N|A*
        l,l,i,g,h,e,i,d,_,_,_,0
        l,i,g,h,e,i,d,_,_,_,_,0
        i,g,h,e,i,d,_,_,_,_,_,0

    Args:
        - inst (str): a string with morphemes separated by SEP holding tags
            separated by TAGSEP.
        - fn (function): the function used to extract the tags or segments.
            Use :func:`get_segments` to create an instance with segmentation
            marks. Use :func:`get_tags` to create an instance with Part of
            Speech marks.
        - size (int): the window size
        - sep (str): the separator used to separate the items of inst
        - tagsep (str): the separator used to separate tags from
        - windowsep (str): the separator used to separate variables in the window.
    Yields:
        a complete window for word in which all outcomes are marked as '?'
    """
    word, tags = fn(inst, sep=sep, tagsep=tagsep)
    if len(word) != len(tags):
        raise ValueError("Window has a different size than tags...")
    tags = [tag.replace('.', '*') for tag in tags]
    return make_instances(word, tags, right=size, left=size, sep=windowsep)

def _extract_tags(iterator, default):
    """
    Helper function to extract classes from an annotated instance.
    """
    segments, word = [], []
    for leaf, tag in iterator:
        segments.append(tag)
        word.append(leaf[0])
        for elt in leaf[1:]:
            segments.append(default)
            word.append(elt)
    return ''.join(word), segments
    
def get_segments(inst, sep='+', tagsep=None, default='0'):
    """
    Return the original word and the tags per character. An instance
    such as ``huis+deur`` is converted into::
    
        ('huisdeur', ['0','0','0','0','+','0','0','0'])
    """
    word, segments = _extract_tags(
        ((segment, sep) for segment in inst.split(sep)), default)
    return word, ['0'] + segments[1:]

def get_tags(inst, sep='+', tagsep='@', default='0'):
    """
    Return the original word and the tags per character. An instance
    such as ``huis@N+deur@NWB`` is converted into::
    
        ('huisdeur', ['N','0','0','0','NWB','0','0','0'])
    """
    return _extract_tags((m.split(tagsep) for m in inst.split(sep)), default)

def get_rewrite_tags(inst, sep=None, tagsep=None, default='0'):
    """
    Return the original word and the rewite tags to transform the
    word into the corresponding lemma per character of word. An instance
    such as ``k,l,o,p,p+DEL:p,e,n`` is converted into::
    
        ('kloppen', ['0','0','0','0','DEL:p','0','0'])
    """
    word, tags = [], []
    for elt in inst.split(','):
        if len(elt.split('+')) > 1:
            tags.append('+'.join(elt.split('+')[1:]))
        elif tagsep in elt:
            tags.append(elt[2:])
        else:
            tags.append(default)
        word.append(elt[0])
    return word, tags

def get_tags_and_rewrite_tags(source, target, sep='+', tagsep='@', default='0', 
                              nltk_tree=False):
    """
    Return the original word and the rewite tags + POS tags per character.
    An instance such as ``huiz@N+en@INFL huis@N+en@INFL`` is converted into::
    
        ('huizen', ['N','0','0','DEL:z+INS:s','INFL','0','0'])
    """
    analysis = []
    if nltk_tree:
        source = mbma_repr(Tree(source))
        target = mbma_repr(Tree(target))
    sa = [m.split(tagsep) for m in source.split(sep)]
    ta = [m.split(tagsep) for m in target.split(sep)]
    if len(sa) != len(ta):
        print 'Unequal number of morphemes in %s and %s' % (source, target)
        raise ValueError('Unequal number of morphemes in %s and %s' % (source, target))
    for (sm, st), (tm, tt) in zip(sa, ta):
        instance = lemma_formatter(sm, tm, string=False)
        instance[0] += '@%s' % st
        analysis.append(','.join(instance))
    return ','.join(analysis)

def lemma_formatter(source, target, string=True):
    rewrite = rewrite_string(edit_distance(source, target).backtrace())
    if string:
        return ','.join(rewrite)
    return rewrite

def mbma_repr(tree, sep='+', split='@'):
    """
    Transform a tree structure into a flat representation used by MBMA::

        >>> tree = nltk.Tree('(N (V (PRE ver) (A grijs)) (SUF ing))')
        >>> print mbma_repr(tree)
        'ver@V|*A+grijs@A+ing@N|V*WB'
    """
    def _mbma_tree(tree, sep, split):
        if tree.height() < 3: return tree
        subtrees = list(tree)
        newtrees = []
        for subtree in subtrees:
            if isinstance(subtree[0], Tree):
                newtrees.extend(_mbma_tree(subtree, sep, split))
            elif subtree.node in ('PRE', 'LE', 'SUF'):
                node = '%s|' % tree.node
                for t in subtrees:
                    if t.node in ('PRE', 'LE', 'SUF'):
                        if t.node == subtree.node:
                            node += '*'
                        else:
                            node += 'x'
                    else:
                        node += t.node
                newtrees.append(Tree(node, [subtree[0]]))
            else:
                newtrees.append(subtree)
        return Tree(tree.node, newtrees)
    
    if not isinstance(tree, Tree):
        raise ValueError('%r is not of type Tree' % tree)
    tree = _mbma_tree(tree, sep, split)
    return '%sWB' % sep.join(split.join(m) for m in tree.pos())

def delimiter_type(delimiter):
    if delimiter == '\\t':
        delimiter = '\t'
    elif delimiter == '\\n':
        delimiter = '\n'
    return delimiter

def main():
    parser = argparse.ArgumentParser(
        prog = 'mbmptrain',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = textwrap.dedent("""\
        Training utilities for MBMA.
        Script to convert morphological analyses into a format appropriate
        for a letter-by-letter classification task.

        The script supports three kinds of instancebases:
           1. segmentation
           2. POS-tagging of morphemes
           3. lemmatization
           4. POS-tagging of morphemes + lemmatization
        For each task the inputfile must consist of one item per line
        and follow the follwing rules:
           1. segmentation: each morpheme of a word must be separated by a
                 separator, e.g. '+'. Example: huisdeur -> huis+deur
           2. POS-tagging: each morpheme of a word must be separated by a
                 separator, e.g. '+' and to each morpheme a POS-tag is
                 attached by another separator, e.g. '@'.
                 Example: huisdeur -> huis@N+deur@N
           3. lemmatization: inputfile must consist of word form and lemma
                 pairs separated by a comma.
                 Example: mocht,mag
           4. POS-tagging + lemmatization: inputfile must be of the same type
                 as lemmatization, and each word (word form and lemma) must
                 be in the format descripbed under 2 (POS-tagging). (Note
                 that both word form and lemma must contain an equal number
                 of morphemes."""))
    parser.add_argument(
        '-i', dest = 'inputfile', type = str,
        required = True, help = 'the path pointing to the input file')
    parser.add_argument(
        '-o', dest = 'output', type = argparse.FileType('w'),
        required = False, default = sys.stdout,
        help = 'the path pointing to the output file')
    parser.add_argument(
        '-t', dest = 'filetype', type = str,
        choices = ['pos', 'seg', 'lem', 'pos_lem'], required = True,
        help = 'Make windows on the basis of pos, lemma or segmentation tags')
    parser.add_argument(
        '-w', dest = 'windowsize', type = int, default = 5, required = False,
        help = '''Specify the size of the left and right context
                  from the focus letter.''')
    parser.add_argument(
        '--morphsep', dest = 'morphsep', type = str, default = '+',
        required = False, help = 'The separator used to separate morphemes')
    parser.add_argument(
        '--tagsep', dest = 'tagsep', type = str, default = '@',
        required = False,
        help = 'The separator used to separate tags from morphemes')
    parser.add_argument(
        '--lemmasep', dest = 'lemmasep', type = delimiter_type, default = False,
        required = False,
        help = '''The separator used to separate word form and lemma pairs.
        Normally, this option does not need to be set because Python tries to
        detect the correct delimiter.''')
    parser.add_argument(
        '--nltk_trees', dest = 'trees', action = 'store_true', default = False,
        help = 'Input trees are in NLTK tree format')
    parser.add_argument(
        '--encoding', dest = 'encoding', type = str,  default = 'utf-8',
        required = False, help = 'Default encoding of input')
    parser.add_argument(
        '--instancebase', dest = 'timbl', action='store_true',
        default = False, help = 'Make a timbl instancebase from the input file')
    
    args = parser.parse_args()

    args.inputfile = codecs.open(args.inputfile, encoding=args.encoding)
    # setup an appropriate formatter function and a file check function    
    if args.filetype in ('pos', 'seg'):
        if args.filetype == 'pos':
            fn = get_tags
        elif args.filetype == 'seg':
            fn = get_segments
        if args.trees:
            assert args.filetype != 'seg'
            check_fn = lambda l: Tree(l.strip())
            formatter = lambda l: mbma_repr(Tree(l.strip()))
        else:
            check_fn = lambda l: len(l.split('\t')) == 1 or len(l.split()) == 1
            formatter = lambda l: l.strip()
    elif args.filetype in ('lem', 'pos_lem'):
        fn = get_rewrite_tags
        if not args.lemmasep:
            args.lemmasep = csv.Sniffer().sniff(args.inputfile.read(1024))
            args.inputfile.seek(0)
            args.inputfile = unicode_csv_reader(args.inputfile, args.lemmasep)
        else:
            args.inputfile = unicode_csv_reader(args.inputfile, delimiter=args.lemmasep)
        check_fn = lambda l: len(l) == 2
        if args.filetype == 'lem':
            formatter = lambda l: lemma_formatter(*l)
        else:
            formatter = lambda l: get_tags_and_rewrite_tags(*l, nltk_tree=args.trees)
            
    # process the input line by line
    for line in args.inputfile:
        sys.stderr.write('%r\n' % line)
        if not check_fn(line):
            raise ValueError('Wrong input line: %s' % line)
            # change back to normal one item per line!!
        for window in make_tagged_instances(formatter(line), fn, args.windowsize,
                                            tagsep=args.tagsep, sep=args.morphsep):
            args.output.write(u'{}\n'.format(window).encode('utf-8'))
    args.output.close()

    # if the option --instancebase was set, try to compile an instancebase
    # with timbl. (This of course requires TiMBL to be installed and on
    # your path.)
    if args.timbl:
        sys.stderr.write('Creating instancebase...\n')
        timbl_instancebase(args.output.name)

if __name__ == '__main__':
    main()
