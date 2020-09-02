'''Build standard pop up window'''
# pylint: disable=no-name-in-module
from efl.elementary.button import Button
from efl.elementary.icon import Icon
from efl.elementary.image import Image
from efl.elementary.label import Label, ELM_WRAP_WORD
from efl.elementary.need import need_ethumb
from efl.elementary.popup import Popup
from efl.elementary.table import Table
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5


# pylint: disable=no-member,too-few-public-methods
class StandardPopup:
    '''Standard popup class'''

    def __init__(self, our_parent, our_msg, *args, our_ic=None, **kwargs):
        Popup.__init__(self, our_parent, *args, **kwargs)
        self.callback_block_clicked_add(lambda obj: self.delete())

        # Add a table to hold dialog image and text to Popup
        tbl = Table(self, size_hint_weight=EXPAND_BOTH)
        self.part_content_set('default', tbl)
        tbl.show()

        # Add dialog-error Image to table
        need_ethumb()
        icon = Icon(self, thumb='True')
        icon.standard_set(our_ic)
        # Using gksudo or sudo fails to load Image here
        #   unless options specify using preserving their existing environment.
        #   may also fail to load other icons but does not raise an exception
        #   in that situation.
        # Works fine using eSudo as a gksudo alternative,
        #   other alternatives not tested
        try:
            dialog_img = Image(self,
                               size_hint_weight=EXPAND_HORIZ,
                               size_hint_align=FILL_BOTH,
                               file=icon.file_get())
            tbl.pack(dialog_img, 0, 0, 1, 1)
            dialog_img.show()
        except RuntimeError:
            # An error message is displayed for this same error
            #   when aboutWin is initialized so no need to redisplay.
            pass
        # Add dialog text to table
        dialog_lb = Label(self,
                          line_wrap=ELM_WRAP_WORD,
                          size_hint_weight=EXPAND_HORIZ,
                          size_hint_align=FILL_BOTH)
        dialog_lb.text = our_msg
        tbl.pack(dialog_lb, 1, 0, 1, 1)
        dialog_lb.show()

        # Ok Button
        ok_btn = Button(self)
        ok_btn.text = 'Ok'
        ok_btn.callback_clicked_add(lambda obj: self.delete())
        ok_btn.show()

        # add button to popup
        self.part_content_set('button3', ok_btn)
