import os

from flask import request, abort, make_response, jsonify
from linebot.models import (MessageAction, BoxComponent,
                            BubbleContainer, TextComponent,
                            ButtonComponent, FlexSendMessage, CarouselContainer)

from . import bot_bp as bot
from .models import UnfulfilledMessage
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import InvalidSignatureError
from rdflib_sqlalchemy import registerplugins
from rdflib.store import Store
from rdflib import URIRef, Graph, plugin, Namespace, FOAF, RDFS, Literal
from rdflib.plugins.sparql import prepareQuery
from app import DB_URI, db
from pytz import timezone
from datetime import datetime

bkk = timezone('Asia/Bangkok')
line_bot_api = LineBotApi(os.environ.get('LINE_MESSAGE_API_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_MESSAGE_API_CLIENT_SECRET'))

registerplugins()

identifier = URIRef('labtests')
store = plugin.get('SQLAlchemy', Store)(identifier=identifier, configuration=DB_URI)
graph = Graph(store, identifier=identifier)
graph.open(DB_URI)

labn = Namespace('http://mtclan.net/rdfs/labtests/')
ns2 = Namespace('http://mtclan.net/rdfs/riskfactors/')

FEMALE_ENDING = 'ค่ะ'


def join_and(alist, sep=',', conj='และ'):
    text = ''
    for i in range(len(alist)):
        text += alist[i]
        if i != len(alist) - 2:
            if i != len(alist) - 1:
                text += sep
        else:
            text += conj
    return text


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
    q = prepareQuery(('SELECT ?atest ?analname ?fastinfo WHERE {'
                      '?analyte foaf:name ?analname .'
                      '?atest lab:tests ?analyte .'
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


def get_self_prep_from_test_code(req):
    tcode = req.get('queryResult').get('parameters').get('tests')
    if not tcode:
        return None
    q = prepareQuery(
        ('SELECT ?atest ?tcode ?fastinfo WHERE '
         '{?atest lab:code ?tcode .'
         '?atest lab:fasting ?fastinfo .'
         '}'),
        initNs={'lab': labn}
    )
    message = 'การเตรียมตัวเพื่อการตรวจควรปฏิบัติดังนี้'
    for row in graph.query(q, initBindings={'tcode': tcode}):
        message += ' ' + row.fastinfo
    return message


def get_test_info_from_code(req):
    tcode = req.get('queryResult').get('parameters').get('tests')
    if not tcode:
        return None
    tests = []
    q = prepareQuery(
        ('SELECT ?atest ?testname ?tcode ?analname ?fastinfo WHERE {'
         '?analyte rdfs:label ?analname .'
         '?atest lab:tests ?analyte .'
         '?atest lab:code ?tcode .'
         '?atest foaf:name ?testname .'
         '?atest lab:fasting ?fastinfo .'
         'FILTER (lang(?analname) = "th")'
         '}'),
        initNs={'foaf': FOAF, 'lab': labn}
    )
    data = []
    message = ''
    for row in graph.query(q, initBindings={'tcode': tcode}):
        data.append({
            'test': row.atest,
            'testname': row.testname,
            'tcode': row.tcode,
            'analname': row.analname
        })

    for t in data:
        q = prepareQuery(
            'SELECT ?specimens ?label WHERE {'
            '?atest lab:code ?tcode .'
            '?atest lab:testWith ?specimens .'
            '?specimens rdfs:label ?label}',
            initNs={'lab': labn}
        )
        specimens = []
        for row in graph.query(q, initBindings={'tcode': tcode}):
            specimens.append(row.label)
        t['specimens'] = specimens
    for t in data:
        message += '{} ({}) เป็นการตรวจ{} ใน{}' \
            .format(t['testname'], t['tcode'], t['analname'], ' '.join(t['specimens']))
    message += ' ต้องการทราบรายละเอียดเกี่ยวกับเตรียมตัวก่อนการตรวจไหมคะ'
    return message


def get_tests_for_concern(req):
    diseases = req.get('queryResult').get('parameters').get('diseases', '')
    print('disease is {}'.format(diseases))
    if not diseases:
        return None
    tests = []
    q = prepareQuery(
        ('SELECT ?testname ?tcode WHERE { ?a rdfs:label ?disease .'
         '?test lab:screenFor ?a .'
         '?test lab:code ?tcode .'
         '?test rdfs:label ?testname .}')
        , initNs={'lab': labn, 'foaf': FOAF, 'rdfs': RDFS}
    )
    for row in graph.query(q, initBindings={'disease': diseases}):
        print(row.testname)
        tests.append({
            'name': row.testname,
            'code': row.tcode
        })
    instruction = 'กรุณาพิมพ์รหัสในวงเล็บสำหรับรายละเอียดของรายการตรวจ'
    message = 'ควรตรวจ {} {}'.format(join_and([t['name'] for t in tests], sep=" "), instruction)
    bubbles = []
    for t in tests:
        bubbles.append(
            BubbleContainer(
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text=u'{}'.format(t['name']),
                            weight='bold',
                            size='xl',
                            gravity='center',
                            align='center',
                        )
                    ]
                ),
                footer=BoxComponent(
                    layout='vertical',
                    contents=[
                        ButtonComponent(
                            action=MessageAction(
                                label='detail',
                                text=u'{}'.format(t['code'])
                            )
                        )
                    ]
                )
            )
        )

    return bubbles


