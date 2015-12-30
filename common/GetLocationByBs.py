# -*- coding:utf-8 -*-
import urllib2, urllib
from eviltransform import gcj2wgs_exact

request = urllib2.Request('http://apilocate.amap.com/position')
#secret key of gaode map service
AMAP_SERVICE_KEY = '56f2c85f19dbfae6269363d64d688173'


def getLocationByBsinfo(mcc, mnc, imei, imsi, lac, cid, signal, timestamp):
    paramsDict = dict()
    paramsDict['accesstype'] = '0'
    paramsDict['key'] = AMAP_SERVICE_KEY
    paramsDict['output'] = 'json'
    paramsDict['imei'] = str(imei)
    paramsDict['imsi'] = str(imsi)
    paramsDict['bts'] = ','.join((str(mcc), str(mnc), str(lac), str(cid), str(signal)))
    params = urllib.urlencode(paramsDict)
    request.add_data(params)
    for i in range(3):
        try:
            locations = urllib2.urlopen(request).read()
            locations = eval(locations)['result']['location'].split(',')
            result = gcj2wgs_exact(float(locations[1]), float(locations[0]))
            latlog = str(result[1])+','+str(result[0])
        except Exception as e:
            latlog = '0,0'
        else:
            break
    return latlog

if __name__ == '__main__':
    print getLocationByBsinfo(460, 00, 868986022055835,460002606774197,93659,5013,-93,20151218074832)

