'''
Simple program to test SortedList module.
'''
# pylint: disable=no-name-in-module, no-member
import random
from efl.elementary.window import StandardWindow
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
import efl.elementary as elm
from sortedlist import SortedList

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

ROWS = 300
COLUMNS = 5


# pylint: disable=too-few-public-methods
class Derp(object):
    '''Sample Window for testing SortedList module'''
    def __init__(self):
        win = StandardWindow("Testing", "Elementary Sorted Table")
        win.callback_delete_request_add(lambda o: elm.exit())

        titles = []
        for i in range(COLUMNS):
            titles.append(("Column " + str(i), True if i != 2 else False))

        slist = SortedList(win,
                           titles=titles,
                           size_hint_weight=EXPAND_BOTH,
                           size_hint_align=FILL_BOTH)

        for _i in range(ROWS):
            row = []
            # pylint: disable=unused-variable
            for _j in range(COLUMNS):
                data = random.randint(0, ROWS * COLUMNS)
                row.append(data)
            slist.row_pack(row, sort=False)
        # slist.sort_by_column(1)
        slist.show()

        win.resize_object_add(slist)

        win.resize(600, 400)
        win.show()


if __name__ == "__main__":
    GUI = Derp()
    elm.init()
    elm.run()
    elm.shutdown()
