from flask import Flask, jsonify, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import (
    ViberMessageRequest, ViberSubscribedRequest
)
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError


class MessageRequest(Schema):
    name = fields.Str(required=True)
    message = fields.Str(required=True)


message_schema = MessageRequest(strict=True)
vibersig = 'X-Viber-Content-Signature'

bot_configuration = BotConfiguration(
   name='Codes24',
   avatar='http://viber.com/avatar.jpg',
   auth_token='50e8d1281ca7e5c6-2e462af8e7fda68e-93203ff5ca380e61'
)
viber = Api(bot_configuration)
# viber.set_webhook('https://foobar/incoming')

app = Flask(__Codes24__)


@app.route('/send', methods=['POST'])
def send():
    res_json = request.get_json()

    try:
        result = message_schema.load(res_json)
    except ValidationError as err:
        return Response(jsonify({"errors": err.messages}), status=400)

    result = result.data
    message = TextMessage(text=result['message'])
    viber.send_messages(result['name'], [message])
    return Response(status=200)


@app.route('/incoming', methods=['POST'])
def incoming():
    if not viber.verify_signature(
            request.get_data(), request.headers.get(vibersig)):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        viber.send_messages(viber_request.sender.id, [
            message
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        print("received request. post data: {0}".format(request.get_data()))

    return Response(status=200)
