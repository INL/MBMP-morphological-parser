## Python implementation of MBMA (Van den Bosch & Daelemans 1999)

## Copyright (C) 2011 Institute for Dutch Lexicology (INL)
## Author: Folgert Karsdorp, INL
## E-mail: <servicedesk@inl.nl>
## URL: <http://www.inl.nl/>
## For licence information, see LICENCE.TXT

import os
import tempfile
import socket
import subprocess


def pid_file(server):
    """
    Return the path to the file holding the pid for a given instance
    of TimblServer.

    Args:
        - server: an instance of Timblserver that needs to be started
    Returns:
        str -- the path to the file containing the pid for this server.
    """
    return os.path.join(
        tempfile.gettempdir(),
        'mbmp.%s_%s_%s.pid' % (server.classifier, server.port, server.host))

def remove_pid_file(server):
    """
    Remove the file holding the pid for a given instance of TimblServer.

    Args:
        - server: an instance of Timblserver that needs to be started
    Returns:
        boolean        
    """
    try:
        os.remove(pid_file(server))
    except OSError:
        pass

def free_port(server):
    """
    Utility function to check whether a given port is free.

    Args:
        - server: an instance of Timblserver that needs to be started
    Returns:
        boolean        
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server.host, server.port))
        s.close()
        return False
    except socket.error, e:
        return True

def server_in_use(serverinstance):
    """
    Check if there are any other connections with the timblserver. If so,
    return True, else return False.

    Args:
        - server: an instance of Timblserver that needs to be started
    Returns:
        boolean
    """
    command = 'netstat -an | grep :%s' % serverinstance.port
    p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         close_fds=True)
    # count how many established connections there are
    established = sum(1 for line in p.stdout if 'ESTABLISHED' in line)
    if established > 1:
        return True
    return False

