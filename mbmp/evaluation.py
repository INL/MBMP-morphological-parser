# Evaluate morphological segmentation and detection of morphemes

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

import argparse

from nltk import Tree

def words_to_indexes(tree):
    """
    Return a new tree based on the original tree, such that the leaf values
    are replaced by their indexs.
    """
    out = tree.copy(deep=True)
    leaves = out.leaves()
    for index in range(0, len(leaves)):
        path = out.leaf_treeposition(index)
        out[path] = index + 1
    return out

def list_brackets(tree, ignore_labels=True):
    def label(tr):
        if ignore_labels:
            return 'ignore'
        return tr.node
    out = []
    i_tree = words_to_indexes(tree)
    for subtree in i_tree.subtrees(filter=lambda t: t.height() > 1):
        right_pos = len(''.join(tree.leaves()[:subtree.leaves()[0]-1]))
        left_pos = len(''.join(tree.leaves()[:subtree.leaves()[-1]]))-1
        out.append((right_pos, left_pos, label(subtree)))
    return out
    # return [(firstleaf(sub), lastleaf(sub), label(sub)) for sub in
    #         i_tree.subtrees(filter = lambda t: t.height() > 1)]

def list_segments(parse, ignore_labels=True):
    def label(leaf):
        if ignore_labels:
            return 'ignore'
        return leaf
    pos = 0
    segments = []
    for segment in parse.leaves():
        segments.append((pos+1, pos+len(segment), label(segment)))
        pos += len(segment)
    return segments

def list_lemmas(parse, ignore_labels=False):
    return parse.leaves()

class ParseEval(object):
    def __init__(self, gold, parses, eval_fn = list_brackets):
        if len(gold) != len(parses):
            raise ValueError('Number of parses is unequal')
        self.gold = gold
        self.parses = parses
        self.eval_fn = eval_fn

    def _scores(self, reference, compared, ignore_labels):
        total = 0.0
        successes = 0.0
        for a,b in zip(reference, compared):
            a_brackets = self.eval_fn(a, ignore_labels)
            b_brackets = self.eval_fn(b, ignore_labels)
            for bracket in a_brackets:
                if bracket in b_brackets:
                    successes += 1
            total += len(b_brackets)
        return successes / total

    def precision(self, ignore_labels=True):
        return self._scores(self.gold, self.parses, ignore_labels)

    def recall(self, ignore_labels=True):
        return self._scores(self.parses, self.gold, ignore_labels)

    def f_score(self, precision, recall):
        return 2 * ((precision * recall) / (precision + recall))

    def print_scores(self, ignore_labels=True):
        precision = self.precision(ignore_labels=ignore_labels)
        recall = self.recall(ignore_labels=ignore_labels)
        f_score = self.f_score(precision, recall)
        print 'Evaluating', self.eval_fn.__name__.split('_')[1], 
        print '(labels was', 'unset)' if ignore_labels else 'set)'
        print '-'*40
        print 'Precision:', precision
        print '   Recall:', recall
        print '  F-score:', f_score
        print '-'*40
        print


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = """
        Evaluate the quality of segmentation. Calculates the precision
        recall and F-score for the segmentation of words into morphemes.

        Input file must be a tab-separated file with the gold standard
        segmentations as the left column and the suggested segmentations
        as the right column.""")
    parser.add_argument(
        '-i', dest='input', type=str, required=True,
        help = 'the path pointing to the file holding the segmentations.')
    parser.add_argument(
        '-t', dest = 'evaluation_type', required = False,
        default = 'brackets', choices = ['brackets', 'segments', 'lemmas'],
        help = 'type of evaluation (one of "brackets" or "segments")')
    args = parser.parse_args()
    if args.evaluation_type == 'brackets':
        evaluation_type = list_brackets
    elif args.evaluation_type == 'lemmas':
        evaluation_type = list_lemmas
    else:
        evaluation_type = list_segments
    gold_parses = []
    parses = []
    for line in open(args.input):
        gold,parse = map(Tree, line.strip().split('\t'))
        if (args.evaluation_type == 'brackets' and
            len(gold.leaves()) != len(parse.leaves())):
            print 'Skipping analyses: unequal morphemes %s -- %s' % (gold, parse)
            continue
        elif ''.join(gold.leaves()) != ''.join(parse.leaves()):
            print 'Skipping analyses: unequal input %s -- %s' % (gold, parse)
            continue
        gold_parses.append(gold)
        parses.append(parse)
    scores = ParseEval(gold_parses, parses).scores()
    precision, recall, f_score, l_precision, l_recall, l_f_score = scores
    print 'precision: %f' % precision
    print 'recall: %f' % recall
    print 'F-score: %f' % f_score
    print
    print 'labeled precision: %f' % l_precision
    print 'labeled recall: %f' % l_recall
    print 'labeled F-score: %f' % l_f_score

