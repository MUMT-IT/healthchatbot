import requests
from flask import request, abort
from . import bot_bp as bot
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import InvalidSignatureError
from wsgi import app

line_bot_api = LineBotApi(app.config.get('LINE_MESSAGE_API_ACCESS_TOKEN'))
handler = WebhookHandler(app.config.get('LINE_MESSAGE_API_CLIENT_SECRET'))


@bot.route('/message')
def send_message():
    return 'Gotcha.'


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
