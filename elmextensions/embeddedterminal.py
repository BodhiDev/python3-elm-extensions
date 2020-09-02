'''Simple and simple minded embedded terminal. Not for serious use.'''
from efl import ecore
from efl.elementary.box import Box
from efl.elementary.button import Button
from efl.elementary.entry import Entry, markup_to_utf8
from efl.elementary.frame import Frame
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5


class EmbeddedTerminal(Box):
    '''Embedded Terminal class.'''

    def __init__(self, parent_widget, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        self.output = Entry(self,
                            size_hint_weight=EXPAND_BOTH,
                            size_hint_align=FILL_BOTH)
        self.output.editable_set(False)
        self.output.scrollable_set(True)
        self.output.callback_changed_add(self.cb_changed)
        self.output.show()

        frame = Frame(self,
                      size_hint_weight=EXPAND_HORIZ,
                      size_hint_align=FILL_HORIZ)
        frame.text = 'Input:'
        frame.autocollapse_set(True)
        frame.collapse_go(True)
        frame.show()

        hbx = Box(self,
                  size_hint_weight=EXPAND_HORIZ,
                  size_hint_align=FILL_HORIZ)
        hbx.horizontal = True
        hbx.show()

        frame.content = hbx

        self.input = Entry(self,
                           size_hint_weight=EXPAND_BOTH,
                           size_hint_align=FILL_BOTH)
        self.input.single_line_set(True)
        self.input.callback_activated_add(self.cb_enter)
        self.input.show()

        enter_btn = Button(self)
        enter_btn.text = 'Execute'
        enter_btn.callback_pressed_add(self.cb_enter)
        enter_btn.show()

        hbx.pack_end(self.input)
        hbx.pack_end(enter_btn)

        self.pack_end(self.output)
        self.pack_end(frame)

        self.cmd_exe = None
        self.done_cb = None

    # pylint: disable=no-self-use
    def cb_changed(self, obj):
        '''Output changed, move cursor'''
        obj.cursor_end_set()

    def cb_enter(self, btn):
        '''Enter pressed on input'''
        if not self.cmd_exe:
            self.run_cmd(self.input.text)
            self.input.text = ''
        else:
            self.cmd_exe.send(f'{self.input.text}\n')
            self.input.text = ''

    def run_cmd(self, command, done_cb=None):
        '''Run command capture ouput'''
        command = markup_to_utf8(command)
        # pylint: disable=c-extension-no-member
        self.cmd_exe = cmd = ecore.Exe(
            command, ecore.ECORE_EXE_PIPE_READ | ecore.ECORE_EXE_PIPE_ERROR |
            ecore.ECORE_EXE_PIPE_WRITE)
        cmd.on_add_event_add(self.cb_started)
        cmd.on_data_event_add(self.cb_data)
        cmd.on_error_event_add(self.cb_error)
        cmd.on_del_event_add(self.cb_done)

        self.done_cb = done_cb

    def cb_started(self, cmd, event, *args, **kwargs):
        '''Command start'''
        self.output.entry_append('---------------------------------')
        self.output.entry_append('<br>')

    def cb_data(self, cmd, event, *args, **kwargs):
        '''Stdout callback'''
        self.output.entry_append(f'{event.data}')
        self.output.entry_append('<br>')

    def cb_error(self, cmd, event, *args, **kwargs):
        '''Stderr callback'''
        self.output.entry_append(f'Error: {event.data}')

    def cb_done(self, cmd, event, *args, **kwargs):
        '''Command finished callback'''
        self.output.entry_append('---------------------------------')
        self.output.entry_append('<br>')
        self.cmd_exe = None
        if self.done_cb:
            if callable(self.done_cb):
                self.done_cb()
