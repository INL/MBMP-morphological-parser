## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

"""
Module that implements a client for communicating with a timblserver. Note
that the class TimblClient does not depend on the class
:class:`mbmp.server.TimblServer` but expects an original timblserver running
at some host and port.
"""

import re
import socket

from mbmp.mbmp_exceptions import ConnectionError


def format_query(query):
    """
    Transform the query into the format required by the TimblServer.

    Args:
        - query (str): the query send to the timblserver.
    """
    query = query.encode('utf-8')
    # all queries must start with 'c '!
    if not query.startswith('c '):
        query = 'c ' + query.strip()
    # check if outcome of query is set to '?'
    if query[-1] != '?':
        query = query + ' ?'
    return query + '\n'

def format_answer(answer):
    """
    Remove all information except the outcome class from the servers response.

    Args:
        - answer (str): the answer returned by the timblserver
    """
    # a regular expression matching the predicted outcome
    # by timbl.
    pattern = re.compile(r'CATEGORY \{([^}]+)\}')
    answer = pattern.search(answer)
    return answer and answer.group(1) or '0'


class TimblClient(object):
    """
    A client for communicating with the TimblServer.
    """

    def __init__(self, host='localhost', port=None):
        """
        Connects to an instance of TimblServer.

        Args:
            - host (str): Host specifies the server address (default localhost).
            - port (int): Port specifies the server tcp communicating port.
        """
        self.host = host
        self.port = port
        self.name = '%s:%s' % (self.host, self.port)
        self.socket = None
        self.packet_size = 1024
        self._send = 0
        self._reset = 100
        # try to connect with a TimblServer instance
        self.connect()

    def __repr__(self):
        return '<TimblClient connected to %s' % self.name

    def __del__(self):
        self.close()

    def connect(self):
        """
        Connect to the server at the tcp communicating port.

        Raises: ConnectionError if no connection can be made.
        """
        try:
            self._send = 0
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM,
                                        socket.getprotobyname('tcp'))
            self.socket.connect((self.host, self.port))
            self.socket.recv(self.packet_size)
        except socket.error:
            raise ConnectionError(
                'Cannot connect to server at %s' % self.name)

    def reconnect(self):
        """
        Try to reconnect the client to the server.
        """
        self.close()
        self.connect()

    def _stream(self):
        """
        Return the servers response on the query.
        """
        packets = [self.socket.recv(self.packet_size)]
        while ('\n' not in reversed(packets[-1]) or
               (packets[-1] == '\n' and len(packets) == 1)):
            packets.append(self.socket.recv(self.packet_size))
        return ''.join(packets)

    def query(self, query):
        """
        Send a query to the listening server.

        Args:
            - query (str): the query to be send to the timblserver.
        Returns:
            str -- The answer of the timblserver.
        Raises:
            socket.error: Server is not running
        """
        # if self._send > self._reset:
        #     self.reconnect()
        query = format_query(query)
        try:
            self.socket.send(query)
        except socket.error:
            raise ConnectionError('Server is not running.')
        answer = self._stream()
        self._send += 1
        answer = format_answer(answer)
        return answer

    def close(self):
        """
        Close the connection between the client and the server.
        """
        self.socket.close()
        return True


