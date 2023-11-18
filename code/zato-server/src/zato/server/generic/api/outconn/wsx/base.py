# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep as _gevent_sleep

# Zato
from zato.common.api import DATA_FORMAT, GENERIC as COMMON_GENERIC, WEB_SOCKET, ZATO_NONE
from zato.common.typing_ import cast_
from zato.server.connection.queue import Wrapper
from zato.server.generic.api.outconn.wsx.client_generic import _NonZatoWSXClient
from zato.server.generic.api.outconn.wsx.client_zato import ZatoWSXClient
from zato.server.generic.api.outconn.wsx.common import OnClosed, OnConnected, OnMessageReceived

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, callable_, strdict, strlist, strnone
    from zato.common.wsx_client import MessageFromServer
    from zato.server.base.parallel import ParallelServer
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_json = DATA_FORMAT.JSON
msg_closing_superfluous = 'Closing superfluous connection (Zato queue)'

# ################################################################################################################################
# ################################################################################################################################

class WSXClient:
    """ A client through which outgoing WebSocket messages can be sent.
    """
    send: 'callable_'
    invoke: 'callable_'
    is_zato: 'bool'
    impl: 'ZatoWSXClient | _NonZatoWSXClient'

    def __init__(self, server:'ParallelServer', config:'strdict') -> 'None':
        self.server = server
        self.config = config
        self.is_zato = self.config['is_zato']
        self.impl = cast_('any_', None)

    def _init(self) -> 'None':

        # Decide which implementation class to use ..
        if self.is_zato:
            _impl_class = ZatoWSXClient
        else:
            _impl_class = _NonZatoWSXClient

        # .. this will create an instance ..
        self.impl = _impl_class(
            self.server,
            self.config,
            self.on_connected_cb,
            self.on_message_cb,
            self.on_close_cb
        )

        # .. this will initialize it ..
        _ = self.impl.init()

        # .. so now, we can make use of what was possibly initialized in .init above ..
        self.send   = self.impl.send
        self.invoke = self.send

        # .. additional features of the Zato client ..
        if _impl_class is ZatoWSXClient:
            self.invoke_service = self.impl._zato_client.invoke_service # type: ignore

        # .. now, the client can connect ..
        _ = self.impl.connect()

        # .. and run forever.
        _ = self.impl.run_forever()

# ################################################################################################################################

    def init(self) -> 'None':

        # Keep trying until our underlying client is connected ..
        while not self.is_impl_connected():

            # .. but stop if the client should not try again, e.g. it has been already deleted ..
            if self.impl and (not self.impl.should_keep_running()):
                return

            # .. if we are here, it means that we keep trying ..
            else:

                # .. do try to connect ..
                self._init()

                # .. sleep for a while after the attempt.
                _gevent_sleep(1)

    def on_connected_cb(self, conn:'OutconnWSXWrapper') -> 'None':
        self.config['parent'].on_connected_cb(conn)

# ################################################################################################################################

    def on_message_cb(self, msg:'MessageFromServer') -> 'None':
        self.config['parent'].on_message_cb(msg)

# ################################################################################################################################

    def on_close_cb(self, code:'int', reason:'strnone'=None) -> 'None':
        self.config['parent'].on_close_cb(code, reason)

# ################################################################################################################################

    def delete(self, reason:'str'='') -> 'None':
        if self.impl:
            self.impl.delete()
            self.impl.close(reason=reason) # type: ignore

# ################################################################################################################################

    def is_impl_connected(self) -> 'bool':
        return self.impl and self.impl.check_is_connected()

# ################################################################################################################################

    def get_name(self) -> 'str':
        return f'{self.config["name"]} - {self.config["type_"]} - {hex(id(self))}'

# ################################################################################################################################
# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    has_delete_reasons = True
    supports_reconnections = True

    on_connect_service_name:'str' = ''
    on_message_service_name:'str' = ''
    on_close_service_name:'str'   = ''
    on_subscribe_service_name:'str' = ''

    is_on_connect_service_wsx_adapter:'bool'   = False
    is_on_message_service_wsx_adapter:'bool'   = False
    is_on_close_service_wsx_adapter:'bool'     = False
    is_on_subscribe_service_wsx_adapter:'bool' = False

    def __init__(self, config:'strdict', server:'ParallelServer') -> 'None':

        # .. these used to be optional which is why we need ..
        # .. to ensure that we have this information here ..

        if not 'ping_internval' in config:
            config['ping_interval'] = WEB_SOCKET.DEFAULT.PING_INTERVAL

        if not 'pings_missed_threshold' in config:
            config['pings_missed_threshold'] = WEB_SOCKET.DEFAULT.PINGS_MISSED_THRESHOLD_OUTGOING

        config['parent'] = self
        self._has_json = config.get('data_format') == _json
        self._resolve_config_ids(config, server)
        super(OutconnWSXWrapper, self).__init__(cast_('Bunch', config), COMMON_GENERIC.ConnName.OutconnWSX, server)

