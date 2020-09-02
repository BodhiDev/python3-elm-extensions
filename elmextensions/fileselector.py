'''FileSelector widget for EFL'''
import os
import math
from collections import deque
from efl import ecore
from efl.elementary.box import Box
from efl.elementary.button import Button
from efl.elementary.entry import Entry, ELM_INPUT_HINT_AUTO_COMPLETE
from efl.elementary.hoversel import Hoversel
from efl.elementary.icon import Icon, ELM_ICON_LOOKUP_THEME
from efl.elementary.image import Image
from efl.elementary.genlist import Genlist, GenlistItem, GenlistItemClass, \
    ELM_LIST_COMPRESS
from efl.elementary.label import Label
from efl.elementary.list import List
from efl.elementary.panes import Panes
from efl.elementary.popup import Popup
from efl.elementary.separator import Separator
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, EVAS_CALLBACK_KEY_DOWN
# imported to work around a bug
# import efl.elementary.layout
from .easythreading import ThreadedFunction
from .bookmarks import Bookmarks

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5


class FileGLIC(GenlistItemClass):
    '''GenlistItemClass for files'''
    error = False

    # pylint: disable=unused-argument, no-self-use
    def text_get(self, gen_lst, part, data):
        '''Return text for GenlistItem'''
        return data['d']

    def content_get(self, gen_lst, part, data):
        '''Return Icon for GenlistItem'''
        icon = None
        if part == 'elm.swallow.icon':
            try:
                icon = Icon(gen_lst, standard='file')
            except RuntimeWarning:
                try:
                    icon = Icon(gen_lst, standard='gtk-file')
                except RuntimeWarning:
                    if not FileGLIC.error:
                        print('ERROR: Cannot find gtk-file icon')
                        FileGLIC.error = True
        return icon


class DirGLIC(GenlistItemClass):
    '''GenlistItemClass for folders'''

    # pylint: disable=unused-argument, no-self-use
    def text_get(self, gen_lst, part, data):
        '''Return text for GenlistItem'''
        return data['d']

    def content_get(self, gen_lst, part, data):
        '''Return icon for GenlistItem'''
        if part == 'elm.swallow.icon':
            return Icon(gen_lst, standard='folder')
        return None


FILEGLIC = FileGLIC(item_style='one_icon')
DIRGLIC = DirGLIC(item_style='one_icon')