def get_risk_disease_by_age(req):
    age = req.get('queryResult').get('parameters').get('age')
    if age is None:
        return None
    print(age)
    q = prepareQuery(('SELECT ?disease ?name WHERE { '
                      '?disease rdfs:label ?name .'
                      '?disease lab:startRiskAge ?age .'
                      'FILTER (?a >= ?age)'
                      '}'),
                     initNs={'lab': labn, 'rdfs': RDFS})
    message = 'ในช่วงวัยของคุณอาจมีความเสี่ยงต่อ'
    found = False
    for row in graph.query(q, initBindings={'a': Literal(int(age))}):
        message += '{} '.format(row.name)
        found = True
    if not found:
        message = 'ไม่พบโรคที่มีความเสี่ยงในช่วงวัยของคุณ ทั้งนี้กรุณาปรึกษานักเทคนิคการแพทย์หรือสอบถามเราเกี่ยวกับความเสี่ยงของโรคที่เกิดจากปัจจัยอื่น'
    return message


def get_self_preparation(req):
    checkup = req.get('queryResult').get('parameters').get('checkups')
    params = req.get('queryResult').get('parameters').get('parameter')
    analyte = req.get('queryResult').get('parameters').get('analytes')
    interfs = set()
    if checkup and params:
        tests = set()
        q = prepareQuery((
            'SELECT ?testname ?interferance WHERE {'
            '?checkup rdfs:label ?label .'
            '?checkup lab:requires ?specimens .'
            '?test lab:testWith ?specimens .'
            '?test rdfs:label ?testname .'
            '?test lab:interferedBy ?interferance .'
            '?interferance rdfs:label ?param'
            '}'
        ), initNs={'lab': labn, 'rdfs': RDFS})

        for param in params:
            for row in graph.query(q, initBindings={'label': checkup, 'param': param}):
                tests.add(row.testname)
                interfs.add(param)
        if tests:
            message = '{}อาจรบกวนผลการตรวจได้แก่'.format(join_and(list(interfs), sep=' '))
            return message + join_and(list(tests), sep=' ')
        else:
            return 'ไม่พบรายงานว่า{}รบกวนการตรวจ'.format(join_and(params, sep=' '))
    return None


def get_disease_from_risk_factor(req):
    factor = req.get('queryResult').get('parameters').get('risk-factor')
    q = prepareQuery((
        'SELECT ?disname WHERE {'
        '?factor rdfs:label ?factorname .'
        '?factor ns2:causes ?disease .'
        '?disease rdfs:label ?disname .'
        'FILTER (LANG(?disname) = "th")'
        '}'
    ), initNs={'rdfs': RDFS, 'ns2': ns2})
    diseases = []
    message = ''
    for row in graph.query(q, initBindings={'?factorname': factor}):
        diseases.append(row.disname)
    if diseases:
        message = 'คุณมีความเสี่ยงต่อโรค'
        message += join_and(diseases, sep=' ')
    return message


def get_reference_value(req):
    analyte = req.get('queryResult').get('parameters').get('analytes')
    specimens = req.get('queryResult').get('parameters').get('specimens')
    q = prepareQuery((
        'SELECT ?hival ?lowval ?tname ?unit WHERE {'
        '?specimens rdfs:label ?slabel .'
        '?test lab:testWith ?specimens .'
        '?analyte rdfs:label ?alabel .'
        '?test lab:tests ?analyte .'
        '?test rdfs:label ?tname .'
        '?test lab:normalHi ?hival .'
        '?test lab:normalLow ?lowval .'
        '?test lab:unit ?unit .'
        '}'), initNs={'lab': labn, 'rdfs': RDFS})
    tests = []
    for row in graph.query(q, initBindings={'slabel': specimens, 'alabel': analyte}):
        tests.append({
            'name': row.tname,
            'hi': row.hival,
            'low': row.lowval,
            'unit': row.unit
        })

    if not tests:
        return None

    message = 'ค่าปกติของการตรวจหา{}ใน{}จากการตรวจ'.format(analyte, specimens)
    for t in tests:
        message += '{}คือ {} - {} {} '.format(t['name'], t['low'], t['hi'], t['unit'])
    return message


