## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

import cPickle

from collections import defaultdict
from itertools import product

from nltk.grammar import induce_pcfg
from nltk.tree import Tree, ProbabilisticTree

from mbmp.config import PCFG


def prod_to_chomsky_normal_form(production):
    """
    Transform a production into Chomsky Normal Form.

    Args:
        - production (:class:`nltk.Production`): a grammar rule

    Returns:
        a list of CNF'ified productions
    """
    if len(production.rhs()) > 2:
        node = [production.lhs().symbol(), []]
        cur_node = node
        num_children = len(production.rhs())
        children = [c for c in production.rhs()]
        child_nodes = [c.symbol() for c in production.rhs()]
        for i in range(1, num_children - 1):
            new_head = '%s|<%s>' % (
                production.lhs(), '-'.join(child_nodes[i:num_children]))
            new_node = Tree(new_head, [])
            cur_node[1:] = [children.pop(0), new_node]
            cur_node = new_node
        cur_node[1:] = [child for child in children]
        return Tree(node[0], node[1:]).productions()
    else:
        return [production]

def _initialize(grammar):
    """
    Declare a initialization function depending on the type of grammar
    given as input (a regular PCFG or the grammar from MBMA).

    Args:
        - grammar: a probabilistic grammar

    Returns:
        an initialization function
    """
    def initialize(tokens):
        table = ParserTable(tokens)
        for end in xrange(1, table.num_leaves()+1):
            table[end-1][end] = [
                ProbabilisticTree(p.lhs().symbol(), p.rhs(), prob=p.prob())
                for p in grammar.productions(rhs=tokens[end-1])]
        return table
    return initialize

def linking(prod):
    """
    Return true if the Left Hand Side of Production contains a CNF rewrite.

    Args:
        - prod (:class:`nltk.Production`): a production rule

    Returns:
        boolean
    """
    return '|' in  prod.lhs().symbol()


class ParserTable(object):
    """
    The matrix used by :class:mbmp.parse.CKYParser`.
    """
    def __init__(self, tokens):
        self._tokens = tuple(tokens)
        self._num_leaves = len(self._tokens)
        self._table = [[[] for i in xrange(self._num_leaves+1)]
                           for j in xrange(self._num_leaves)]

    def __getitem__(self, index):
        return self._table.__getitem__(index)
    
    def __setitem__(self, index, value):
        self._table.__setitem__(index, value)
                       
    def leaves(self):
        """
        Returns: the leaves in the table.
        """
        return self._tokens
        
    def num_leaves(self):
        """
        Returns: the number of leaves in the table.
        """
        return self._num_leaves

    def top_node(self, start, end):
        """
        Returns: True if where at the root node of the tree
        """
        return start == 0 and end == self._num_leaves
        
    def parses(self):
        """
        Returns: all full parses in the table (located at position [0,num_leaves]).
        """
        return self[0][self._num_leaves]
        
    def __repr__(self):
        return '<ParserTable: %s>' % (self._table,)


class CKYParser(object):
    """
    A CKY Parser for deriving trees that represent possible structures for a
    sequence of morphemes.
    """

    def __init__(self, grammar=None, beam_size=1000):
        """
        Initializes a CKYParser.

        Args:
            - grammar (:class:`nltk.WeightedGrammar`): the PCFG used by the parser
            - beam_size (int): the strictness for pruning
        """
        if grammar is None:
            grammar = cPickle.load(open(PCFG))
        self._grammar = grammar
        self.beam_size = beam_size
        self.top_probs = {}
        self._productions = self._build_productions(grammar)
        self.initialize = _initialize(self._grammar)

    def _build_productions(self, grammar):
        """
        Index the Right Hand Rules of the productions in grammar. Raise an
        error if a production is not in Chomsky Normal Form.

        Args:
            - grammar (:class:`nltk.WeightedGrammar`): the grammar to be extracted

        Returns:
            dict -- a dictionary with the rhs of productions as keys and the
                    complete productons as values.
        """
        productions = defaultdict(set)
        for production in grammar.productions():
            rhs = production.rhs()
            if len(rhs) == 2:
                productions[rhs[0].symbol(), rhs[1].symbol()].add(production)
            else:
                if production.lhs().symbol() == 'W':
                    self.top_probs[rhs[0].symbol()] = production.prob()
                # all productions except the top nodes should be in CNF,
                # hence no unary productions are allowed.
                elif not isinstance(rhs[0], basestring):
                    print ValueError('Production %s not in CNF' % production)
        return productions

    def parse(self, tokens):
        """
        Derive of possible trees from the input.
        
        Args:
            - tokens: a list of morphemes

        Returns:
            list -- all complete parses that could be derived.
        """
        # initialize the table
        table = self.initialize(tokens)
        # run the CKY algorithm
        self._parse(table)
        # return all complete parses
        return table.parses()

    def _parse(self, table):
        """
        Helper function of :func:`CKYParser.parse` that implements the actual
        parsing algorithm.

        Args:
            - table :class:`ParserTable`: a probabilistic CKY matrix

        Returns:
            list -- all complete parses that could be derived.
        """
        for end in xrange(1, table.num_leaves()+1):
            for start in xrange(end-2, -1, -1):
                top_node = table.top_node(start, end)
                trees = []
                self.best_prob = 0.0
                for split in xrange(start+1, end):
                    for l, r in product(table[start][split], table[split][end]):
                        for prod in self.find_productions(l, r):
                            # do not add a tree to trees if the top node is
                            # an indexed node or if it is a rewritten
                            # production.
                            if top_node and linking(prod):
                                continue
                            prob = prod.prob()*l.prob()*r.prob()
                            lhs = prod.lhs().symbol()
                            if self.acceptable(lhs, prob, trees):
                                trees.append(
                                    ProbabilisticTree(lhs, [l, r], prob=prob))
                table[start][end] = trees

    def acceptable(self, lhs, prob, trees):
        """
        Return True if there are no trees yet or when the probability
        of the potentional tree is higher than the trees already found.

        Args:
            - lhs: the top node of the new tree
            - prob (float): the probability of the new tree
            - trees: a list of trees

        Returns:
            boolean
        """
        return not trees or self._prune(prob, trees)

    def find_productions(self, left, right):
        """
        Find productions that have left and right as the RHS.

        Args:
            - left: the left Nonterminal
            - right: the right Nonterminal

        Returns:
            list -- all grammar rules that have left and right as the RHS.
        """
        return self._productions.get((left.node, right.node), [])

    def _prune(self, prob, best_prob):
        """
        Return True if the probability of the new tree falls within the
        accepted range of best probabilities.
        """
        if prob > (self.best_prob / self.beam_size):
            self.best_prob = prob
            return True
        return False

    def assign_top_probabilitiy(self, tree):
        tree.set_prob(tree.prob() * self.top_probs.get(tree.node, 0.000001))
        return tree

    def nbest_parse(self, tokens, n=5, post_process=False, filter=None):
        """
        Return the nbest parses for the given word. Parses with the same
        probability will count for one n step.

        Args:
            - tokens (list): the list of morphemes to be parsed.
            - n (int): how many parses to be returned.

        Returns:
            list -- the nbest parses
        """
        if filter is None:
            parses = self.parse(tokens)
        else:
            parses = (p for p in self.parse(tokens) if filter(p))
        parses = (self.assign_top_probabilitiy(p) for p in parses)
        parses = sorted(parses, key=lambda t: t.prob(), reverse=True)
        best = parses and parses[0].prob() / n
        for parse in parses:
            if not (parse.prob() < best):
                parse.un_chomsky_normal_form()
                yield parse


