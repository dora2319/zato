# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

MESSAGE = Bunch()
MESSAGE.MESSAGE_TYPE_LENGTH = 4
MESSAGE.TOKEN_LENGTH = 32
MESSAGE.TOKEN_START = MESSAGE.MESSAGE_TYPE_LENGTH
MESSAGE.TOKEN_END = MESSAGE.MESSAGE_TYPE_LENGTH + MESSAGE.TOKEN_LENGTH
MESSAGE.PAYLOAD_START = MESSAGE.MESSAGE_TYPE_LENGTH + MESSAGE.TOKEN_LENGTH
MESSAGE.NULL_TOKEN = '0' * MESSAGE.TOKEN_LENGTH

MESSAGE_TYPE = Bunch()
MESSAGE_TYPE.TO_SINGLETON = b'0000'
MESSAGE_TYPE.TO_PARALLEL_PULL = b'0001'
MESSAGE_TYPE.TO_PARALLEL_SUB = b'0002'

MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_SUB = b'0003'
MESSAGE_TYPE.TO_AMQP_CONSUMING_CONNECTOR_PULL = b'0004'
MESSAGE_TYPE.TO_AMQP_CONNECTOR_SUB = b'0005'

MESSAGE_TYPE.TO_JMS_WMQ_PUBLISHING_CONNECTOR_SUB = b'0006'
MESSAGE_TYPE.TO_JMS_WMQ_CONSUMING_CONNECTOR_PULL = b'0007'
MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_SUB = b'0008'

MESSAGE_TYPE.TO_ZMQ_PUBLISHING_CONNECTOR_SUB = b'0009'
MESSAGE_TYPE.TO_ZMQ_CONSUMING_CONNECTOR_PULL = b'0010'
MESSAGE_TYPE.TO_ZMQ_CONNECTOR_SUB = b'0011'

MESSAGE_TYPE.USER_DEFINED_START = b'5000'

SCHEDULER = Bunch()
SCHEDULER.CREATE = b'10000'
SCHEDULER.EDIT = b'10001'
SCHEDULER.DELETE = b'10002'
SCHEDULER.EXECUTE = b'10003'
SCHEDULER.JOB_EXECUTED = b'10004'

ZMQ_SOCKET = Bunch()
ZMQ_SOCKET.CLOSE = b'10100'

SECURITY = Bunch()
DEFINITION = Bunch()
OUTGOING = Bunch()
CHANNEL = Bunch()

SECURITY.BASIC_AUTH_CREATE = b'10200'
SECURITY.BASIC_AUTH_EDIT = b'10201'
SECURITY.BASIC_AUTH_DELETE = b'10202'
SECURITY.BASIC_AUTH_CHANGE_PASSWORD = b'10203'

SECURITY.TECH_ACC_CREATE = b'10300'
SECURITY.TECH_ACC_EDIT = b'10301'
SECURITY.TECH_ACC_DELETE = b'10302'
SECURITY.TECH_ACC_CHANGE_PASSWORD = b'10303'

SECURITY.WSS_CREATE = b'10400'
SECURITY.WSS_EDIT = b'10401'
SECURITY.WSS_DELETE = b'10402'
SECURITY.WSS_CHANGE_PASSWORD = b'10403'

DEFINITION.AMQP_CREATE = b'10500'
DEFINITION.AMQP_EDIT = b'10501'
DEFINITION.AMQP_DELETE = b'10502'
DEFINITION.AMQP_CHANGE_PASSWORD = b'10503'

DEFINITION.JMS_WMQ_CREATE = b'10504'
DEFINITION.JMS_WMQ_EDIT = b'10505'
DEFINITION.JMS_WMQ_DELETE = b'10506'

DEFINITION.ZMQ_CREATE = b'10507'
DEFINITION.ZMQ_EDIT = b'10508'
DEFINITION.ZMQ_DELETE = b'10509'

OUTGOING.AMQP_CREATE = b'10600'
OUTGOING.AMQP_EDIT = b'10601'
OUTGOING.AMQP_DELETE = b'10602'
OUTGOING.AMQP_PUBLISH = b'10603'

OUTGOING.JMS_WMQ_CREATE = b'10604'
OUTGOING.JMS_WMQ_EDIT = b'10605'
OUTGOING.JMS_WMQ_DELETE = b'10606'
OUTGOING.JMS_WMQ_SEND = b'10607'

OUTGOING.ZMQ_CREATE = b'10608'
OUTGOING.ZMQ_EDIT = b'10609'
OUTGOING.ZMQ_DELETE = b'10610'
OUTGOING.ZMQ_SEND = b'10611'

OUTGOING.SQL_CREATE_EDIT = b'10612' # Same for creating and updating the pools
OUTGOING.SQL_CHANGE_PASSWORD = b'10613'
OUTGOING.SQL_DELETE = b'10614'

OUTGOING.HTTP_SOAP_CREATE_EDIT = b'10615' # Same for creating and updating
OUTGOING.HTTP_SOAP_DELETE = b'10616'

OUTGOING.FTP_CREATE_EDIT = b'10617' # Same for creating and updating
OUTGOING.FTP_DELETE = b'10618'
OUTGOING.FTP_CHANGE_PASSWORD = b'10619'

CHANNEL.AMQP_CREATE = b'10700'
CHANNEL.AMQP_EDIT = b'10701'
CHANNEL.AMQP_DELETE = b'10702'
CHANNEL.AMQP_MESSAGE_RECEIVED = b'10703'

CHANNEL.JMS_WMQ_CREATE = b'10704'
CHANNEL.JMS_WMQ_EDIT = b'10705'
CHANNEL.JMS_WMQ_DELETE = b'10706'
CHANNEL.JMS_WMQ_MESSAGE_RECEIVED = b'10707'

CHANNEL.ZMQ_CREATE = b'10708'
CHANNEL.ZMQ_EDIT = b'10709'
CHANNEL.ZMQ_DELETE = b'10710'
CHANNEL.ZMQ_MESSAGE_RECEIVED = b'10711'

CHANNEL.HTTP_SOAP_CREATE_EDIT = b'10712' # Same for creating and updating
CHANNEL.HTTP_SOAP_DELETE = b'10713'

AMQP_CONNECTOR = Bunch()
AMQP_CONNECTOR.CLOSE = b'10801'

JMS_WMQ_CONNECTOR = Bunch()
JMS_WMQ_CONNECTOR.CLOSE = b'10802'

ZMQ_CONNECTOR = Bunch()
ZMQ_CONNECTOR.CLOSE = b'10803'

SERVICE = Bunch()
SERVICE.EDIT = b'10900'
SERVICE.DELETE = b'10901'
SERVICE.SET_REQUEST_RESPONSE = b'10902'

code_to_name = {}

# To prevent 'RuntimeError: dictionary changed size during iteration'
bunch_name, bunch = None, None

for bunch_name, bunch in globals().items():
    if isinstance(bunch, Bunch) and not bunch is Bunch:
        if bunch not in(MESSAGE, MESSAGE_TYPE):
            for code_name, code_value in bunch.items():
                code_name = bunch_name + '_' + code_name
                code_to_name[code_value] = code_name
                
del bunch_name, bunch, code_name, code_value