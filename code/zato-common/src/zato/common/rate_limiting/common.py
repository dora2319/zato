# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strset

# ################################################################################################################################
# ################################################################################################################################

class BaseException(Exception):
    pass

class AddressNotAllowed(BaseException):
    pass

class RateLimitReached(BaseException):
    pass

# ################################################################################################################################
# ################################################################################################################################

class Const:

    from_any = '*'
    rate_any = '*'

    class Unit:
        minute = 'm'
        hour   = 'h'
        day    = 'd'

    @staticmethod
    def all_units() -> 'strset':
        return {Const.Unit.minute, Const.Unit.hour, Const.Unit.day}

# ################################################################################################################################
# ################################################################################################################################

class ObjectInfo:
    """ Information about an individual object covered by rate limiting.
    """
    __slots__ = 'type_', 'id', 'name'

    type_:'str'
    id:'int'
    name:'str'

# ################################################################################################################################
# ################################################################################################################################

class DefinitionItem:
    __slots__ = 'config_line', 'from_', 'rate', 'unit', 'object_id', 'object_type', 'object_name'

    config_line:'int'
    from_:'any_'
    rate:'int'
    unit:'str'
    object_id:'int'
    object_type:'str'
    object_name:'str'

    def __repr__(self) -> 'str':
        return '<{} at {}; line:{}, from:{}, rate:{}, unit:{} ({} {} {})>'.format(
            self.__class__.__name__, hex(id(self)), self.config_line, self.from_, self.rate, self.unit,
            self.object_id, self.object_name, self.object_type)

# ################################################################################################################################
# ################################################################################################################################