class MbmaCKYParser(CKYParser):
    """
    This parser implements a :class:`CKYParser` that uses the grammar rules from
    :class:`mbmp.MBMA` and -- if needed -- a Probabilistic Context Free Grammar
    to parse a word.
    """
    def __init__(self, grammar = None, beam_size = 1000):
        CKYParser.__init__(self, grammar, beam_size)

    def set_grammar(self, productions):
        """
        Add the grammar rules from MBMA to the parser. Transforms all rules
        to Chomsky Normal Form, induces a Weighted Context Free Grammar on
        the basis of these rules and indexes the Right Hand Rules of the
        productions.

        Args:
            - productions (list): a list of :class:`nltk.Production` instances
        """
        cnf_prods = []
        for p in productions:
            # transform each production of MBMA into CNF
            cnf_prods.extend(prod_to_chomsky_normal_form(p))
        self._local_grammar = induce_pcfg('S', cnf_prods)
        self._local_productions = self._build_productions(self._local_grammar)
        self.initialize = _initialize(self._local_grammar)

    def find_productions(self, left, right):
        """
        Find productions that have left and right as the RHS. First try to
        find productions in the valency rules returned by MBMA. If that
        fails, try to find the productions in the PCFG.

        Args:
            - left: the left Nonterminal
            - right: the right Nonterminal

        Returns:
            list -- all grammar rules that have left and right as the RHS.
        """
        prods = self._local_productions.get((left.node, right.node), [])
        if not prods:
            prods = self._productions.get((left.node, right.node), [])
        return prods


# class DOParser(CKYParser):
#     def __init__(self, grammar = None, beam_size = 1000):
#         CKYParser.__init__(self, grammar, beam_size)

#     def acceptable(self, lhs, prob, trees):
#         """
#         Return True if there are no trees yet or when the probability
#         of the potentional tree is higher than the trees already found or
#         when the lhs is an indexed node.
#         """
#         return CKYParser.acceptable(self, lhs, prob, trees) or '@' in lhs

#     def linking(self, prod):
#         """
#         Return true if the Left Hand Side of Production contains a CNF rewrite.
#         """
#         lhs = prod.lhs().symbol()
#         return '|' in lhs or ('@' in lhs and self._grammar.productions(rhs=prod.lhs()))


def demo():
    """
    A demo showing some basic functionality.
    """
    from mbmp.parse.util import make_grammar
    from mbmp.datatypes import Morpheme
    parse = [Morpheme(pos='V|*V', token='ver', lemma='ver'),
             Morpheme(pos='V', token='koop', lemma='koop'),
             Morpheme(pos='A|V*', token='baar', lemma='baar')]
    print 'Parse produced by MBMA:'
    print ['(%s %s)' % (m.pos, m) for m in parse]
    print
    grammar = cPickle.load(open(PCFG))
    print 'Parsing word "ver koop baar" with default CKY Parser'
    parser = CKYParser(grammar)
    for tree in parser.nbest_parse('ver koop baar'.split()):
        print tree
    print
    print 'Parsing word "ver koop baar" with Mbma CKY Parser'
    print 'Compiling grammar rules from parse...'
    g = make_grammar(parse)
    for prod in g:
        print prod
    print
    parser = MbmaCKYParser(grammar)
    parser.set_grammar(g)
    for tree in parser.nbest_parse('ver koop baar'.split(), n=5):
        print tree


__all__ = ['CKYParser', 'MbmaCKYParser']

if __name__ == '__main__':
    demo()
