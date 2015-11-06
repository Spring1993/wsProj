from appException import *

'''''''''''''''''''''''''''''''''''''''''''''
1. check if adminpwd is correct
2. check if imei exists and simnum remain unchanged
3. check how many sosnumbers exists in stick
'''''''''''''''''''''''''''''''''''''''''''''

def checkAdminPwdSql(wsdbpool, imei, adminpwd):
    return wsdbpool.runInteraction(_checkAdminPwd, imei, adminpwd)

def _checkAdminPwd(txn, imei, adminpwd):
    txn.execute('select * from wsinfo where imei = %s and adminpwd = %s', (imei, adminpwd))
    if len(txn.fetchall()) == 0:
        raise PasswordErrorException
    return True

def updateAdminPwdSql(wsdbpool, imei, newpwd):
    return wsdbpool.runOperation('update wsinfo set adminpwd = %s where imei = %s', (newpwd, imei))

def checkImeiSimnumSql(wsdbpool, imei):
    return wsdbpool.runInteraction(_checkImeiSimnum, imei)

def _checkImeiSimnum(txn, imei):
    txn.execute('select simnum from wsinfo where imei = %s', (imei,))
    simnum = txn.fetchall()
    #assert simnum[0][0] == '10086', 'simnum shoule be 10086'
    if len(simnum) == 0:
        raise NoImeiException
    if simnum[0][0] in (0, '0'):
        raise SimnumChangedException
    return True
 
def checkSosnumberSql(wsdbpool, imei, number, oper):
    return wsdbpool.runInteraction(_checkSosnumber, imei, number, oper)

def _checkSosnumber(txn, imei, number, oper):
    MAXNUM = 3
    MINNUM = 1
    if oper == 'ADD':
        txn.execute('select * from sosnumber where imei = %s', (imei,))
        num = len(txn.fetchall())
        if num >= MAXNUM:
            raise StorageLimitException
        txn.execute('select * from sosnumber where imei = %s and sosnumber = %s', (imei, number))
        num = len(txn.fetchall())
        if num != 0:
            raise DuplicateSosnumberException
    txn.execute('select * from sosnumber where imei = %s', (imei,))
    num = len(txn.fetchall())
    if oper == 'DEL' and num <= MINNUM:
        raise NoSosnumberException
    return True

   


'''''''''''''''''''''''''''''''''''''''''''''
used to tell stick if stick received legal sosnumber operation request from sms
'''''''''''''''''''''''''''''''''''''''''''''

def insertTempSosSql(wsdbpool, imei, number, contact):
    return wsdbpool.runOperation('replace into temp_sos (imei, sosnumber, contact) values(%s, %s, %s)', (imei, number, contact))

def deleteTempSosSql(wsdbpool, imei, number):
    return wsdbpool.runOperation('delete from temp_sos where imei = %s and sosnumber = %s', (imei, number))




'''''''''''''''''''''''''''''''''''''''''''''
These operation will be executed when server received ack from stick
'''''''''''''''''''''''''''''''''''''''''''''

def insertSosNumberSql(wsdbpool, imei, number, contact):
    return wsdbpool.runOperation('replace into sosnumber (imei, sosnumber, contact) values(%s, %s, %s)', (imei, number, contact))

def deleteSosNumberSql(wsdbpool, imei, number=None):
    if number is None:
        return wsdbpool.runOperation('delete from sosnumber where imei = %s', (imei,))
    return wsdbpool.runOperation('delete from sosnumber where imei = %s and sosnumber = %s', (imei, number))

def selectSosNumberSql(wsdbpool, imei):
    return wsdbpool.runInteraction(_selectSosNumber, imei)

def _selectSosNumber(txn, imei):
    txn.execute('select * from sosnumber where imei = %s', (imei,))
    result = txn.fetchall()
    if len(result) == 0:
        raise NoSosnumberException
    return result




'''''''''''''''''''''''''''''''''''''''''''''
check if sosnumber have successfully added/deleted
'''''''''''''''''''''''''''''''''''''''''''''

def verifyOperSql(wsdbpool, imei, number, oper):
    return wsdbpool.runInteraction(_verifyOper, imei, number, oper)

def _verifyOper(txn, imei, number, oper):
    txn.execute('select * from sosnumber where sosnumber = %s', (number,))
    result = txn.fetchall()
    if oper == 'ADD' and len(result) == 1:
        return True
    if oper == 'DEL' and len(result) == 0:
        return True
    raise NoStickAckException




'''''''''''''''''''''''''''''''''''''''''''''
kepp sosnumbers in database sync with stick
'''''''''''''''''''''''''''''''''''''''''''''

def syncSosSql(wsdbpool, imei, numbersInStick):
    return wsdbpool.runInteraction(_syncSos, imei, numbersInStick)

def _syncSos(txn, imei, numbersInStick):
    numbersInDb = set()
    txn.execute('select sosnumber from sosnumber where imei = %s', (imei,))
    for r in txn.fetchall():
        numbersInDb.add(r[0])

    #number in database but not in stick, to be deleted
    for number in numbersInDb.difference(numbersInStick):
        txn.execute('delete from sosnumber where sosnumber = %s', (number,))
        txn.execute('delete from temp_sos where imei = %s and sosnumber = %s', (imei, number))

    #number in stick but not in database, to be added to table sosnumber
    for number in numbersInStick.difference(numbersInDb):
        txn.execute('select contact from temp_sos where imei = %s and sosnumber = %s', (imei, number))
        contact = txn.fetchall()
        if len(contact) == 0:
            contact = 'unnamed'
        else:
            contact = contact[0][0]
        txn.execute('replace into sosnumber (imei, sosnumber, contact) values(%s, %s, %s)', (imei, number, contact))
        txn.execute('delete from temp_sos where imei = %s and sosnumber = %s', (imei, number))


    return True
        


    



if __name__ == '__main__':
    def onResult(result):
        print result
        reactor.stop()

    def onError(error):
        try:
            print error.value.errCode
        except Exception:
            print error.value
        reactor.stop()

    from sqlPool import wsdbpool
    from twisted.internet import reactor, defer
    #insertTempSosSql(wsdbpool, 1027, '12345678901', 'name').addCallbacks(onResult, onError)
    stickset = set()
    stickset.add('12345678901')
    stickset.add('42345678901')

    checkImeiSimnumSql(wsdbpool, 98789).addCallbacks(onResult, onError)
    reactor.run()

