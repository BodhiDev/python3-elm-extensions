'''
   Standardized About Window for EFL
'''
# pylint: disable=no-name-in-module
from efl.ecore import Exe
from efl.elementary.background import Background
from efl.elementary.box import Box
from efl.elementary.button import Button
from efl.elementary.entry import Entry
from efl.elementary.frame import Frame
from efl.elementary.icon import Icon
from efl.elementary.label import Label
from efl.elementary.separator import Separator
from efl.elementary.window import Window, ELM_WIN_DIALOG_BASIC
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
EXPAND_VERT = 0.0, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
FILL_VERT = 0.5, EVAS_HINT_FILL


def xdg_open(url_or_file):
    '''convenience function.'''
    Exe(f'xdg-open "{url_or_file}"')


class InstanceError(Exception):
    '''Instance error msg'''
    pass

# pylint: disable=too-few-public-methods
class AboutWindow(Window):
    '''
    A standardized About Window Class for EFL
    '''
    __initialized = False
    # pylint: disable=too-many-arguments, too-many-locals, too-many-statements
    def __init__(self,
                 parent,
                 title='About',
                 standardicon='dialog-information',
                 version='N/A',
                 authors='No One',
                 licen='GPL',
                 webaddress='',
                 info='Something, something, turtles'):

        if AboutWindow.__initialized:
            raise InstanceError(
                "You can't create more than 1 instance of AboutWindow")
        AboutWindow.__initialized = True
        self.parent = parent
        Window.__init__(self, title, ELM_WIN_DIALOG_BASIC, autodel=True)
        self.callback_delete_request_add(self.cb_close)
        background = Background(self, size_hint_weight=EXPAND_BOTH)
        self.resize_object_add(background)
        background.show()

        frame = Frame(self,
                      style='pad_large',
                      size_hint_weight=EXPAND_BOTH,
                      size_hint_align=FILL_BOTH)
        self.resize_object_add(frame)
        frame.show()

        hbox = Box(self, horizontal=True, padding=(12, 12))
        frame.content = hbox
        hbox.show()

        vbox = Box(self,
                   align=(0.0, 0.0),
                   padding=(6, 6),
                   size_hint_weight=EXPAND_VERT,
                   size_hint_align=FILL_VERT)
        hbox.pack_end(vbox)
        vbox.show()

        # icon + version
        icon = Icon(self, size_hint_min=(64, 64))
        icon.standard_set(standardicon)
        vbox.pack_end(icon)
        icon.show()

        ver_lb = Label(self, text=f'Version: {version}')
        vbox.pack_end(ver_lb)
        ver_lb.show()

        sep = Separator(self, horizontal=True)
        vbox.pack_end(sep)
        sep.show()

        # buttons
        btn = Button(self, text=(title), size_hint_align=FILL_HORIZ)
        btn.callback_clicked_add(lambda b: self.entry.text_set(info))
        vbox.pack_end(btn)
        btn.show()

        btn = Button(self, text=('Website'), size_hint_align=FILL_HORIZ)
        btn.callback_clicked_add(lambda b: xdg_open(webaddress))
        vbox.pack_end(btn)
        btn.show()

        btn = Button(self, text=('Authors'), size_hint_align=FILL_HORIZ)
        btn.callback_clicked_add(lambda b: self.entry.text_set(authors))
        vbox.pack_end(btn)
        btn.show()

        btn = Button(self, text=('License'), size_hint_align=FILL_HORIZ)
        btn.callback_clicked_add(lambda b: self.entry.text_set(licen))
        vbox.pack_end(btn)
        btn.show()

        # main text
        self.entry = Entry(self,
                           editable=False,
                           scrollable=True,
                           text=info,
                           size_hint_weight=EXPAND_BOTH,
                           size_hint_align=FILL_BOTH)
        self.entry.callback_anchor_clicked_add(lambda e, i: xdg_open(i.name))
        hbox.pack_end(self.entry)
        self.entry.show()

        self.resize(400, 200)
        self.show()

    # pylint: disable=no-self-use
    def cb_close(self, obj):
        '''Callback on close'''
        AboutWindow.__initialized = False
