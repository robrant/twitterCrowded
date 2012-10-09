'''
Created on Oct 7, 2012

@author: brantinghamr
'''

from bottle import route, run, template, request
import json

@route('/contribute', method='POST')
def postTest():
    
    requestData = request.body.read()
    requestData = json.loads(requestData)
    data = requestData['data']
    
    return json.dumps(data[0])

@route('/events', method='GET')
def getCrowdedEventsTest():

    data = {"meta": 200, "data": [{"start": "2012-10-07T13:41:07.734000", "objectId": "protest", "subType": "tag"}, {"start": "2012-10-07T13:44:42.044000", "objectId": "spain", "subType": "tag"}]}
    data = json.dumps(data)
    return data
    
    
run(host='localhost', port=8991)
