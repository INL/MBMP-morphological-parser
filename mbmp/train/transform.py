## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

from itertools import product


class Cell(object):
    """
    A class representing a cell in the L{DistanceMatrix}
    """
    def __init__(self, cost=0, parent=[0, 0], action=None, character=None):
        self._cost = cost
        self.parent = parent
        self.action = action
        self.character = character

    def cost(self):
        """
        Return the cost to get to this cell.
        """
        return self._cost

    def __repr__(self):
        return '<Cell: %d, %s>' % (self._cost, self.parent)


class DistanceMatrix(object):
    """
    A Matrix that is used to calculate the edit distance between to strings.
    """
    def __init__(self, source, target):
        """
        Args:
            - source (str): the source word
            - target (str): the target word
        """
        self._source = source
        self._target = target
        self._slen = len(self._source)
        self._tlen = len(self._target)
        self._table = self.init_table()

    def __getitem__(self, index):
        return self._table.__getitem__(index)
    
    def __setitem__(self, index, value):
        self._table.__setitem__(index, value)

    def init_table(self):
        """
        Inititalize the distance matrix.
        """
        return [[Cell() for i in xrange(self._slen+1)] 
                for j in xrange(self._tlen+1)]

    def insert(self, i, j, cost=1):
        """
        Returns the insertion cost
        """
        return Cell(cost = self[i-1][j].cost() + cost, action = 'INS',
                    parent = [i-1, j], character = ('_', self._target[i-1]))

    def replace(self, i, j, cost=2):
        """
        Returns: the replacement cost
        """
        return Cell(cost = self[i-1][j-1].cost() + cost, action = 'REP',
                    parent = [i-1, j-1],
                    character = (self._source[j-1], self._target[i-1]))

    def delete(self, i, j, cost=1):
        """
        Returns: the deletion cost
        """
        return Cell(cost = self[i][j-1].cost() + cost, action = 'DEL',
                    parent = [i, j-1], character = (self._source[j-1], '_'))

    def distance(self):
        """
        Returns: the distance between two strings
        """
        return self[self._tlen][self._slen].cost()

    def backtrace(self):
        """
        Returns: the transformation path for two strings with the lowest cost.
        """
        i, j = self._tlen, self._slen
        traceback = []
        while i > 0 or j > 0:
            cell = self[i][j]
            traceback.append((cell.character, cell.action))
            i, j = cell.parent
        traceback.reverse()
        return traceback


def edit_distance(source, target, matrixclass=DistanceMatrix):
    """
    Calculate the Levenstein distance for string word1 and word2::

        >>> matrix = edit_distance('beuk', 'deuk')
        >>> matrix.distance()
        2

    Args:
        - source (str): the source word
        - target (str): the target word
    Returns:
        :class:`DistanceMatrix` -- a distance matrix
    """
    matrix = matrixclass(source, target)
    for i in xrange(1, matrix._tlen+1):
        matrix[i][0] = matrix.insert(i, 0)
    for j in xrange(1, matrix._slen+1):
        matrix[0][j] = matrix.delete(0, j)
    for i, j in product(xrange(1, matrix._tlen+1), xrange(1, matrix._slen+1)):
        if target[i-1] == source[j-1]:
            matrix[i][j] = matrix.replace(i, j, cost=0)
        else:
            matrix[i][j] = min(
                matrix.insert(i, j), matrix.replace(i, j), matrix.delete(i, j),
                key=lambda cell: cell.cost())
    return matrix


def rewrite_string(trace):
    """
    Based on the backtrace of edit_distance, return a string that can
    be given to the different classifiers::

        >>> m = edit_distance('beuk', 'deuk')
        >>> print m.backtrace()
        [(('b', '_'), 'DEL'), (('_', 'd'), 'INS'), (('e', 'e'), 'REP'),
         (('u', 'u'), 'REP'), (('k', 'k'), 'REP')]
        >>> print rewrite_string(m.backtrace())
        ['b+DEL:b+INS:d', 'e', 'u', 'k']
    """
    transform = []
    delt, ins = False, False
    i = 0
    while i < len(trace):
        (s, t), a = trace[i]
        if a == 'REP':
            if s != t:
                transform.append('%s+DEL:%s+INS:%s' % (s, s, t))
                ins = True
            else:
                transform.append('%s' % s)
                ins = False
            delt = False
        elif a == 'DEL':
            transform.append('%s+DEL:%s' % (s, s))
            delt = True
            ins = False
        elif a == 'INS':
            if i > 0:
                if delt or not ins:
                    transform[-1] += '+INS:%s' % t
                elif ins:
                    transform[-1] += '%s' % t
            else:
                i += 1
                s = trace[i][0][0]
                while s == '_':
                    t += trace[i][0][1]
                    i += 1
                    s = trace[i][0][0]
                transform.append('%s+DEL:%s+INS:%s%s' % (s, s, t, s))
            ins = True
            delt = False
        else: print 'This cannot be!'
        i += 1
    return transform
