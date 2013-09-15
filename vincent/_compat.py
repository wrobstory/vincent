# -*- coding: utf-8 -*-
"""
Compat: Minimal, required compatibility layer for py2/py3
"""

import sys

PY2 = sys.version_info[0] == 2


if not PY2:
    str_types = (str, )
else:
    str_types = (unicode, str)
