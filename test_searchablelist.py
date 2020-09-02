''' Code to test SearchableList class'''
import efl.elementary as elm
from efl.elementary.window import StandardWindow
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from elmextensions import SearchableList

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

# pylint: disable=too-few-public-methods
class MainWindow(object):
    '''Main Window for test'''
    def __init__(self):
        win = StandardWindow("Testing", "Elementary SearchableList")
        # pylint: disable=no-member
        win.callback_delete_request_add(lambda o: elm.exit())

        our_list = SearchableList(win,
                                  size_hint_weight=EXPAND_BOTH,
                                  size_hint_align=FILL_BOTH)
        self.keys = [
            "Jeff", "Kristi", "Jacob", "Declan", "Joris", "Timmy", "Tristam"
        ]
        for kbl in self.keys:
            our_list.item_append(kbl)
        our_list.show()

        win.resize_object_add(our_list)

        win.resize(600, 400)
        win.show()


if __name__ == "__main__":
    GUI = MainWindow()
    # pylint: disable=no-member
    elm.run()
    elm.shutdown()
