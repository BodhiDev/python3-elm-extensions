'''A searchable list widget for ELM'''
from efl.elementary.box import Box
from efl.elementary.entry import Entry
from efl.elementary.frame import Frame
from efl.elementary.list import List
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5


def search_list(text, lst):
    '''Case insenstive search function for list'''
    for item in lst:
        if text.lower() in item.lower()[:len(text)]:
            return lst.index(item)
    return 0


class SearchableList(Box):
    '''Searchable list class'''
    def __init__(self, parent_widget, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        self.lst = List(self,
                        size_hint_weight=EXPAND_BOTH,
                        size_hint_align=FILL_BOTH)
        self.keys = []
        self.lst.go()
        self.lst.show()
        self.items = []

        sframe = Frame(self,
                       size_hint_weight=EXPAND_HORIZ,
                       size_hint_align=FILL_HORIZ)
        sframe.text = 'Search'
        self.search = search = Entry(self)
        search.single_line = True
        search.callback_changed_add(self.cb_search)
        search.show()
        sframe.content = search
        sframe.show()

        self.pack_end(self.lst)
        self.pack_end(sframe)

    def callback_item_focused_add(self, callback):
        '''List item focused callback'''
        self.lst.callback_item_focused_add(callback)

    def callback_clicked_double_add(self, callback):
        '''List item doubled clicked callback'''
        self.lst.callback_clicked_double_add(callback)

    def item_append(self, text, icon=None):
        '''Add item to list'''
        self.keys.append(text)
        self.keys.sort()

        current = self.keys.index(text)

        if not self.items or current > len(self.items) - 1:
            item = self.lst.item_append(text, icon=icon)
            self.items.append(item)
        else:
            # print("Inserting after item %s"%self.items[current])
            item = self.lst.item_insert_before(self.items[current],
                                               text,
                                               icon=icon)
            self.items.insert(current, item)

        return item

    def items_get(self):
        '''Return item'''
        return self.lst.items_get()

    def selected_item_get(self):
        '''Return selected item'''
        return self.lst.selected_item_get()

    def cb_search(self, entry):
        '''Search entry callback'''
        zeindex = search_list(entry.text, self.keys)
        self.items[zeindex].selected_set(True)
        self.items[zeindex].bring_in()
        self.search.focus = True
