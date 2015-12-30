# -*- coding:utf-8 -*-
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


class StringProducer(object):
    implements(IBodyProducer)
    
    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

class ResourcePrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished

    def dataReceived(self, data):
        #print time.time(), 'received data', data
        print data

    def connectionLost(self, reason):
        self.finished.callback(None)

def printResource(response):
    finished = Deferred()
    response.deliverBody(ResourcePrinter(finished))
    return finished


def stop(result):
    reactor.stop()

tcplocation = '3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,113\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,13\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n3,1024,151202071454,11356.28750E,2232.94179N,2495,1395,24,100,0,1\r\n'
tcpaddsos = '2,862609000056700,add18688702834'
tcpdelsos = '2,8789,del12332112345'
tcpimsi = '4,868986022047287,460002606774194'
tcpbind = '1,1028,bon1234567890,15882205392'
tcpdelete = '6,1023,ok'
tcpsync = '5,98789,3,7,12332112345,92332112345,22332112345'




gpsrequest = dumps({'imei': '867715029503039', 'timestamp': '1448824052000'})
bindrequest = dumps({'username': 'zod', 'simnum': '1234567890', 'name': '拐杖'})
imeirequest = dumps({'username': 'zod', 'simnum': '13836435683'})
setsosrequest = dumps({'imei': '98787', 'adminpwd': '123456', 'contactentry': {'sosnumber': '72332112345', 'contact':'蝙蝠侠'}})
delsosrequest = dumps({'imei': '1024', 'adminpwd': '123456', 'contactentry': {'sosnumber': '12332112345', 'contact':'蝙蝠侠'}})
varifyadd = dumps({'imei': '98789', 'sosnumber': '12332112345'})
varifydel = dumps({'imei': '98789', 'sosnumber': '12332112345'})
getsos = dumps({'imei': '1024'})
updatepwd = dumps({'imei': '1024', 'adminpwd': '123456', 'newadminpwd': '223456'})
register = dumps({'username': 'zod', 'password':'f'})
login = dumps({'username': 'apple', 'password':'123456'})
upwd = dumps({'username': 'wonderwoman', 'password':'f', 'newpassword': 'g'})
newname = dumps({'username': 'zod', 'imei': '1024', 'name': '绿巨人'})
getstick = dumps({'username': 'Baby'})
current = dumps({'username': 'apple', 'imei': '868986022047287'})
upload = dumps({'username': 'zod', 'sticks': [{'name': 'hull', 'imei': '9981'}, {'name': 'del', 'imei': '1028'}] })
review = dumps({'username': 'zod', 'review': '很好的app'})
#rurequest = dumps({'username': 'zox', 'password': 'f', 'sticks': [{'name': 'hull', 'imei': '1024'}, {'name': 'del', 'imei': '1023'}] })
rurequest = dumps({'username': 'zoo', 'password':'f'})
#upload = dumps({'username': 'zod', 'sticks': [] })
getcoderequest = dumps({'username': 'alice', 'imei': '98789'})
unsubrequest = dumps({'username': '702', 'imei': '868986022047287'})
forgotpassword = dumps({'username': 'xmen'})
emailrequest = dumps({'username': 'alice', 'email': 'htang@pku.edu.cn'})

host = 'http://52.68.218.151:8082/api'
gpsaddress = host + '/gps?action=getuserlocation'
bindaddress = host + '/stick?action=bind'
imeiaddress = host + '/stick?action=getimei'
currentaddress = host + '/stick?action=setcurrentimei'
batteryaddress = host + '/stick?action=getbatterylevel'
setsosaddress = host + '/sos?action=addnumber'
delsosaddress = host + '/sos?action=delnumber'
varifyaddaddress = host + '/sos?action=varifyadd'
varifydeladdress = host + '/sos?action=varifydel'
getsosaddress = host + '/sos?action=getnumber'
updatepwdaddress = host + '/sos?action=updatepassword'
registeraddress = host + '/user?action=register'
loginaddress = host + '/user?action=login'
upwdaddress = host + '/user?action=updatepassword'
newnameaddress = host + '/user?action=setstickname'
getsticksaddress = host + '/user?action=getsticks'
getcodeaddress = host + '/stick?action=getverifycode'
getbycodeaddress = host + '/stick?action=getimeibycode'
uploadaddress = host + '/user?action=uploadsticks'
unsubaddress = host + '/user?action=unsubscribe'
reviewaddress = host + '/user?action=review'
ruaddress = host + '/user?action=registerandupload'
updateaddress = host + '/user?action=updateapp'
checkaddress = host + '/user?action=checkemail'
getemailaddress = host + '/user?action=getemail'
emailaddress = host + '/user?action=fillinemail'
passwordaddress = host + '/user?action=forgotpassword'
subaddress = host + '/stick?action=subscribebycode'


agent = Agent(reactor)

def printResource(response):
    finished = Deferred()
    response.deliverBody(ResourcePrinter(finished))
    return finished

def printError(failure):
    import os
    print  failure
    #os.system('twistd -y init.py')
    print 'SERVE　RESTARTED'

def stop(result):
   # print time.time(), '\treactor stop'
    reactor.stop()

def makeTest(request, address):
    if sys.argv[1] == 'updateapp' or sys.argv[1] == 'checkemail':
        d = agent.request('GET', address, bodyProducer = StringProducer(request))
    else:
        d = agent.request('POST', address, bodyProducer = StringProducer(request))
    d.addCallbacks(printResource, printError)
    d.addBoth(stop)
    reactor.run()
    