# ################################################################################################################################

    def check_is_active(self) -> 'bool':
        is_active = self.server.is_active_outconn_wsx(self.config['id'])
        return is_active

# ################################################################################################################################

    def on_outconn_stopped_running(self) -> 'None':
        self.server.on_wsx_outconn_stopped_running(self.config['id'])

# ################################################################################################################################

    def on_outconn_connected(self) -> 'None':
        self.server.on_wsx_outconn_connected(self.config['id'])

# ################################################################################################################################

    def _resolve_config_ids(self, config:'strdict', server:'ParallelServer') -> 'None':

        on_connect_service_id   = config.get('on_connect_service_id',   0) # type: int
        on_message_service_id   = config.get('on_message_service_id',   0) # type: int
        on_close_service_id     = config.get('on_close_service_id',     0) # type: int
        on_subscribe_service_id = config.get('on_subscribe_service_id', 0) # type: int

        on_connect_service_name   = config.get('on_connect_service_name',   '') # type: str
        on_message_service_name   = config.get('on_message_service_name',   '') # type: str
        on_close_service_name     = config.get('on_close_service_name',     '') # type: str
        on_subscribe_service_name = config.get('on_subscribe_service_name', '') # type: str

        #
        # Connect service
        #
        if not on_connect_service_name:
            if on_connect_service_id:
                on_connect_service_name = server.api_service_store_get_service_name_by_id(on_connect_service_id)

        if on_connect_service_name:
            self.on_connect_service_name = on_connect_service_name
            self.is_on_connect_service_wsx_adapter = server.is_service_wsx_adapter(self.on_connect_service_name)
            config['on_connect_service_name'] = self.on_connect_service_name

        #
        # On message service
        #
        if not on_message_service_name:
            if on_message_service_id:
                on_message_service_name = server.api_service_store_get_service_name_by_id(on_message_service_id)

        if on_message_service_name:
            self.on_message_service_name = on_message_service_name
            self.is_on_message_service_wsx_adapter = server.is_service_wsx_adapter(self.on_message_service_name)
            config['on_message_service_name'] = self.on_message_service_name

        #
        # OnClosed service
        #
        if not on_close_service_name:
            if on_close_service_id:
                on_close_service_name = server.api_service_store_get_service_name_by_id(on_close_service_id)

        if on_close_service_name:
            self.on_close_service_name = on_close_service_name
            self.is_on_close_service_wsx_adapter = server.is_service_wsx_adapter(self.on_close_service_name)
            config['on_close_service_name'] = self.on_close_service_name

        #
        # Subscribe service
        #
        if not on_subscribe_service_name:
            if on_subscribe_service_id:
                on_subscribe_service_name = server.api_service_store_get_service_name_by_id(on_subscribe_service_id)

        if on_subscribe_service_name:
            self.on_subscribe_service_name = on_subscribe_service_name
            self.is_on_subscribe_service_wsx_adapter = server.is_service_wsx_adapter(self.on_subscribe_service_name)
            config['on_subscribe_service_name'] = self.on_subscribe_service_name

        if config.get('security_def'):
            if config['security_def'] != ZATO_NONE:
                _ignored_sec_type, sec_def_id = config['security_def'].split('/')
                sec_def_id = int(sec_def_id)
                sec_def_config = server.api_worker_store_basic_auth_get_by_id(sec_def_id)

                if sec_def_config:
                    config['username'] = sec_def_config['username']
                    config['secret'] = sec_def_config['password']

# ################################################################################################################################

    def on_subscribe_cb(self, service_name:'str') -> 'strlist':

        # Our response to produce
        out:'strlist' = []

        # Invoke the service that will produce a list of topics to subscribe to
        response = self.server.invoke(service_name)

        # If there was any response, make sure our caller receives it
        if response:
            out.extend(response)

        # Finally, return the result to the caller
        return out

