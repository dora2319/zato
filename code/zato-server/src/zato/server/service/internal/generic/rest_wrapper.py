# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

def _replace_suffix_from_dict_name(data:'stranydict', wrapper_type:'str') -> 'str':
    _prefix = wrapper_type + '.'
    _name = data['name'] # type: str
    _name = _name.replace(_prefix, '', 1)
    return _name

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):

    name = 'zato.generic.rest-wrapper.get-list'

    def handle(self) -> 'None':

        # Our response to produce
        out = []

        # Our service to invoke
        service_name = 'zato.http-soap.get-list'

        # Filter by this wrapper type from input
        wrapper_type = self.request.raw_request['wrapper_type']

        # This response has all the REST connections possible ..
        response = self.invoke(service_name, {
            'cluster_id': self.server.cluster_id,
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
            'paginate': False,
        }, skip_response_elem=True)

        # .. iterate through each of them ..
        for item in response:

            # .. filter out everything but our own wrapper ..
            if item.get('wrapper_type') == wrapper_type:

                # .. replace the name prefix ..
                item['name'] = _replace_suffix_from_dict_name(item, wrapper_type)

                # .. and append the item to the result ..
                out.append(item)

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class _WrapperBase(Service):

    _wrapper_impl_suffix = None
    _uses_name = False

    # SimpleIO
    output = '-id', '-name', '-info', '-is_success'

# ################################################################################################################################

    def _handle(self, initial:'stranydict') -> 'None':

        # Our service to invoke
        service_name = 'zato.http-soap.' + self._wrapper_impl_suffix # type: ignore

        # Base request to create a new wrapper ..
        request = {
            'cluster_id': self.server.cluster_id,
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
            'url_path': r'{_zato_path}'
        }

        # .. extend it with our own extra input ..
        request.update(initial)

        # .. prepend a prefix to the name given that this is a wrapper ..
        # .. but note that the Delete action does not use a name so this block is optional ..
        if self._uses_name:
            _orig_name    = request['name']
            _name         = _orig_name
            _wrapper_type = request['wrapper_type']
            request['name'] = f'{_wrapper_type }.{_name}'

        # .. and send it to the service.
        response = self.invoke(service_name, request, skip_response_elem=True)

        # This is used by Create and Edit actions
        if self._uses_name:
            self.response.payload.name = _orig_name # type: ignore

        # These are optional as well
        self.response.payload.id   = response.get('id')
        self.response.payload.info = response.get('info')
        self.response.payload.is_success = response.get('is_success')

# ################################################################################################################################

    def handle(self):
        self._handle(self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

class Create(_WrapperBase):
    name = 'zato.generic.rest-wrapper.create'
    response_elem = None
    _wrapper_impl_suffix = 'create'
    _uses_name = True

# ################################################################################################################################
# ################################################################################################################################

class Edit(_WrapperBase):
    name = 'zato.generic.rest-wrapper.edit'
    response_elem = None
    _wrapper_impl_suffix = 'edit'
    _uses_name = True

# ################################################################################################################################
# ################################################################################################################################

class Delete(_WrapperBase):
    name = 'zato.generic.rest-wrapper.delete'
    _wrapper_impl_suffix = 'delete'
    _uses_name = False

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(_WrapperBase):
    name = 'zato.generic.rest-wrapper.change-password'
    _wrapper_impl_suffix = 'edit'
    _uses_name = False

    def handle(self):
        response = self.invoke('zato.http-soap.get', self.request.raw_request, skip_response_elem=True)
        edit_request = {
            'id': response['id'],
            'name': response['name'],
            'password': self.request.raw_request['password1']
        }
        self._handle(edit_request)

# ################################################################################################################################
# ################################################################################################################################

class Ping(_WrapperBase):
    name = 'zato.generic.rest-wrapper.ping'
    _wrapper_impl_suffix = 'ping'
    _uses_name = False

# ################################################################################################################################
# ################################################################################################################################
