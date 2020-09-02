'''Test TabbedBox'''
import efl.elementary as elm
from efl.elementary.label import Label
from efl.elementary.window import StandardWindow
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from elmextensions import TabbedBox

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL


# pylint: disable=too-few-public-methods
class MainWindow(object):
    '''Main window to test TabbedBox widget'''
    def __init__(self):
        win = StandardWindow("Testing", "Elementary Tabbed Widget")
        # pylint: disable=no-member
        win.callback_delete_request_add(lambda o: elm.exit())

        tabbs = TabbedBox(win, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        tabbs.close_cb = self.close_checks

        for i in range(10):
            lbl = Label(win)
            lbl.text = "Tab %s"%i
            lbl.show()
            tabbs.add(lbl, "Tab %s"%i)

        tabbs.disable(0)
        tabbs.disable(3)

        tabbs.show()

        win.resize_object_add(tabbs)

        win.resize(600, 400)
        win.show()

    # pylint: disable= no-self-use
    def close_checks(self, tabbs, widget):
        '''Close tab'''
        print(widget.text)
        if widget.text != "Tab 1":
            tabbs.delete_tab(widget)

if __name__ == "__main__":
    GUI = MainWindow()
    # pylint: disable=no-member
    elm.run()
    elm.shutdown()
