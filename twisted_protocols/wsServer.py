# -*- coding:utf-8 -*-
import time
from twisted.python import log
from twisted.internet import protocol, reactor, defer, threads
from twisted.protocols import basic
from twisted.enterprise import adbapi
from sqlhelper import handleSosSql, handleBindSql, insertLocationSql, handleImsiSql, selectWsinfoSql, insertBatteryLevel
from SosModuleSql import deleteSosNumberSql, syncSosSql, syncFamilySql
from StickModuleSql import handleStickBindAck
from GetLocationByBs import getLocationByBsinfo


SQLUSER = 'tanghao'
PASSWORD = '123456'

def insertLocation(wsdbpool, message):
    def _convertToFloat(lati_or_longi):
        #convert string to float, iiff.ffff->dd + (ffffff)/60
        index = lati_or_longi.index('.')
        lati_or_longi_intPart = int(lati_or_longi[0:index-2])
        lati_or_longi_floatPart = float(lati_or_longi[index-2:]) / 60
        return lati_or_longi_intPart + lati_or_longi_floatPart

    def _getGpsinfoFromMessage(message):
        longitude = message[3][:-1].strip()
        latitude = message[4][:-1].strip()
        longitude = _convertToFloat(longitude)
        latitude = _convertToFloat(latitude)
        if (message[3][-1] == 'W') or (message[3][-1] == 'w'):
            longitude = 0 - longitude
        if (message[4][-1] == 's') or (message[4][-1] == 'S'):
            latitude = 0 - latitude
        return longitude, latitude

    def _convertSignalToRssi(signal):
        if signal < 4 or signal == 99:
            return -107
        elif signal < 10:
            return -93
        elif signal < 16:
            return -71
        elif signal < 22:
            return -69
        elif signal < 28:
            return -57
        elif signal >= 28:
            return -56

    def _getGpsinfoCallback(wsinfo, imei, lac, cid, signal, timestamp):
        imsi = wsinfo[0][1]
        mcc = imsi[0:3]
        mnc = imsi[3:5]
        return threads.deferToThread(getLocationByBsinfo, mcc, mnc, imei, imsi, lac, cid, signal, timestamp)

    def _insertLocation(gpsinfo, wsdbpool, imei, timestamp):
        if gpsinfo != '0,0':
            gpsinfo = str(gpsinfo).split(',')
            return insertLocationSql(wsdbpool, imei, gpsinfo[0], gpsinfo[1], timestamp, 'b')
        else:
            d = defer.Deferred()
            d.callback(None)
            return d


    message = message.split(',')
    imei = str(message[1]).strip()
    if int(message[2].strip()) == 0:
        timestamp = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    else:
        timestamp = '20'+ message[2].strip()

    longitude, latitude = _getGpsinfoFromMessage(message)

    #get longitude and latitude in string format form message
    lac = int(message[5], 16)
    cid = int(message[6], 16)
    signal = _convertSignalToRssi(int(message[7]))
    try:
        batteryLevel = int(message[8])
        charging = int(message[9])
    except Exception as e:
        batteryLevel = 50
        charging = 0

    if longitude == 0 or latitude == 0:
        d = selectWsinfoSql(wsdbpool, imei).addCallback(_getGpsinfoCallback, imei, lac, cid, signal, timestamp).addCallback(_insertLocation, wsdbpool, imei, timestamp)
    else:
        d = insertLocationSql(wsdbpool, imei, longitude, latitude,  timestamp)
    d.addCallback(insertBatteryLevel, wsdbpool, imei, batteryLevel, charging, timestamp)
    return d

def onError(failure, transport, message):
        log.msg(failure)
        transport.write(''.join(("Result:", message[0], ',0')))



class WsServer(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        #log.msg('in wsServer, wsdbpool id: ' + str(id(self.factory.wsdbpool)))
    
    def onSuccess(self, result, transport, message):
        if result == True or result == None or type(result) == tuple or type(result) == list:
            transport.write(''.join(("Result:", message[0], ',1')))
        elif result == False:
            transport.write(''.join(("Result:", message[0], ',0')))


    def dataReceived(self, message):
        log.msg(message)
        for m in message.split(','):
            if len(m) == 0 and message[0] != '5' and message[0] != '7':
                self.transport.write(''.join(("Result:", message[0], ',0')))
                return

        #this is ok becase protocol is instantiated for each connection, so it won't has confusion
        if message[0] == '1':
            handleStickBindAck(self.factory.wsdbpool, message).addCallbacks(self.onSuccess, onError, callbackArgs=(self.transport, message), errbackArgs=(self.transport, message))
        elif message[0] == '2':
            handleSosSql(self.factory.wsdbpool, message).addCallbacks(self.onSuccess, onError, callbackArgs=(self.transport, message), errbackArgs=(self.transport, message))
        elif message[0] == '3':
            tempList = list()
            for msg in message.splitlines():
                #d = insertLocation(self.factory.wsdbpool, msg).addCallbacks(self.onSuccess, onError, callbackArgs=(self.transport, msg), errbackArgs=(self.transport, msg))
                tempList.append(insertLocation(self.factory.wsdbpool, msg))
            d = defer.gatherResults(tempList, consumeErrors=True).addCallbacks(self.onSuccess, onError, callbackArgs=(self.transport, msg), errbackArgs=(self.transport, msg))


        elif message[0] == '4':
            handleImsiSql(self.factory.wsdbpool, message).addCallbacks(self.onSuccess, onError, callbackArgs=(self.transport, message), errbackArgs=(self.transport, message))
        elif message[0] == '5':
            syncSosSql(self.factory.wsdbpool, message).addCallbacks(self.onSuccess, onError, callbackArgs=(self.transport, message), errbackArgs=(self.transport, message))
        elif message[0] == '6':
            if message[-2:] == 'ok' or message[-2:] == 'OK':
                deleteSosNumberSql(self.factory.wsdbpool, message.split(',')[1]).addCallbacks(self.onSuccess, onError, callbackArgs=(self.transport, message), errbackArgs=(self.transport, message))
            else:
                self.transport.write(''.join(("Result:", message[0], ',0')))
        elif message[0] == '7':
            syncFamilySql(self.factory.wsdbpool, message).addCallbacks(self.onSuccess, onError, callbackArgs=(self.transport, message), errbackArgs=(self.transport, message))




class WsServerFactory(protocol.Factory):
    def __init__(self, wsdbpool):
        self.wsdbpool = wsdbpool

    def buildProtocol(self, addr):
        return WsServer(self)

if __name__ == '__main__':
    from sqlPool import wsdbpool
    from sys import stdout
    #wsdbpool = adbapi.ConnectionPool("MySQLdb", db="wsdb", user='tanghao', passwd='123456')
    log.startLogging(stdout)
    reactor.listenTCP(8081, WsServerFactory(wsdbpool))
    reactor.run()
