import os
from flask import request, abort, make_response, jsonify
from . import bot_bp as bot
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import InvalidSignatureError
from wsgi import app
from rdflib_sqlalchemy import registerplugins
from rdflib.store import Store
from rdflib import URIRef, Graph, plugin, Namespace, FOAF, RDFS
from rdflib.plugins.sparql import prepareQuery
from app import DB_URI

line_bot_api = LineBotApi(app.config.get('LINE_MESSAGE_API_ACCESS_TOKEN'))
handler = WebhookHandler(app.config.get('LINE_MESSAGE_API_CLIENT_SECRET'))

registerplugins()

identifier = URIRef('labtests')
store = plugin.get('SQLAlchemy', Store)(identifier=identifier, configuration=DB_URI)
graph = Graph(store, identifier=identifier)
graph.open(DB_URI)

labn = Namespace('http://mtclan.net/rdfs/labtests/')

FEMALE_ENDING = 'ค่ะ'

def insert_and(items):
    if len(items) > 1:
        items.insert(-1, 'และ')
    return items

@bot.route('/message')
def send_message():
    return 'Gotcha.'


@bot.route('/tests')
def get_tests_list():
    q = prepareQuery(
        'SELECT ?atest ?testname WHERE { ?atest a lab:Test . ?atest foaf:name ?testname .}',
        initNs={'lab': labn, 'foaf': FOAF}
    )
    data = []
    for row in graph.query(q):
        data.append({
            'test': row.atest,
            'name': row.testname
        })
    return jsonify(data)


@bot.route('/tests/info/<testname>')
def test_info(testname):
    q = prepareQuery(
        ('SELECT ?atest ?analname ?fastinfo WHERE '
        '{ ?atest lab:tests ?analyte .'
         '?analyte foaf:name ?analname .'
         '?atest lab:fasting ?fastinfo .}'),
        initNs={'foaf': FOAF, 'lab': labn}
    )
    test = labn[testname.upper()]
    data = []
    for row in graph.query(q, initBindings={'atest': test}):
        data.append({
            'test': row.atest,
            'test_code': testname.upper(),
            'analyte': row.analname,
            'preparation': {
                'fasting': row.fastinfo
            }
        })
    q = prepareQuery(
        'SELECT ?specimens ?label WHERE { ?atest lab:testWith ?specimens . ?specimens rdfs:label ?label}',
        initNs={'lab': labn}
    )
    specimens = []
    for row in graph.query(q, initBindings={'test': data[0]['test']}):
        specimens.append({
            'specimens': row.specimens,
            'label': row.label
        })
    data[0]['specimens'] = specimens
    return jsonify(data)

@bot.route('/message/callback', methods=['POST'])
def line_message_callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


def get_test_info_from_code(req):
    tcode = req.get('queryResult').get('parameters').get('tests')
    if not tcode:
        return None
    tests = []
    q = prepareQuery(
        ('SELECT ?atest ?testname ?tcode ?analname ?fastinfo WHERE '
         '{?atest lab:code ?tcode .'
         '?atest foaf:name ?testname .'
         '?atest lab:tests ?analyte .'
         '?analyte foaf:name ?analname .'
         '?atest lab:fasting ?fastinfo .}'),
        initNs={'foaf': FOAF, 'lab': labn}
    )
    data = []
    message = ''
    for row in graph.query(q, initBindings={'tcode': tcode}):
        message += '{} ({}) เป็นการตรวจหา {}'.format(row.testname, row.tcode, row.analname)
    '''
    q = prepareQuery(
        'SELECT ?specimens ?label WHERE { ?atest lab:testWith ?specimens . ?specimens rdfs:label ?label}',
        initNs={'lab': labn}
    )
    specimens = []
    for row in graph.query(q, initBindings={'test': data[0]['test']}):
        specimens.append({
            'specimens': row.specimens,
            'label': row.label
        })
    data[0]['specimens'] = specimens
    '''
    return message

def get_tests_for_risk(req):
    diseases = req.get('queryResult').get('parameters').get('diseases', '')
    specimens = req.get('queryResult').get('parameters').get('specimens', '')
    message = ''
    submessages = []
    for ds in graph.nodes.match('Disease', thname=diseases):
        for rel in graph.match((ds, ), r_type='SCREENED_BY'):
            submessage = ''
            test = rel.end_node
            print(test)
            if test['testgroup']:
                submessage += ' กลุ่ม {} ได้แก่ '.format(test['thname'])
                for rel in graph.match((test,), r_type='INCLUDES'):
                    submessage += '{} '.format(rel.end_node['thname'])
            else:
                submessage += '{} '.format(test['thname'])
            submessages.append(submessage)
    if submessages:
        submessages = ['การตรวจความเสี่ยง{} มีรายการตรวจ'.format(diseases)] + submessages
        message = ' '.join(submessages)
    return message