def get_lab_result_interpretation(req):
    value = req.get('queryResult').get('parameters').get('number')
    disease = req.get('queryResult').get('parameters').get('diseases')
    analyte = req.get('queryResult').get('parameters').get('analytes')
    specimens = req.get('queryResult').get('parameters').get('specimens')
    if value and disease and analyte and specimens:
        q = prepareQuery((
            'SELECT ?ctvalue ?ctside ?disname WHERE {'
            '?analyte rdfs:label ?analabel .'
            '?specimens rdfs:label ?splabel .'
            '?test lab:tests ?analyte .'
            '?test lab:testWith ?specimens .'
            '?ct lab:atest ?test .'
            '?ct lab:cutoff ?ctvalue .'
            '?ct lab:side ?ctside .'
            '?condition lab:indicatedBy ?ct .'
            '?condition ns2:causes ?disease .'
            '?disease rdfs:label ?disname .'
            '}'
        ), initNs={'ns2': ns2, 'lab': labn, 'rdfs': RDFS})

        diseases = set()
        for row in graph.query(q, initBindings={'analabel': analyte,
                                                'splabel': specimens,
                                                'disname': disease}):
            if row.ctside == Literal('right'):
                if Literal(value) >= row.ctvalue:
                    diseases.add(row.disname)
            elif row.ctside == Literal('left'):
                if Literal(value) <= row.ctvalue:
                    diseases.add(row.disname)

        if not diseases:
            return 'ไม่มีความเสี่ยง'
        return 'คุณมีความเสี่ยงเป็น' + disease

    if value and analyte and specimens:
        q = prepareQuery((
            'SELECT ?ctvalue ?ctside ?disname ?hi ?low ?unit WHERE {'
            '?analyte rdfs:label ?analabel .'
            '?test lab:tests ?analyte .'
            '?specimens rdfs:label ?splabel .'
            '?test lab:testWith ?specimens .'
            '?test lab:normalHi ?hi .'
            '?test lab:normalLow ?low .'
            '?test lab:unit ?unit .'
            '?ct lab:atest ?test .'
            '?ct lab:cutoff ?ctvalue .'
            '?ct lab:side ?ctside .'
            '?condition lab:indicatedBy ?ct .'
            '?condition ns2:causes ?disease .'
            '?disease rdfs:label ?disname .'
            '}'
        ), initNs={'ns2': ns2, 'lab': labn, 'rdfs': RDFS})

        message = ''
        diseases = set()
        for row in graph.query(q, initBindings={'analabel': analyte, 'splabel': specimens}):
            if row.ctside == Literal('right'):
                if Literal(value) >= row.ctvalue:
                    if row.low == Literal(0) or row.low == Literal(0.0):
                        row.low = 'น้อยกว่า '
                    else:
                        row.low = row.low + '-'
                    diseases.add((row.disname, row.hi, row.low, row.unit))
            elif row.ctside == Literal('left'):
                if Literal(value) <= row.ctvalue:
                    diseases.add((row.disname, row.hi, row.low, row.unit))

        message += join_and(['{} (ค่าปกติคือ {}{} {})'.format(d[0], d[2], d[1], d[3]) for d in diseases], sep=' ')
        if not message:
            return 'ไม่มีความเสี่ยง'
        return 'คุณมีความเสี่ยงเป็น' + message + ' ทั้งนี้ควรปรึกษานักเทคนิคการแพทย์เพิ่มเติมเพื่อตรวจยืนยันผล'


@bot.route('/dialogflow/webhook', methods=['POST'])
def dialogflow_webhook():
    req = request.get_json(force=True)
    intent = req["queryResult"]["intent"]["displayName"]
    text = req['originalDetectIntentRequest']['payload']['data']['message']['text']
    reply_token = req['originalDetectIntentRequest']['payload']['data']['replyToken']
    id = req['originalDetectIntentRequest']['payload']['data']['source']['userId']

    # print('id = ' + id)
    # print('text = ' + text)
    # print('intent = ' + intent)
    # print('reply_token = ' + reply_token)
    # fetch action from json
    action = req.get('queryResult').get('action')
    rsp_message = {'fulfillmentText': f'{action}: เรายังไม่สามารถให้ข้อมูลในประเด็นนี้ได้ค่ะ'}
    message = ''
    if action == 'get_test_info':
        message = get_test_info_from_code(req)
    elif action == 'get_self_prep_from_test':
        message = get_self_prep_from_test_code(req)
    elif action == 'get_tests_for_concern':
        message = get_tests_for_concern(req)
        if message:
            return line_bot_api.reply_message(reply_token=reply_token,
                                              messages=FlexSendMessage(
                                                  alt_text='Recommended Tests',
                                                  contents=CarouselContainer(contents=message)
                                              ))
    elif action == 'get_risk_disease_by_age':
        message = get_risk_disease_by_age(req)
    elif action == 'self-preparation':
        message = get_self_preparation(req)
    elif action == 'get_disease_from_risk_factor':
        message = get_disease_from_risk_factor(req)
    elif action == 'get_reference_value':
        message = get_reference_value(req)
    elif action == 'get_lab_result_interpretation':
        message = get_lab_result_interpretation(req)
    else:
        unfulfilled_msg = UnfulfilledMessage(
            line_id=id,
            message=text.lower(),
            action=action,
            created_at=bkk.localize(datetime.now())
        )
        db.session.add(unfulfilled_msg)
        db.session.commit()

    if message:
        if not message.endswith('คะ'):
            message += FEMALE_ENDING
        rsp_message['fulfillmentText'] = f'{action}: {message}'

    return make_response(jsonify(rsp_message))
