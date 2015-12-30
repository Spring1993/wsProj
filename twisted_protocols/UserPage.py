# -*- coding:utf-8 -*-
from json import dumps, loads
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time

from twisted.python import log
from twisted.internet import reactor, defer, threads
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET

import cgi

from appServerCommon import onError, resultValue
from sqlhelper import *
from sqlPool import wsdbpool


class UserPage(Resource):
    isLeaf = True

    def unSubSuccess(self, result, request, imei):
        request.write(dumps({'imei': imei, 'result': '1'}))
        request.finish()

    def unSubError(self, failure, request, imei):
        request.write(dumps({'imei': imei, 'result': str(failure.value.errCode)}))
        request.finish()



    def checkUser(self, result, payload):
        if len(result) != 0:
            d = defer.Deferred()
            d.callback('400')
            return d
        else:
            return insertUserSql(wsdbpool, username=payload['username'], passwd=payload['password'])

    def onResult(self, result, request):
        log.msg(str(result))
        if result in ['400', '401', '402', '403', '404']:
            request.write(resultValue(result))
        elif type(result) == tuple and len(result) != 0:
            #user has only 1 stick
            if len(result) == 1:
                request.write(dumps({'result': '1', 'imei': result[0][1], 'name': result[0][2], 'type': result[0][3], 'simnum': result[0][5]}))
            else:
                #user have many sticks
                info = result[0]
                for r in result:
                    if r[4] == '1':
                        info = r
                print 'INFO !!!! ', info
                request.write(dumps({'result': '1', 'imei': info[1], 'name': info[2], 'type': info[3], 'simnum': info[5]}))


        elif type(result) == tuple and len(result) == 0:
            request.write(resultValue(404))
        else:
            request.write(resultValue(1))
        request.finish()

    
    def onLogin(self, result, request, payload):
        if len(result) == 0:
            d = defer.Deferred()
            d.callback('401')
            return d
        if payload['password'] != result[0][1]:
            d = defer.Deferred()
            d.callback('402')
            return d
        if request.args['action'] == ['login']:
            return selectLoginInfoSql(wsdbpool, payload['username'])
        if request.args['action'] == ['updatepassword']:
            return UpdateUserPasswordSql(wsdbpool, username=payload['username'], newpassword=payload['newpassword'])

    def onRegister(self, result, request):
        if str(result) == '400':
            request.write(resultValue(result))
        else:
            request.write(resultValue('1'))

        request.finish()
        
    
    def onChangeName(self, result, payload):
        if len(result) == 0:
            return '403'
        else:
            return updateStickNameSql(wsdbpool, username=payload['username'], imei=payload['imei'], name=payload['name'])


    def onGetSticks(self, result, request):
        if len(result) == 0:
            request.write(resultValue(404))
        else:
            sticks = list()
            for r in result:
                stick = dict()
                stick['type'] = str(r[3])
                stick['simnum'] = str(r[2])
                stick['name'] = str(r[1])
                stick['imei'] = str(r[0])
                sticks.append(stick)
            request.write(dumps({'result': '1', 'sticks': sticks}))
        request.finish()

    def onUpload(self, result, request):
        if result:
            request.write(resultValue(1))
        else:
            request.write(resultValue(403))
        request.finish()

    def onRegisterUpload(self, result, request):
        if result == True:
            request.write(resultValue(1))
        elif result == 400:
            request.write(resultValue(400))
        request.finish()

    def render_POST(self, request):
        payload = eval(request.content.read())
        log.msg(str(payload))

        if request.args['action'] == ['register']:
            if 'username' not in payload or 'password' not in payload:
                return resultValue(300)
            if len(payload['username']) == 0 or len(payload['password']) == 0:
                return resultValue(300)
            d = selectUserSql(wsdbpool, payload['username']).addCallback(self.checkUser, payload)
            d.addCallback(self.onRegister, request)
            d.addErrback(onError)
            return NOT_DONE_YET
        if request.args['action'] == ['registerandupload']:
            if 'username' not in payload or 'password' not in payload:
                return resultValue(300)
            if 'sticks' in payload:
                for s in payload['sticks']:
                    if len(s['name']) == 0 or len(s['imei']) == 0:
                        return resultValue(300)
            handleRegisterandUploadSql(wsdbpool, payload).addCallbacks(self.onRegisterUpload, onError, callbackArgs=(request,))
            return NOT_DONE_YET
            


        if request.args['action'] == ['login']:
            if 'username' not in payload or 'password' not in payload:
                return resultValue(300)
            if len(payload['username']) == 0 or len(payload['password']) == 0:
                return resultValue(300)
            d = selectUserSql(wsdbpool, payload['username']).addCallback(self.onLogin, request, payload).addCallback(self.onResult, request)
            d.addErrback(onError)
            return NOT_DONE_YET
        if request.args['action'] == ['updatepassword']:
            if 'username' not in payload or 'password' not in payload or 'newpassword' not in payload:
                return resultValue(300)
            if len(payload['username']) == 0 or len(payload['newpassword']) == 0:
                return resultValue(300)
            d = selectUserSql(wsdbpool, payload['username']).addCallback(self.onLogin, request, payload).addCallback(self.onResult, request)
            d.addErrback(onError)
            return NOT_DONE_YET

        if request.args['action'] == ['setstickname']:
            if 'username' not in payload or 'imei' not in payload or 'name' not in payload:
                return resultValue(300)
            if len(payload['username']) == 0 or len(payload['name']) == 0 or len(payload['imei']) == 0:
                return resultValue(300)
            d = selectRelationByImeiSql(wsdbpool, payload['username'], payload['imei']).addCallback(self.onChangeName, payload)
            d.addCallback(self.onResult, request)
            d.addErrback(onError)
            return NOT_DONE_YET

        if request.args['action'] == ['getsticks']:
            if 'username' not in payload:
                return resultValue(300)
            d = selectRelationSql(wsdbpool, payload['username'])
            d.addCallback(self.onGetSticks, request)
            d.addErrback(onError)
            return NOT_DONE_YET

        if request.args['action'] == ['uploadsticks']:
            if 'username' not in payload or 'sticks' not in payload:
                return resultValue(300)
            if len(payload['username']) == 0 or len(payload['sticks']) == 0:
                return resultValue(300)
            for s in payload['sticks']:
                if len(s['name']) == 0 or len(s['imei']) == 0:
                    return resultValue(300)

            d = handleUploadSql(wsdbpool, payload)
            d.addCallback(self.onUpload, request)
            d.addErrback(onError)
            return NOT_DONE_YET
        
        if request.args['action'] == ['unsubscribe']:
            if 'username' not in payload or 'imei' not in payload:
                return resultValue(300)
            if len(payload['username']) == 0 or len(payload['imei']) == 0:
                return resultValue(300)
            d = handleUnsubscribeSql(wsdbpool, payload['username'], payload['imei']).addCallbacks(self.unSubSuccess, self.unSubError, callbackArgs=(request, payload['imei']), errbackArgs=(request, payload['imei']))
            d.addErrback(onError)
            return NOT_DONE_YET

        if request.args['action'] == ['forgotpassword']:
            if 'username' not in payload :
                return resultValue(300)
            if len(payload['username']) == 0:
                return resultValue(300)
            d = FoundPasswordSql(wsdbpool, payload['username'])
            d.addCallbacks(self.onFoundPassword, onError,callbackArgs=(request, str(payload['username'])))
            return NOT_DONE_YET

        if request.args['action'] == ['review']:
            d = insertUserReview(wsdbpool, username=payload['username'], review=payload['review'])
            d.addCallback(self.onResult, request)
            return NOT_DONE_YET

        if request.args['action'] == ['fillinemail']:
            hashcode = hash(payload['username'] + payload['email'])
            authlink = 'http://smartstick.huahailife.com:8082/api/user?action=checkemail&&username=%s&&hc=%s' %(payload['username'], hashcode)
            from sendMail import sendAuthLinkByEmail
            d = threads.deferToThread(sendAuthLinkByEmail, payload['email'], payload['username'], authlink).addCallback(insertTempEmailSql, wsdbpool, payload['username'], payload['email'])
            return resultValue(1)

        if request.args['action'] == ['getemail']:
            selectUserSql(wsdbpool, payload['username']).addCallback(self.onGetEmail, request)
            return NOT_DONE_YET

    def onGetEmail(self, result, request):
        if result[0][3] is None:
            request.write(dumps({'result': '1', 'email': ''}))
        else:
            request.write(dumps({'result': '1', 'email': result[0][3]}))
        request.finish()



    def render_GET(self, request):
        if request.args['action'] == ['updateapp']:
            self.UpdateVerson(request)
            return NOT_DONE_YET
        
        elif request.args['action'] == ['checkemail']:
		if (request.args.has_key('lang') is False) or (request.args['lang'] == ['cn']):
			d = checkEmailSql(wsdbpool, request.args['username'][0], request.args['hc'][0]).addCallback(self.onCheckEmail, request)
            		return NOT_DONE_YET

		elif request.args['lang'] == ['en']:
			d = checkEmailSql(wsdbpool, request.args['username'][0], request.args['hc'][0]).addCallback(self.onCheckEmailen, request)
			return NOT_DONE_YET

		elif request.args['lang'] == ['tw']:
			d = checkEmailSql(wsdbpool, request.args['username'][0], request.args['hc'][0]).addCallback(self.onCheckEmailtw, request)
			return NOT_DONE_YET

    def onCheckEmail(self, result, request):
	f1 = open("./twisted_protocols/correct.html",'r')
	all_the_html_correct = f1.read()
	f1.close()

	f2 = open("./twisted_protocols/invalid602.html","r")
	all_the_html_invalid602 = f2.read()
	f2.close()

	f3 = open("./twisted_protocols/invalid604.html","r")
	all_the_html_invalid604 = f3.read()
	f3.close()

	f4 = open("./twisted_protocols/invalid401.html","r")
	all_the_html_invalid401 = f4.read()
	f4.close()

        if result == 602:
            request.write(all_the_html_invalid602)
        elif result == 604:
            request.write(all_the_html_invalid604)
        elif result == 401:
            request.write(all_the_html_invalid401)
        else:
            request.write(all_the_html_correct )
        request.finish()


	def onCheckEmailen(self, result, request):
	f1 = open("./twisted_protocols/correcten.html",'r')
	all_the_html_correct = f1.read()
	f1.close()

	f2 = open("./twisted_protocols/invalid602en.htnl","r")
	all_the_html_invalid602 = f2.read()
	f2.close()

	f3 = open("./twisted_protocols/invalid604en.html","r")
	all_the_html_invalid604 = f3.read()
	f3.close()

	f4 = open("./twisted_protocols/invalid401en.html","r")
	all_the_html_invalid401 = f4.read()
	f4.close()

        if result == 602:
            request.write(all_the_html_invalid602)
        elif result == 604:
            request.write(all_the_html_invalid604)
        elif result == 401:
            request.write(all_the_html_invalid401)
        else:
            request.write(all_the_html_correct )
        request.finish()
        

	def onCheckEmailtw(self, result, request):
	f1 = open("./twisted_protocols/correcttw.html",'r')
	all_the_html_correct = f1.read()
	f1.close()

	f2 = open("./twisted_protocols/invalid602tw.htnl","r")
	all_the_html_invalid602 = f2.read()
	f2.close()

	f3 = open("./twisted_protocols/invalid604tw.html","r")
	all_the_html_invalid604 = f3.read()
	f3.close()

	f4 = open("./twisted_protocols/invalid401tw.html","r")
	all_the_html_invalid401 = f4.read()
	f4.close()

        if result == 602:
            request.write(all_the_html_invalid602)
        elif result == 604:
            request.write(all_the_html_invalid604)
        elif result == 401:
            request.write(all_the_html_invalid401)
        else:
            request.write(all_the_html_correct )
        request.finish()


        


    def onFoundPassword(self, result, request, username):
        address = result[0][0]
        password = result[0][1]
        log.msg('RESULT FROM SQL IS:\t', address, password)
        from sendMail import sendPasswordByEmail
        try:
            sendPasswordByEmail(address, password, username)     
        except Exception, e:
            log.msg(str(e))
        request.write(resultValue(1))
        request.finish()
    
    def UpdateVerson(self,request):
        if (request.args.has_key('lang') is False) or (request.args['lang'] == ['cn']):
            f = open("./common/updateinfo_cn.json", 'r')
        elif request.args['lang'] == ['en']:
            f = open("./common/updateinfo_en.json", 'r')
        elif request.args['lang'] == ['tw']:
            f = open("./common/updateinfo_tw.json", 'r')
        result = f.read()
        f.close()
        request.write(result)
        request.finish()
    
userPage = UserPage()