# ################################################################################################################################

    def on_connected_cb(self, conn:'OutconnWSXWrapper') -> 'None':

        if self.on_connect_service_name:
            try:
                ctx = OnConnected(self.config, conn)
                if self.is_on_connect_service_wsx_adapter:
                    self.server.invoke_wsx_adapter(self.on_connect_service_name, ctx)
                else:
                    self.server.invoke(self.on_connect_service_name, ctx)
            except Exception:
                logger.warning('Could not invoke CONNECT service `%s`, e:`%s`', self.on_connect_service_name, format_exc())

# ################################################################################################################################

    def on_message_cb(self, msg:'bytes | MessageFromServer') -> 'None':

        if self.on_message_service_name:
            try:
                if self._has_json and isinstance(msg, bytes):
                    msg = msg.decode('utf8') # type: ignore
                    msg = loads(msg) # type: ignore
                ctx = OnMessageReceived(cast_('strdict | MessageFromServer', msg), self.config, self)
                if self.is_on_message_service_wsx_adapter:
                    self.server.invoke_wsx_adapter(self.on_message_service_name, ctx)
                else:
                    self.server.invoke(self.on_message_service_name, ctx)
            except Exception:
                logger.warning('Could not invoke MESSAGE service `%s`, e:`%s`', self.on_message_service_name, format_exc())

# ################################################################################################################################

    def _should_handle_close_cb(self, _ignored_code:'int', reason:'strnone') -> 'bool':

        if reason not in (ZATO_NONE, msg_closing_superfluous):
            if not self.delete_requested:
                return True

        # Return False by default
        return False

# ################################################################################################################################

    def on_close_cb(self, code:'int', reason:'strnone'=None) -> 'None':

        # We need to special-case the situation when it is us who deleted the outgoing connection.
        reason_is_not_delete = reason != COMMON_GENERIC.DeleteReasonBytes

        # Ignore events we generated ourselves, e.g. when someone edits a connection in web-admin
        # this will result in deleting and rerecreating a connection which implicitly calls this callback.
        if self._should_handle_close_cb(code, reason):

            # If reason is something else than our deleting the connection, we can log this message
            # to indicate that it must have been the remote server that did it.
            if reason_is_not_delete:
                logger.info('Remote server closed connection to WebSocket `%s`, c:`%s`, r:`%s`',
                    self.config['name'], code, reason)

            if self.on_close_service_name:
                try:
                    ctx = OnClosed(code, reason, self.config, self)
                    if self.is_on_close_service_wsx_adapter:
                        self.server.invoke_wsx_adapter(self.on_close_service_name, ctx)
                    else:
                        self.server.invoke(self.on_close_service_name, ctx)
                except Exception:
                    logger.warning('Could not invoke CLOSE service `%s`, e:`%s`', self.on_close_service_name, format_exc())

            has_auto_reconnect = self.config.get('has_auto_reconnect', True)

            if has_auto_reconnect:
                try:

                    # Reconnect only if it was not us who deleted the connection ..
                    if reason_is_not_delete:

                        # .. log what we are about to do ..
                        logger.info('WebSocket `%s` will reconnect to `%s` (hac:%d)',
                            self.config['name'], self.config['address'], has_auto_reconnect)

                        # .. and do reconnect now.
                        self.server.api_worker_store_reconnect_generic(self.config['id'])

                except Exception:
                    logger.warning('Could not reconnect WebSocket `%s` to `%s`, e:`%s`',
                        self.config['name'], self.config['address'], format_exc())

        else:
            # Do not handle it but log information so as not to overlook the event
            logger.info('WSX `%s` (%s) ignoring close event code:`%s` reason:`%s`',
                self.config['name'], self.config['address'], code, reason)

# ################################################################################################################################

    def send(self, data:'any_') -> 'None':

        # If we are being invoked while the queue is still building, we need to wait until it becomes available ..
        while self.client.is_building_conn_queue:
            _gevent_sleep(1)

        # .. now, we can invoke the remote web socket.
        with self.client() as client:
            client.send(data) # type: ignore

    invoke = send

# ################################################################################################################################

    def add_client(self) -> 'None':

        try:
            conn = WSXClient(self.server, self.config)
            self.conn_in_progress_list.append(conn)
            conn.init()

            if not conn.is_impl_connected():
                self.client.decr_in_progress_count()
                return

        except Exception:
            logger.warning('WSX client `%s` could not be built `%s`', self.config['name'], format_exc())
        else:
            try:
                if not self.client.put_client(conn):
                    self.delete_queue_connections(msg_closing_superfluous)
            except Exception:
                logger.warning('WSX error `%s`', format_exc())
            finally:
                self.client.decr_in_progress_count()

# ################################################################################################################################
# ################################################################################################################################
