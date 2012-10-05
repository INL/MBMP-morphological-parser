## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

class ConnectionError(Exception):
    """
    Exception used to catch connection errors with the timbl server.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class ServerConnectionError(ConnectionError):
    pass

