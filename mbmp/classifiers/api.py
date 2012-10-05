## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

"""
API of the different memory-based classifiers implemented
in :mod:`mbmp.classifier`
"""

import sys
import atexit
  
from mbmp.client import TimblClient
from mbmp.server import TimblServer
from mbmp.server.util import server_in_use
from mbmp.train import format_testitem


class MBClassifier(object):
    """
    Abstract Class representing a Memory-Based Classifier. The classifier
    sets up a :class:`mbmp.server.TimblServer` instance and connects to this
    server via a :class:`mbmp.client.TimblClient`.
    """
    def __init__(self, host, port, settings, **kwargs):
        """
        Initializes a MBClassifier, sets up a L{TimblServer}
        and connects to this server via an instance of L{TimblClient}.

        Args:
            - host (str): Host specifies the server address (localhost by default)
            - port (int): Port specifies the server tcp communicating port.
            - settings (dict): the settings used by Timbl (see :mod:`config`)
        """
        self.server = TimblServer(host=host, port=port, features=settings,
                                  classifier=self.__class__.__name__,)
        self.server.run()
        self.client = TimblClient(host=host, port=port)

        # register the kill method to make sure the timblserver is killed
        # at exiting the interactive shell
        atexit.register(self.kill)
        
    def __repr__(self):
        return '<%s connected to %s>' % (
            self.__class__.__name__, self.client.name)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        """
        Within a 'with' statement, always kill the server and close the
        connection to the server in case of an error.
        """
        self.kill()

    def kill(self):
        """
        Close the connection between the client and the server and
        kill the server if not in use by another process.
        """
        self.client.close()
        if server_in_use(self.server):
            sys.stderr.write(
                'Connection closed. Cannot kill timbl server; server in '
                'use by other instance or by someone else.\n')
        else:
            if self.server._process is not None:
                self.server.kill()

    def _classify(self, iterable, size=5):
        """
        Helper function to query the server.

        Args:
            - iterable (iterable): the item to be classified
            - size (int): the window size used be the classifier
        Returns:
            List of predictions per element of iterable
        """
        return [self.client.query(elt)
                for elt in format_testitem(iterable, size)]

    def classify(self, word):
        """
        Return a list of outcome classes for each element of WORD.

        Args:
            - word (str): a string representing a word.
        Returns:
            List of predicted outcomes per letter of word.
        """
        raise NotImplementedError('MBClassifier is an abstract interface')
        
    def pprint_parse(self, parse):
        """
        Return a pretty print of the classification.

        Args:
            - parse: the parse returned by :func:`mbmp.MBClassifier.classify`
        Returns:
            A string representation of parse
        """
        raise NotImplementedError('MBClassifier is an abstract interface')

    def trees(self, parse):
        """
        Return a tree-structure of the classification using the NLTK-Tree
        Class.

        Args:
            - parse: the parse returned by :func:`mbmp.MBClassifier.classify`
        Yields:
            a generator with all tree structures obtained.
        """
        raise NotImplementedError('MBClassifier is an abstract interface')
