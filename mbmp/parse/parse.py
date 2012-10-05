## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

from nltk.tree import Tree
from nltk.grammar import Nonterminal, ContextFreeGrammar
from nltk.parse.chart import AbstractChartRule, ChartParser, BU_STRATEGY
from nltk.parse.chart import LeafEdge, TreeEdge
from nltk.parse.pchart import ProbabilisticTreeEdge

from mbmp.parse.util import post_process_tree


def is_lexical(item):
    """
    Test whether an item contains lexical information.
    Items are considered lexical when they have the format TAG:leaf.

    Args:
        - item (:class:`nltk.TreeEdge`): a (Probabilistic) tree edge

    Returns:
        Boolean -- is this treeedge lexical or not.
    """
    if not isinstance(item, (TreeEdge, ProbabilisticTreeEdge)):
        return False
    if ':' in item.lhs().symbol():
        return True
    if item.lhs().symbol() == 'x':
        return True
    return False


class RightHandRule(AbstractChartRule):
    """
    A rule that joins two adjacent edges together into a single combined edge.
    In particular, this rule states that any pair of edges that are not
    lexical (see :func:`is_lexical`) can be joined resulting in a new edge
    in which the left-hand-side is taken from the right edge and the right-
    hand-side is the adjunction of the left-hand-side of the left and right
    edge.
    """
    NUM_EDGES = 1

    def apply_iter(self, chart, grammar, right_edge):
        if (right_edge.is_incomplete() or       # use only completed edges
            isinstance(right_edge, LeafEdge) or # skip terminal leaves
            is_lexical(right_edge) or           # skip lexical productions
            right_edge.lhs().symbol() == 'G'):  # skip BRM rules
            return
        # We only merge if both the right end left edge are completed. The
        # left edge must be adjacent to the right edge in the chart.
        for left_edge in chart.select(end=right_edge.start(), is_complete=True):
            if isinstance(left_edge, LeafEdge) or is_lexical(left_edge):
                continue
            new_edge = TreeEdge(span=(left_edge.start(), right_edge.end()),
                                lhs=right_edge.lhs(),
                                rhs=[left_edge.lhs(), right_edge.lhs()],
                                dot=2) # edge is completed at initialization
            if chart.insert(new_edge, (left_edge, right_edge)):
                yield new_edge


# we use the standard Bottom-Up Parse strategy and add the Right-Hand-Rule to it
BU_RHR_STRATEGY = BU_STRATEGY + [RightHandRule()]


class MbmaParser(ChartParser):
    """
    A ChartParser using a bottom-up parsing strategy plus the Right Hand Rule.
    See :func:`RightHandRule` for more information.
    """

    def __init__(self, **parser_args):
        """
        Constructor. Initializes a MbmaParser.

        Args:
            - parser_args: needs a keyword grammar which is of
                type :class:`ContextFreeGrammar`
        """
        ChartParser.__init__(self, [], BU_RHR_STRATEGY, **parser_args)

    def set_grammar(self, grammar):
        """
        Asign a new grammar to the parser

        Args:
            - parser_args: needs grammar of type :class:`ContextFreeGrammar`
        """
        self._grammar = ContextFreeGrammar(Nonterminal('S'), grammar)

    def nbest_parse(self, word, n=None, post_process=False, filter=None):
        """
        Return the nbest parses for the given word.

        Args:
            - word (str or list): a list or string of morphemes
            - n (int): how many parses should be returned

        Returns:
            A list of trees
        """
        if isinstance(word, basestring):
            word = word.split()
        chart = self.chart_parse(word)
        trees = [tree for edge in chart.select(start=0, end=len(word))
                 for tree in chart.trees(edge, complete=True)
                 if isinstance(tree, Tree)][:n]
        if post_process:
            for tree in trees:
                post_process_tree(tree)
        return trees


def demo():
    """
    A demo showing some basic functionality.
    """
    from mbmp.parse.util import make_grammar
    from mbmp.datatypes import Morpheme
    parse = [Morpheme(pos='V|*V', token='ver', lemma='ver'),
             Morpheme(pos='V', token='eis', lemma='eis'),
             Morpheme(pos='V|VINFL', token='t', lemma='t')]
    print 'Parse produced by MBMA:'
    print parse
    print
    print 'Compiling grammar rules from parse...'
    productions = make_grammar(parse)
    for prod in productions:
        print prod
    print
    print 'Parsing word "ver eis t"'
    parser = MbmaParser(productions)
    for tree in parser.nbest_parse('ver eis t'.split()):
        print tree

__all__ = ['MbmaParser', 'BU_RHR_STRATEGY', 'RightHandRule', 'demo']

if __name__ == '__main__':
    demo()