def asynchroTest(requests, addresses):
    dl = list()
    for z in zip(requests, addresses):
        d = agent.request('POST', z[1], bodyProducer=StringProducer(z[0]))
        d.addCallback(printResource)
        dl.append(d)
    deferList = DeferredList(dl, consumeErrors=True)
    deferList.addCallback(printResource)
    deferList.addBoth(stop)
    reactor.run()



def testTcp(message):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('smartcane.huahailife.com', 8081)
    sock.connect(server_address)

    try:
        sock.sendall(message)
        data = sock.recv(96)
        print >> sys.stdout, 'RECEIVED: %s' % data
    finally:
        print >> sys.stdout, 'CLOSING SOCKET'
        sock.close()

def multiTest():
    try:
        server_address = ('smartcane.huahailife.com', 8081)
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1.connect(server_address)
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.connect(server_address)

        location1 = '3,1025,150930141223,23.12321,87.22234'
        location2 = '3,1024,150930141223,23.12321W,87.22234N'
        sock1.sendall(location1)
        sock2.sendall(location2)
        data1 = sock1.recv(96)
        data2 = sock1.recv(96)
        
        print >> sys.stdout, 'RECEIVED: %s' % data1
        print >> sys.stdout, 'RECEIVED: %s' % data2
    finally:
        print >> sys.stdout, 'CLOSING SOCKET'
        sock1.close()
        sock2.close()

if sys.argv[1] == 'multi':
    multiTest()

if sys.argv[1] == 'sub':
    code = sys.argv[2]
    subrequest = dumps({'username': 'hulk', 'name': 'needle', 'code': str(code)})
    makeTest(subrequest, subaddress)

if sys.argv[1] == 'ru':
    makeTest(rurequest, ruaddress)

if sys.argv[1] == 'forgotpassword':
    makeTest(forgotpassword, passwordaddress)

if sys.argv[1] == 'unsub':
    makeTest(unsubrequest, unsubaddress)
if sys.argv[1] == 'getemail':
    makeTest(forgotpassword, getemailaddress)

if sys.argv[1] == 'updateapp':
    makeTest('asdfadsf', updateaddress)
if sys.argv[1] == 'checkemail':
    makeTest('asdfadsf', checkaddress)
if sys.argv[1] == 'review':
    makeTest(review, reviewaddress)
if sys.argv[1] == 'fillinemail':
    makeTest(emailrequest, emailaddress)

if sys.argv[1] == 'gps':
    makeTest(gpsrequest, gpsaddress)
if sys.argv[1] == 'bind':
    makeTest(bindrequest, bindaddress)
if sys.argv[1] == 'tcpbind':
    testTcp(tcpbind)
if sys.argv[1] == 'tcplocation':
    testTcp(tcplocation)
if sys.argv[1] == 'getimei':
    makeTest(imeirequest, imeiaddress)
if sys.argv[1] == 'setsos':
    makeTest(setsosrequest, setsosaddress)
if sys.argv[1] == 'delsos':
    makeTest(delsosrequest, delsosaddress)
if sys.argv[1] == 'varifyadd':
    makeTest(varifyadd, varifyaddaddress)
if sys.argv[1] == 'varifydel':
    makeTest(varifydel, varifydeladdress)
if sys.argv[1] == 'getsos':
    makeTest(getsos, getsosaddress)
if sys.argv[1] == 'getbattery':
    makeTest(getsos, batteryaddress)
if sys.argv[1] == 'updatepwd':
    makeTest(updatepwd, updatepwdaddress)
if sys.argv[1] == 'register':
    makeTest(register, registeraddress)
if sys.argv[1] == 'current':
    makeTest(current, currentaddress)
if sys.argv[1] == 'login':
    try:
        makeTest(login, loginaddress)
    except Exception, e:
        print 'Server gone away, err msg: ', e
if sys.argv[1] == 'upwd':
    makeTest(upwd, upwdaddress)
if sys.argv[1] == 'newname':
    makeTest(newname, newnameaddress)
if sys.argv[1] == 'upload':
    makeTest(upload, uploadaddress)
if sys.argv[1] == 'getstick':
    makeTest(getstick, getsticksaddress)
if sys.argv[1] == 'tcpimsi':
    testTcp(tcpimsi)
if sys.argv[1] == 'tcpsetsos':
    print tcpaddsos
    testTcp(tcpaddsos)
if sys.argv[1] == 'tcpdelsos':
    testTcp(tcpdelsos)
if sys.argv[1] == 'tcpdelall':
    testTcp(tcpdelete)
if sys.argv[1] == 'tcpsync':
    testTcp(tcpsync)
if sys.argv[1] == 'getcode':
    makeTest(getcoderequest, getcodeaddress)
if sys.argv[1] == 'getbycode':
    makeTest(dumps({'code': str(sys.argv[2])}), getbycodeaddress)


if sys.argv[1] == 'gpspage':
    requests = list()
    for i in xrange(300):
        requests.append(register)
        requests.append(gpsrequest)
        requests.append(current)
    '''
    requests.append(upload)
    requests.append(getstick)
    requests.append(login)
    requests.append(gpsrequest)
    requests.append(current)
    requests.append(getsos)
    '''
    addresses = list()
    for i in xrange(300):
        addresses.append(registeraddress)
        addresses.append(gpsaddress)
        addresses.append(currentaddress)
    '''
    addresses.append(gpsaddress)
    addresses.append(currentaddress)
    addresses.append(getsosaddress)
    addresses.append(loginaddress)
    '''
    asynchroTest(requests, addresses)

