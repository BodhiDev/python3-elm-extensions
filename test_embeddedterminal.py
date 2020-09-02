'''Test embedded terminal'''
# pylint: disable=no-name-in-module,no-member
import efl.elementary as elm
from efl.elementary.window import StandardWindow
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from elmextensions import EmbeddedTerminal

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL


# pylint: disable=too-few-public-methods
class MainWindow:
    '''build main window'''

    def __init__(self):
        win = StandardWindow("Testing", "Elementary Embedded Terminal")
        win.callback_delete_request_add(lambda o: elm.exit())
        term = EmbeddedTerminal(win,
                                size_hint_weight=EXPAND_BOTH,
                                size_hint_align=FILL_BOTH)
        term.show()
        win.resize_object_add(term)
        win.resize(600, 400)
        win.show()


if __name__ == "__main__":
    elm.init()
    GUI = MainWindow()
    elm.run()
    elm.shutdown()
