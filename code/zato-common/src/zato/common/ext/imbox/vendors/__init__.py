# -*- coding: utf-8 -*-

"""
This module is a modified vendor copy of the Imbox package from https://pypi.org/project/imbox/

The MIT License (MIT)

Copyright (c) 2013 Martin Rusev

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from zato.common.ext.imbox.vendors.gmail import GmailMessages

vendors = [GmailMessages]

hostname_vendorname_dict = {vendor.hostname: vendor.name for vendor in vendors}
name_authentication_string_dict = {vendor.name: vendor.authentication_error_message for vendor in vendors}

__all__ = [v.__name__ for v in vendors]

__all__ += ['hostname_vendorname_dict',
            'name_authentication_string_dict']
