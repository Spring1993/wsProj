# -*- coding:utf-8 -*-
from twisted.python import log
from twisted.internet import protocol, reactor, defer, threads
from twisted.protocols import basic
import time
from twisted.enterprise import adbapi
from sqlhelper import handleSosSql, handleBindSql, insertLocationSql

SQLUSER = 'tanghao'
PASSWORD = '123456'


def insertLocation(dbpool, message):
    message = message.split(',')
    imei = str(message[1]).strip()
    timestamp = '20'+ message[2].strip()
    longitude = message[3][:-1].strip()
    latitude = message[4][:-1].strip()
    if (message[3][-1] == 'W') or (message[3][-1] == 'w'):
        longitude = '-' + longitude
    if (message[4][-1] == 's') or (message[4][-1] == 'S'):
        latitude = '-' + latitude
    return insertLocationSql(dbpool, imei, longitude, latitude,  timestamp)


class WsServer(protocol.Protocol):
    
    def onError(self, failure):
        log.msg(failure)
        self.transport.write(''.join(("Result:", self.message[0], ',0')))

    def onSuccess(self, result):
        if result == True or result == None:
            self.transport.write(''.join(("Result:", self.message[0], ',1')))
        elif result == False:
            self.transport.write(''.join(("Result:", self.message[0], ',0')))


    def dataReceived(self, message):
        #this is ok becase protocol is instantiated for each connection, so it won't has confusion
        self.message = message
        if message[0] == '1':
            handleBindSql(dbpool, message).addCallbacks(self.onSuccess, self.onError)
        if message[0] == '2':
            handleSosSql(dbpool, message).addCallbacks(self.onSuccess, self.onError)
        if message[0] == '3':
            insertLocation(dbpool, message).addCallbacks(self.onSuccess, self.onError)



class WsServerFactory(protocol.Factory):
    protocol = WsServer


from sys import stdout
dbpool = adbapi.ConnectionPool("MySQLdb", db="wsdb", user='tanghao', passwd='123456')
log.startLogging(stdout)
log.startLogging(open('./wsserver.log', 'w'))
reactor.listenTCP(8081, WsServerFactory())
reactor.run()