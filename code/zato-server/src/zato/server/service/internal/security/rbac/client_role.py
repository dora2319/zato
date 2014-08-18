# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import RBAC
from zato.common.odb.model import RBACClientRole, RBACRole
from zato.common.odb.query import rbac_client_role_list
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_rbac_client_role'
model = RBACClientRole
label = 'an RBAC client role'
broker_message = RBAC
broker_message_prefix = 'CLIENT_ROLE_'
list_func = rbac_client_role_list
output_optional_extra = ['client_name', 'role_name']
create_edit_rewrite = ['id']
skip_input_params = ['name']
check_existing_one = False

def instance_hook(service, input, instance, attrs):
    with closing(service.odb.session()) as session:
        role = session.query(RBACRole).\
            filter(RBACRole.id==input.role_id).one()

    instance.name = '{}/{}'.format(instance.client_def, role.name)

def response_hook(service, input, instance, attrs, service_type):

    if service_type == 'get_list':
        for item in service.response.payload:
            with closing(service.odb.session()) as session:
                role = session.query(RBACRole).filter(RBACRole.id==item.role_id).one()
                item.client_name = item.client_def
                item.role_name = role.name
    else:
        service.response.payload.client_name = 'c'
        service.response.payload.role_name = 'r'

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class GetClientDefList(AdminService):
    """ Returns a list of client definitions - both these that use Zato's built-in security mechanisms
    as well as custom ones, as defined by users.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_rbac_client_role_get_client_def_list_request'
        response_elem = 'zato_security_rbac_client_role_get_client_def_list_response'
        input_required = ('cluster_id',)
        output_required = ('client_def', 'client_name')

    def get_data(self, session):

        service = 'zato.security.get-list'
        request = {'cluster_id':self.request.input.cluster_id, 'needs_internal':False}

        for item in self.invoke(service, request, as_bunch=True)['zato_security_get_list_response']:
            client_name = '{}/{}'.format(item.sec_type, item.name)
            yield {'client_def':'sec_def:::{}'.format(client_name), 'client_name':client_name}

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)