def get_risk_factors_of_diseases(req):
    parameter = req.get('queryResult').get('parameters').get('parameter', '')
    diseases = req.get('queryResult').get('parameters').get('diseases', '')
    age = req.get('queryResult').get('parameters').get('number-integer', 0)
    message = ''
    if diseases:
        factors = []
        for ds in graph.nodes.match('Disease', thname=diseases):
            for rel in graph.match((ds, ), r_type='ASSOCIATED_BY'):
                factors.append(rel.end_node['thname'])
        if factors:
            message = 'ปัจจัยเสี่ยงต่อ{} ได้แก่ {}'.format(diseases, ' '.join(insert_and(factors)))
        return message
    elif parameter:
        diseases = []
        for par in graph.nodes.match('Parameter', thname=parameter):
            for rel in graph.match((par, ), r_type='ASSOCIATES_WITH'):
                diseases.append(rel.end_node['thname'])
        if diseases:
            message = '{} เกี่ยวข้องกับ {}'.format(parameter, ' '.join(insert_and(diseases)))
        return message
    if age:
        diseases = []
        agenode = graph.nodes.match('Parameter', enname='age').first()
        if age > 65:
            for rel in graph.match((agenode, ), r_type='ASSOCIATES_WITH'):
                if rel['greater'] <= age:
                    diseases.append(rel.end_node['thname'])
        if diseases:
            message = 'อายุ {} เกี่ยวข้องกับ {}'.format(age, ' '.join(insert_and(diseases)))
        return message


def get_tests_for_concern(req):
    parameter = req.get('queryResult').get('parameters').get('parameter', '')
    diseases = req.get('queryResult').get('parameters').get('diseases', '')
    print('disease is {}'.format(diseases))
    age = req.get('queryResult').get('parameters').get('number-integer', 0)
    if not diseases:
        return None
    tests = []
    q = prepareQuery(
        ('SELECT ?testname ?tcode WHERE { ?a rdfs:label ?disease .'
         '?test lab:screenFor ?a .'
         '?test lab:code ?tcode .'
         '?test foaf:name ?testname .}')
        , initNs={'lab': labn, 'foaf': FOAF, 'rdfs': RDFS}
    )
    for row in graph.query(q, initBindings={'disease': diseases}):
        tests.append({
            'name': row.testname + " ({})".format(row.tcode)
        })
    instruction = 'กรุณาพิมพ์รหัสในวงเล็บสำหรับรายละเอียดของรายการตรวจ'
    message = 'ควรตรวจ {}\n{}'.format(' '.join([t['name'] for t in tests]), instruction)
    return message


@bot.route('/dialogflow/webhook', methods=['POST'])
def dialogflow_webhook():
    req = request.get_json(force=True)
    # fetch action from json
    action = req.get('queryResult').get('action')
    rsp_message = {'fulfillmentText': 'ขออภัยเราไม่สามารถให้ข้อมูลได้ค่ะ'}
    message = ''
    print(action)
    if action == 'get_test_info':
        message = get_test_info_from_code(req)
    if action == 'get_tests_for_concern':
        message = get_tests_for_concern(req)
    if action == 'get_tests_for_risk':
        message = get_tests_for_risk(req)
    if action == 'get_risk_factors_of_diseases':
        message = get_risk_factors_of_diseases(req)
    if action == 'get_min_fasting_time':
        analyte = req.get('queryResult').get('parameters').get('testname', '')
        specimens = req.get('queryResult').get('parameters').get('specimens', '')
        print('{}, {}'.format(analyte, specimens))
        for n in graph.nodes.match('Analyte', thname=analyte):
            if n['testgroup']:
                message += 'รายการตรวจในกลุ่ม {} ได้แก่ '.format(n['thname'])
                for rel in graph.match((n,), r_type='INCLUDES'):
                    message += '{} ควรงดอาหาร {} '.format(rel.end_node['thname'],
                                              rel.end_node['fast'])
                message = message.rstrip(',')
            else:
                message += 'ควรงดอาหารประมาณ {}'.format(n['fast'])
    if message:
        rsp_message['fulfillmentText'] = message + ' ' + FEMALE_ENDING
    return make_response(jsonify(rsp_message))
