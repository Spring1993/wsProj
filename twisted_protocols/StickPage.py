# -*- coding:utf-8 -*-
from json import dumps, loads

from twisted.python import log
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
import cgi

from appServerCommon import onError, resultValue, onSuccess, appRequest
from sqlhelper import *
from sqlPool import wsdbpool
import StickModuleSql



class StickPage(Resource):
    isLeaf = True
        

    def onImeiResult(self, result, request):
        if len(result) == 0:
            request.write(resultValue(501))
        else:
            request.write(dumps({'result':'1', 'imei': result[0][1], 'type': result[0][2]}))
        request.finish()


    def onGetCode(self, code, request, payload):
        request.write(dumps({'result': '1', 'code': str(code), 'imei': payload['imei']}))
        request.finish()

    def onGetImei(self, code, request):
        request.write(dumps({'result': '1', 'imei': str(code)}))
        request.finish()

    def onSubscribe(self, wsinfo, request):
        request.write(dumps({'result': '1', 'imei': wsinfo[0], 'simnum': wsinfo[2], 'type': 's'}))
        request.finish()

    def onBatteryLevel(self, result, request):
        if len(result) == 0:
            request.write(resultValue(505))
        else:
            result = result[0]
            request.write(dumps({'result': '1', 'imei': str(result[0]), 'level': str(int(result[1])), 'charging': str(result[2]), 'timestamp': str(result[3])}))
        request.finish()

    def render_POST(self, request):

        payload = eval(request.content.read())
        log.msg(str(payload))

        apprequest = appRequest(payload)
        if apprequest.isValid == False:
            return resultValue(300)

        if request.args['action'] == ['bind']:
            d = StickModuleSql.handleAppBindRequest(wsdbpool, payload['username'], payload['simnum'], payload['name'])
            d.addCallback(onSuccess, request)
            d.addErrback(onError, request)
            return NOT_DONE_YET

        elif request.args['action'] == ['getimei']:
            d = StickModuleSql.getRelationByUsernameSimnum(wsdbpool, payload['username'], payload['simnum'])
            d.addCallback(self.onImeiResult, request)
            d.addErrback(onError, request)
            return NOT_DONE_YET

        if request.args['action'] == ['setcurrentimei']:
            d = StickModuleSql.setImeiDefault(wsdbpool, payload['username'], payload['imei'])
            d.addCallback(onSuccess, request)
            d.addErrback(onError, request)
            return NOT_DONE_YET

        if request.args['action'] == ['getverifycode']:
            d = StickModuleSql.createAuthCode(wsdbpool, payload['imei'])
            d.addCallback(self.onGetCode, request, payload)
            d.addErrback(onError, request)
            return NOT_DONE_YET

        if request.args['action'] == ['getimeibycode']:
            d = StickModuleSql.getImeiByCode(wsdbpool, payload['code'])
            d.addCallback(self.onGetImei, request)
            d.addErrback(onError, request)
            return NOT_DONE_YET

        if request.args['action'] == ['subscribebycode']:
            d = StickModuleSql.handleAppSubRequest(wsdbpool, payload['username'], payload['name'], payload['code'])
            d.addCallback(self.onSubscribe, request)
            d.addErrback(onError, request)
            return NOT_DONE_YET

        if request.args['action'] == ['getbatterylevel']:
            selectBatteryLevel(wsdbpool, payload['imei']).addCallbacks(self.onBatteryLevel, onError, callbackArgs=(request,))
            return NOT_DONE_YET

            


stickPage = StickPage()
