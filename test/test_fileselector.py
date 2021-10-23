'''Test FileSelector Widget'''
import efl.elementary as elm
from efl.elementary.window import StandardWindow
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

from elmextensions import FileSelector

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL


# pylint: disable=too-few-public-methods
class MainWindow(object):
    '''FileSelector test window'''
    def __init__(self):
        win = StandardWindow("Testing", "Elementary File Selector")
        # pylint: disable=no-member
        win.callback_delete_request_add(lambda o: elm.exit())

        self.f_selector = f_selector = FileSelector(win,
                                                    size_hint_weight=EXPAND_BOTH,
                                                    size_hint_align=FILL_BOTH)
        # f_selector.folderOnlySet(True)
        f_selector.set_mode("Open")
        f_selector.show()

        f_selector.callback_activated_add(self.cb_activated)
        f_selector.callback_cancel_add(lambda o: elm.exit())

        win.resize_object_add(f_selector)

        win.resize(600, 400)
        win.show()

    # pylint: disable=no-self-use
    def cb_activated(self, f_selector, sel):
        '''Print selected'''
        print(sel)


if __name__ == "__main__":
    GUI = MainWindow()
    # pylint: disable=no-member
    elm.run()
    GUI.f_selector.shutdown()
    elm.shutdown()
