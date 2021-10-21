'''
   Standard button module
'''
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl.elementary.button import Button
from efl.elementary.icon import Icon

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL


# pylint: disable=too-few-public-methods
class StandardButton(Button):
    '''Build standard button'''

    def __init__(self,
                 parent,
                 text,
                 *args,
                 ic_btn=None,
                 cb_onclick=None,
                 **kwargs):

        Button.__init__(self, parent, *args, **kwargs)
        icon = Icon(self,
                    size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
        icon.standard_set(ic_btn)
        icon.show()

        self.text = text
        self.content_set(icon)
        if cb_onclick:
            self.callback_clicked_add(cb_onclick)