# pylint: disable=too-many-public-methods, too-many-locals
class FileSelector(Box):
    '''FileSelector Class'''

    # pylint: disable=too-many-instance-attributes, too-many-statements
    def __init__(self,
                 parent_widget,
                 *args,
                 default_path='',
                 default_populate=True,
                 **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        self.cancel_cb = None
        self.action_cb = None
        self.cb_dir_change = None

        self.threaded_fn = ThreadedFunction()
        # pylint: disable=c-extension-no-member
        self._timer = ecore.Timer(0.02, self.populate_file)

        # Watch key presses for ctrl+l to select entry
        parent_widget.elm_event_callback_add(self.cb_events)

        self.selected_dir = None
        self.show_hidden = False
        self.cur_dir = None
        self.focused_entry = None
        self.dir_only = False
        self.sort_reverse = False
        self.adding_hidden = False
        self.pending_files = deque()
        self.cur_subdirs = []
        self.cur_files = []

        # Mode should be 'save' or 'load'
        self.mode = 'save'

        self.home = os.path.expanduser('~')

        desktop = os.environ.get('XDG_DESKTOP_DIR')
        if desktop:
            self.desktop = desktop
        else:
            self.desktop = self.home + '/Desktop'

        self.root = '/'

        # Label+Entry for File Name
        self.filename_bx = Box(self,
                               size_hint_weight=EXPAND_HORIZ,
                               size_hint_align=FILL_HORIZ)
        self.filename_bx.horizontal = True
        self.filename_bx.show()

        file_label = Label(self,
                           size_hint_weight=(0.15, EVAS_HINT_EXPAND),
                           size_hint_align=FILL_HORIZ)
        file_label.text = 'Filename:'
        file_label.show()

        self.file_entry = Entry(self,
                                size_hint_weight=EXPAND_BOTH,
                                size_hint_align=FILL_HORIZ)
        self.file_entry.single_line_set(True)
        self.file_entry.scrollable_set(True)
        self.file_entry.callback_changed_user_add(self.cb_file_entry)
        self.file_entry.show()

        self.filename_bx.pack_end(file_label)
        self.filename_bx.pack_end(self.file_entry)

        sep = Separator(self,
                        size_hint_weight=EXPAND_HORIZ,
                        size_hint_align=FILL_HORIZ)
        sep.horizontal_set(True)
        sep.show()

        # Label+Entry for File Path
        self.filepath_bx = Box(self,
                               size_hint_weight=EXPAND_HORIZ,
                               size_hint_align=FILL_HORIZ)
        self.filepath_bx.horizontal = True
        self.filepath_bx.show()

        file_label = Label(self,
                           size_hint_weight=(0.15, EVAS_HINT_EXPAND),
                           size_hint_align=FILL_HORIZ)
        file_label.text = 'Current Folder:'
        file_label.show()

        self.filepath_en = Entry(self,
                                 size_hint_weight=EXPAND_BOTH,
                                 size_hint_align=FILL_HORIZ)
        self.filepath_en.single_line_set(True)
        self.filepath_en.scrollable_set(True)
        self.filepath_en.callback_changed_user_add(self.cb_file_entry)
        self.filepath_en.callback_unfocused_add(self.cb_filepath_en)
        self.filepath_en.callback_activated_add(self.cb_filepath_en)
        # Wish this worked. Doesn't seem to do anything
        # Working now EFL 1.22 ?
        self.filepath_en.input_hint_set(ELM_INPUT_HINT_AUTO_COMPLETE)

        if default_path and os.path.isdir(default_path):
            start = default_path
        else:
            start = self.home
        self.filepath_en.show()

        self.filepath_bx.pack_end(file_label)
        self.filepath_bx.pack_end(self.filepath_en)

        self.autocomplete_hover = Hoversel(self, hover_parent=self)
        self.autocomplete_hover.callback_selected_add(self.cb_hover)
        self.autocomplete_hover.show()

        self.file_selector_bx = Panes(self,
                                      content_left_size=0.3,
                                      size_hint_weight=EXPAND_BOTH,
                                      size_hint_align=FILL_BOTH)
        self.file_selector_bx.show()
        # Bookmarks Box contains:
        #
        # - Button - Up Arrow
        # - List - Home/Desktop/Root/GTK bookmarks
        # - Box
        # -- Button - Add Bookmark
        # -- Button - Remove Bookmark
        self.bookmark_bx = Box(self,
                               size_hint_weight=(0.3, EVAS_HINT_EXPAND),
                               size_hint_align=FILL_BOTH)
        self.bookmark_bx.show()

        up_ic = Icon(self,
                     size_hint_weight=EXPAND_BOTH,
                     size_hint_align=FILL_BOTH,
                     order_lookup=ELM_ICON_LOOKUP_THEME)
        up_ic.standard_set('arrow-up')
        up_ic.show()

        self.up_btn = Button(self,
                             size_hint_weight=EXPAND_HORIZ,
                             size_hint_align=FILL_HORIZ,
                             content=up_ic)
        self.up_btn.text = 'Up'
        self.up_btn.callback_pressed_add(self.cb_up_btn)
        self.up_btn.show()

        self.bookmarks_lst = List(self,
                                  size_hint_weight=EXPAND_BOTH,
                                  size_hint_align=FILL_BOTH)
        self.bookmarks_lst.callback_activated_add(self.cb_bookmarks_lst)
        self.bookmarks_lst.show()

        self.bookmark_modbox = Box(self,
                                   size_hint_weight=EXPAND_HORIZ,
                                   size_hint_align=FILL_HORIZ)
        self.bookmark_modbox.horizontal = True
        self.bookmark_modbox.show()

        con = Icon(self,
                   size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        con.standard_set('list-add')
        con.show()

        self.add_btn = Button(self,
                              size_hint_weight=EXPAND_HORIZ,
                              size_hint_align=FILL_HORIZ,
                              content=con)
        self.add_btn.callback_pressed_add(self.cb_add_btn)
        self.add_btn.disabled = True
        self.add_btn.show()

        con = Icon(self,
                   size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        con.standard_set('list-remove')
        con.show()

        self.rm_btn = Button(self,
                             size_hint_weight=EXPAND_HORIZ,
                             size_hint_align=FILL_HORIZ,
                             content=con)
        self.rm_btn.callback_pressed_add(self.cb_remove)
        self.rm_btn.disabled = True
        self.rm_btn.show()

        self.bookmark_modbox.pack_end(self.add_btn)
        self.bookmark_modbox.pack_end(self.rm_btn)

        self.bookmark_bx.pack_end(self.up_btn)
        self.bookmark_bx.pack_end(self.bookmarks_lst)
        self.bookmark_bx.pack_end(self.bookmark_modbox)

        # Directory List
        self.file_list_bx = Box(self,
                                size_hint_weight=EXPAND_BOTH,
                                size_hint_align=FILL_BOTH)
        self.file_list_bx.show()

        self.file_sort_btn = Button(self,
                                    size_hint_weight=EXPAND_HORIZ,
                                    size_hint_align=FILL_HORIZ)
        self.file_sort_btn.text = u'⬆ Name'
        self.file_sort_btn.callback_pressed_add(self.cb_sort)
        self.file_sort_btn.show()

        self.file_lst = Genlist(self,
                                size_hint_weight=EXPAND_BOTH,
                                size_hint_align=FILL_BOTH,
                                homogeneous=True,
                                mode=ELM_LIST_COMPRESS)
        self.file_lst.callback_activated_add(self.cb_file_lst)
        self.file_lst.show()

        self.preview = preview = Image(self)
        preview.size_hint_align = FILL_BOTH
        preview.show()

        self.file_list_bx.pack_end(self.file_sort_btn)
        self.file_list_bx.pack_end(self.file_lst)
        self.file_list_bx.pack_end(self.preview)

        self.file_selector_bx.part_content_set('left', self.bookmark_bx)
        self.file_selector_bx.part_content_set('right', self.file_list_bx)

        # Cancel and Save/Open button
        self.button_bx = Box(self,
                             size_hint_weight=EXPAND_HORIZ,
                             size_hint_align=(1.0, 0.5))
        self.button_bx.horizontal = True
        self.button_bx.show()

        self.action_ic = Icon(self,
                              size_hint_weight=EXPAND_BOTH,
                              size_hint_align=FILL_BOTH)
        self.action_ic.standard_set('document-save')
        self.action_ic.show()

        self.action_btn = Button(self,
                                 size_hint_weight=(0.0, 0.0),
                                 size_hint_align=(1.0, 0.5),
                                 content=self.action_ic)
        self.action_btn.text = 'Save  '
        self.action_btn.callback_pressed_add(self.cb_action_btn)
        self.action_btn.show()

        cancel_ic = Icon(self,
                         size_hint_weight=EXPAND_BOTH,
                         size_hint_align=FILL_BOTH)
        cancel_ic.standard_set('application-exit')
        cancel_ic.show()

        self.cancel_btn = Button(self,
                                 size_hint_weight=(0.0, 0.0),
                                 size_hint_align=(1.0, 0.5),
                                 content=cancel_ic)
        self.cancel_btn.text = 'Cancel  '
        self.cancel_btn.callback_pressed_add(self.cb_cancel_btn)
        self.cancel_btn.show()

        con = Icon(self,
                   size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        con.standard_set('edit-find')
        con.show()

        self.hidden_btn = Button(self,
                                 size_hint_weight=(0.0, 0.0),
                                 size_hint_align=(1.0, 0.5),
                                 content=con)
        self.hidden_btn.text = 'Toggle Hidden  '
        self.hidden_btn.callback_pressed_add(self.cb_toggle_hidden)
        self.hidden_btn.show()

        con = Icon(self,
                   size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        con.standard_set('folder-new')
        con.show()

        self.create_dir_btn = Button(self,
                                     size_hint_weight=(0.0, 0.0),
                                     size_hint_align=(1.0, 0.5),
                                     content=con)
        self.create_dir_btn.text = 'Create Folder  '
        self.create_dir_btn.callback_pressed_add(self.cb_create_dir)
        self.create_dir_btn.show()

        self.button_bx.pack_end(self.create_dir_btn)
        self.button_bx.pack_end(self.hidden_btn)
        self.button_bx.pack_end(self.cancel_btn)
        self.button_bx.pack_end(self.action_btn)

        self.pack_end(self.filename_bx)
        self.pack_end(sep)
        self.pack_end(self.filepath_bx)
        self.pack_end(self.autocomplete_hover)
        self.pack_end(self.file_selector_bx)
        self.pack_end(self.button_bx)

        self.populate_bookmarks()

        self.create_popup = Popup(self)
        self.create_popup.part_text_set('title,text', 'Create Folder:')

        self.create_en = Entry(self,
                               size_hint_weight=EXPAND_HORIZ,
                               size_hint_align=FILL_HORIZ)
        self.create_en.single_line_set(True)
        self.create_en.scrollable_set(True)
        self.create_en.show()

        self.create_popup.content = self.create_en

        bt0 = Button(self, text='Create')
        bt0.callback_clicked_add(self.cb_create_folder)
        self.create_popup.part_content_set('button1', bt0)
        bt1 = Button(self, text='Cancel')
        bt1.callback_clicked_add(self.cb_close_popup)
        self.create_popup.part_content_set('button2', bt1)

        self.recent = None  # keeps pylint happy:
        if default_populate:
            self.populate_files(start)

    def dir_only_set(self, value):
        '''Set folder only attribute and adjust display'''
        self.dir_only = value

        if not self.dir_only:
            self.filename_bx.show()
        else:
            self.filename_bx.hide()

    def cb_create_folder(self, obj):
        '''Create a new folder'''
        new = f'{self.cur_dir}{self.create_en.text}'
        os.makedirs(new)
        self.cb_close_popup()
        self.populate_files(self.cur_dir)

    def cb_create_dir(self, obj):
        '''Open popup to create a new folder'''
        self.create_en.text = ''
        self.create_popup.show()
        self.create_en.select_all()

    def cb_close_popup(self, btn=None):
        '''Close popup'''
        self.create_popup.hide()

    # pylint: disable=unused-argument
    def shutdown(self, obj=None):
        '''Cleanup function for FileSelector widget shutdown'''
        self._timer.delete()
        self.threaded_fn.shutdown()

    def cb_sort(self, btn):
        '''callback for sort button'''
        self.sort_reverse = not self.sort_reverse
        if self.sort_reverse:
            self.file_sort_btn.text = u'⬇ Name'
        else:
            self.file_sort_btn.text = u'⬆ Name'

        self.populate_files(self.cur_dir)

    def populate_bookmarks(self):
        '''Fill Bookamrks List'''
        con = Icon(self,
                   size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        con.standard_set('document-open-recent')
        con.show()
        cur_item = self.bookmarks_lst.item_append('Recent', icon=con)
        cur_item.data['path'] = 'recent:///'

        cur_item = self.bookmarks_lst.item_append('')
        cur_item.separator_set(True)

        con = Icon(self,
                   size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        con.standard_set('user-home')
        con.show()

        cur_item = self.bookmarks_lst.item_append('Home', icon=con)
        cur_item.data['path'] = self.home

        if os.path.isdir(self.desktop):
            con = Icon(self,
                       size_hint_weight=EXPAND_BOTH,
                       size_hint_align=FILL_BOTH)
            con.standard_set('user-desktop')
            con.show()

            cur_item = self.bookmarks_lst.item_append('Desktop', icon=con)
            cur_item.data['path'] = self.desktop

        con = Icon(self,
                   size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        con.standard_set('drive-harddisk')
        con.show()

        cur_item = self.bookmarks_lst.item_append('Root', icon=con)
        cur_item.data['path'] = self.root

        cur_item = self.bookmarks_lst.item_append('')
        cur_item.separator_set(True)

        for url in self.get_gtk_bookmarks():
            con = Icon(self,
                       size_hint_weight=EXPAND_BOTH,
                       size_hint_align=FILL_BOTH)
            con.standard_set('folder')
            con.show()
            cur_item = self.bookmarks_lst.item_append(url.split('/')[-1],
                                                      icon=con)
            cur_item.data['path'] = url[7:]

    def populate_file(self):
        '''Add Pending File to Files list'''
        pen_file = len(self.pending_files)
        if pen_file:
            for _ in range(int(math.sqrt(pen_file))):
                path, name, is_dir = self.pending_files.popleft()
                self.pack_all(path, name, is_dir)

        # else:
        #    self._timer.freeze()

        return True

    def populate_files(self, path):
        '''Start threaded FN to get dir contents'''
        self.autocomplete_hover.hover_end()

        self.pending_files.clear()

        if path[:-1] != '/':
            path = path + '/'
        if path != self.filepath_en.text or not self.show_hidden:
            self.adding_hidden = False

            if self.cb_dir_change:
                self.cb_dir_change(path)

            del self.cur_subdirs[:]
            del self.cur_files[:]
            self.file_lst.clear()
        else:
            self.adding_hidden = True

        self.filepath_en.text = path.replace('//', '/')
        self.cur_dir = path.replace('//', '/')

        self.threaded_fn.run(self.get_dir_contents)

    def get_dir_contents(self):
        '''Add Folder contents to pending files'''
        path = self.cur_dir
        if path == 'recent://':
            self.recent = Bookmarks()
            data = list(self.recent.dict.keys())
            for cur in data:
                self.pending_files.append([path, cur, False])
            return
        data = os.listdir(str(path))

        sorted_data = []
        for name in data:
            is_dir = os.path.isdir(f'{path}{name}')
            if is_dir:
                self.cur_subdirs.append(name)
                if self.sort_reverse:
                    sorted_data.append([1, name])
                else:
                    sorted_data.append([0, name])
            else:
                self.cur_files.append(name)
                if self.sort_reverse:
                    sorted_data.append([0, name])
                else:
                    sorted_data.append([1, name])

        sorted_data.sort(reverse=self.sort_reverse)
        for cur in sorted_data:
            name = cur[1]
            is_dir = cur[0] if self.sort_reverse else not cur[0]
            if self.adding_hidden and name[0] == '.':
                self.pending_files.append([path, name, is_dir])
            elif (name[0] != '.' or
                  self.show_hidden) and not self.adding_hidden:
                self.pending_files.append([path, name, is_dir])

    def pack_all(self, path, name, is_dir):
        '''Append to genlist'''
        if is_dir:
            gen_lst_it = GenlistItem(item_data={
                'type': 'dir',
                'path': path,
                'd': name
            },
                                     item_class=DIRGLIC,
                                     func=self.list_it_selected)
        else:
            gen_lst_it = GenlistItem(item_data={
                'type': 'file',
                'path': path,
                'd': name
            },
                                     item_class=FILEGLIC,
                                     func=self.list_it_selected)
        gen_lst_it.append_to(self.file_lst)

    def cb_file_lst(self, obj, item=None, event=None):
        '''File list double clicked callback'''
        if item.data['type'] == 'dir':
            self.add_btn.disabled = True
            self.rm_btn.disabled = True
            self.populate_files(item.data['path'] + item.text)
        else:
            self.cb_action_btn(self.action_btn)

    # pylint: disable=no-self-use
    def get_gtk_bookmarks(self):
        '''Read GTK bookmarks'''
        try:
            with open(os.path.expanduser('~/.config/gtk-3.0/bookmarks'),
                      'r') as gtk_bk:
                bks = []
                for url in gtk_bk:
                    url = url.split(' ')[0]
                    url = url.replace('%20', ' ')
                    url = url.strip()
                    bks.append(url)
                return bks
        except IOError:
            return []

    def cb_bookmarks_lst(self, obj, item=None, event=None):
        '''Bookamrk list item double clicked callback'''
        item.selected_set(False)
        self.add_btn.disabled = True
        self.rm_btn.disabled = True
        self.populate_files(item.data['path'])

    def list_it_selected(self, item, gen_lst, data):
        '''Genlist item selected'''
        if item.data['type'] == 'dir':
            self.dir_selected(item)
        else:
            self.file_selected(item.text)
            item.selected_set(False)

    def file_selected(self, cur):
        '''File was selected, update everything'''
        self.file_entry.text = cur
        self.add_btn.disabled = True
        self.rm_btn.disabled = True
        self.selected_dir = None

        # Update image preview if an image is selected
        if cur[-3:] in ['jpg', 'png', 'gif']:
            if self.filepath_en.text == 'recent://':
                self.preview.file_set(self.recent[cur])
            else:
                self.preview.file_set(f'{self.filepath_en.text}/{cur}')
            self.preview.size_hint_weight = (1.0, 0.4)
        else:
            self.preview.size_hint_weight = (0, 0)

    def dir_selected(self, btn):
        '''Folder was selected, update everything'''
        cur = btn.data['path']
        if btn == self.selected_dir:
            self.populate_files(cur)
            self.add_btn.disabled = True
        else:
            self.selected_dir = btn
            gtk_bks = self.get_gtk_bookmarks()
            to_append = f'file://{self.filepath_en.text}{self.selected_dir.text}'
            if to_append not in gtk_bks:
                self.add_btn.disabled = False
                self.rm_btn.disabled = True
            else:
                self.add_btn.disabled = True
                self.rm_btn.disabled = False

    def cb_up_btn(self, btn):
        '''Callback for dir up button'''
        cur = self.filepath_en.text.split('/')
        del cur[-1]
        del cur[-1]
        self.populate_files('/'.join(cur))

    def cb_add_btn(self, btn):
        '''Add dir button pressed'''
        safe = self.selected_dir.text.replace(' ', '%20')
        cur = f"file://{self.filepath_en.text}{safe}"

        con = Icon(self,
                   size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        con.standard_set('gtk-directory')
        con.show()
        current = self.bookmarks_lst.item_append(self.selected_dir.text,
                                                 icon=con)
        current.data[
            'path'] = f'{self.filepath_en.text}{self.selected_dir.text}'
        self.bookmarks_lst.go()

        self.add_btn.disabled = True
        self.rm_btn.disabled = False

        with open(os.path.expanduser('~/.config/gtk-3.0/bookmarks'),
                  'a') as gtk_bk:
            gtk_bk.write(cur + ' ' + self.selected_dir.text + '\n')

    def cb_remove(self, btn):
        '''Remove button pressed callback'''
        cur = f'file://{self.filepath_en.text}{self.selected_dir.text}'
        bks = self.get_gtk_bookmarks()
        bks.remove(cur)

        with open(os.path.expanduser('~/.config/gtk-3.0/bookmarks'),
                  'w') as gtk_bk:
            for url in bks:
                name = url.split('/')[-1]
                url = url.replace(' ', '%20')
                gtk_bk.write(url + ' ' + name + '\n')

        self.bookmarks_lst.clear()
        self.populate_bookmarks()

        self.add_btn.disabled = False
        self.rm_btn.disabled = True

    def set_mode(self, mode):
        '''Set FileSelector mode: save or open'''
        self.mode = mode.lower()
        self.action_btn.text = f'{mode}  '
        self.action_ic.standard_set(f'document-{mode.lower()}')

        if self.mode != 'save':
            self.create_dir_btn.hide()
        else:
            self.create_dir_btn.show()

    def cb_events(self, obj, src, event_type, event):
        '''Keyboard event callback: Watch key presses for ctrl+l to select entry'''
        if event.modifier_is_set(
                'Control') and event_type == EVAS_CALLBACK_KEY_DOWN:
            if event.key.lower() == 'l':
                self.filepath_en.focus_set(True)
                self.filepath_en.cursor_end_set()

    def cb_toggle_hidden(self, btn):
        '''Toggle hidden files and folders'''
        self.show_hidden = not self.show_hidden
        self.populate_files(self.filepath_en.text)

    def callback_cancel_add(self, callback):
        '''Add a cancel callback'''
        self.cancel_cb = callback

    def callback_activated_add(self, callback):
        '''Add an action callback'''
        self.action_cb = callback

    def callback_directory_open_add(self, callback):
        '''Add an open folder callback'''
        self.cb_dir_change = callback

    def cb_cancel_btn(self, btn):
        '''Cancel button callback'''
        if self.cancel_cb:
            self.cancel_cb(self)

    def cb_action_btn(self, btn):
        '''Action button callback'''
        if self.action_cb:
            if not self.dir_only and self.file_entry.text:
                if self.filepath_en.text == 'recent://':
                    self.action_cb(self, self.recent[self.file_entry.text])
                else:
                    self.action_cb(
                        self, f'{self.filepath_en.text}{self.file_entry.text}')
            elif self.dir_only:
                self.action_cb(self, f'{self.filepath_en.text}')

    def cb_file_entry(self, entry):
        '''File entry callback'''
        typed = entry.text.split('/')[-1]
        new_lst = []
        self.focused_entry = entry
        if entry == self.filepath_en:
            for name in self.cur_subdirs:
                if typed in name:
                    if len(new_lst) < 10:
                        new_lst.append(name)
                    else:
                        break
        else:
            for name in self.cur_files:
                if typed in name:
                    if len(new_lst) < 10:
                        new_lst.append(name)
                    else:
                        break

        if self.autocomplete_hover.expanded_get():
            self.autocomplete_hover.hover_end()
        self.autocomplete_hover.clear()

        for name in new_lst:
            self.autocomplete_hover.item_add(name)

        self.autocomplete_hover.hover_begin()
        self.focused_entry.focus = True

    def cb_hover(self, hov, item):
        '''Autocomplete Hover item selected callback'''
        hov.hover_end()
        if self.focused_entry == self.filepath_en:
            self.populate_files(f'{self.cur_dir}{item.text}')
            self.filepath_en.cursor_end_set()
        else:
            self.file_entry.text = item.text
            self.file_entry.cursor_end_set()

    def cb_filepath_en(self, entry):
        '''File Path Entry callback'''
        if os.path.isdir(entry.text) and entry.text != self.cur_dir:
            self.populate_files(entry.text)
            self.filepath_en.cursor_end_set()
        else:
            # entry.text = self.cur_dir
            pass

    def selected_get(self):
        '''Return selected'''
        return f'{self.filepath_en.text}{self.file_entry.text}'
