'''
Simple program to test aboutwindow module.
'''

# pylint: disable=no-name-in-module,no-member
import efl.elementary as elm
from efl.elementary.window import StandardWindow
from efl.elementary.label import Label
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from elmextensions import AboutWindow
EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL


AUTHORS = """
<br>
<align=center>
<hilight>Jeff Hoogland (Jef91)</hilight><br>
<link><a href=http://www.jeffhoogland.com>Contact</a></link><br><br>

<hilight>Wolfgang Morawetz (wfx)</hilight><br><br>

<hilight>Kai Huuhko (kukko)</hilight><br><br>
</align>
"""

LICENSE = """
<align=center>
<hilight>
GNU GENERAL PUBLIC LICENSE<br>
Version 3, 29 June 2007<br><br>
</hilight>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.<br><br>

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.<br><br>

You should have received a copy of the GNU General Public License
along with this program. If not, see<br>
<link><a href=http://www.gnu.org/licenses>http://www.gnu.org/licenses/</a></link>
</align>
"""

INFO = """
<align=center>
<hilight>Elementary Python Extensions</hilight> are awesome!<br>
<br>
<br>
</align>
"""

# pylint: disable=too-few-public-methods
class MainWindow(object):
    '''Sample Window for testing aboutwindow module'''
    def __init__(self):
        win = StandardWindow("Testing", "Elementary About Dialog")
        win.callback_delete_request_add(lambda o: elm.exit())
        win.show()

        lbl = Label(win,
                    size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
        lbl.text = "This is a parent window for the About Dialog. Close when done."
        lbl.show()

        win.resize_object_add(lbl)

        win.resize(600, 400)
        win.show()
        # pylint:too-many-function-args
        AboutWindow(win, "About Test", "dialog-information",
                    "1.0", AUTHORS,
                    LICENSE,
                    "https://github.com/JeffHoogland/python-elm-extensions",
                    INFO)


if __name__ == "__main__":
    elm.init()
    GUI = MainWindow()
    elm.run()
    elm.shutdown()
