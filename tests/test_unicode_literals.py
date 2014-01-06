  # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from vincent.charts import Bar


def test_unicode_axes():
    """Verify that python2.7 will allow arbitrary unicode strings
       in the same way python 3.2/3.3 does.
       We use unicode_literals __future__ to make this test cross platform
       without using version switches,
       """
    bar = Bar([1, 2, 3])
    bar.axis_titles(x="老特洛伊呗", y="ZAŻÓŁĆ GĘŚLĄ JAŹŃ")
    ### XXX: if this proves to be correct fix, we should test more methods here
