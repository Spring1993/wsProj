import os
import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, succeed, DeferredList
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.iweb import IBodyProducer
from zope.interface import implements
from json import dumps
import time
from twisted.internet.task import LoopingCall

import socket
server_address = ('localhost', 8081)

def testTcp():
    tcplocation = '6,1024,ok'
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)
        sock.sendall(tcplocation)
        data = sock.recv(96)
        log.msg(data)
    except Exception, e:
        log.msg(e)
        log.msg('\tSERVER RESTART')
    finally:
        sock.close()

def finish():
    reactor.stop()

if __name__ == '__main__':
    os.system('touch ./babysiter.py')
    log.startLogging(open('./log_file/babysiter.log', 'w'))
    LoopingCall(testTcp).start(600)
    reactor.run()

