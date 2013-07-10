  # -*- coding: utf-8 -*-
'''
Test Vincent.charts
-------------------

'''

import nose.tools as nt
from vincent.charts import (data_type, Chart)


def test_data_type():
    """Test automatic data type importing"""

    puts = [[1], [1, 2], ((1, 2)), ((1, 2), (3, 4)), [(1, 2), (3, 4)],
            [[1, 2], [3, 4]], {1: 2}, {1: 2, 3: 4}]

    common = [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]
    gets = [[{'x': 0, 'y': 1}], [{'x': 0, 'y': 1}, {'x': 1, 'y': 2}],
            [{'x': 0, 'y': 1}, {'x': 1, 'y': 2}], common, common,
            common, [{'x': 1, 'y': 2}], common]

    for ins, outs in zip(puts, gets):
        test = data_type(ins, False)
        nt.assert_list_equal(test.values, outs)
