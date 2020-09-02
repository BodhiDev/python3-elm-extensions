'''A SortedList Widget for EFL'''
from efl.elementary.box import Box
from efl.elementary.button import Button
from efl.elementary.label import Label
from efl.elementary.panes import Panes
from efl.elementary.scroller import Scroller, ELM_SCROLLER_POLICY_OFF,\
     ELM_SCROLLER_POLICY_AUTO
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5


# pylint: disable=too-many-instance-attributes
class SortedList(Scroller):
    '''
    A "spread sheet like" widget for elementary.
    Argument "titles" is a list, with each element being a tuple:
    (<Display Text>, <Sortable>)
    '''

    def __init__(self,
                 parent_widget,
                 *args,
                 titles=None,
                 initial_sort=0,
                 ascending=True,
                 **kwargs):
        Scroller.__init__(self, parent_widget, *args, **kwargs)
        self.policy_set(ELM_SCROLLER_POLICY_AUTO, ELM_SCROLLER_POLICY_OFF)

        self.main_box = Box(self,
                            size_hint_weight=EXPAND_BOTH,
                            size_hint_align=FILL_BOTH)
        self.main_box.show()

        self.header = titles
        self.sort_column = initial_sort
        self.sort_column_ascending = ascending

        self.rows = []
        self.header_row = []

        header = Panes(self,
                       size_hint_weight=EXPAND_HORIZ,
                       size_hint_align=FILL_HORIZ)
        header.callback_unpress_add(self.cb_resize_pane)
        header.show()

        list_pane = Panes(self,
                          size_hint_weight=EXPAND_BOTH,
                          size_hint_align=FILL_BOTH)
        list_pane.callback_unpress_add(self.cb_resize_pane)
        list_pane.style_set("flush")
        list_pane.show()

        header.data["related"] = list_pane
        list_pane.data["related"] = header

        self.scroller = Scroller(self,
                                 size_hint_weight=EXPAND_BOTH,
                                 size_hint_align=FILL_BOTH)
        self.scroller.policy_set(ELM_SCROLLER_POLICY_OFF,
                                 ELM_SCROLLER_POLICY_AUTO)
        self.scroller.content = list_pane
        self.scroller.show()

        self.headers = []
        self.headers.append(header)
        self.list_panes = []
        self.list_panes.append(list_pane)
        self.lists = []

        if titles is not None:
            self.header_row_pack(titles)

        self.main_box.pack_end(header)
        self.main_box.pack_end(self.scroller)

        self.content = self.main_box
        self.show()

    def header_row_pack(self, titles):
        '''Takes a list (or a tuple) of tuples (string, bool, int) and packs them to
        the first row of the table.'''

        assert isinstance(titles, (list, tuple))
        for _t in titles:
            assert isinstance(_t, tuple)
            assert len(_t) == 2
            title, sortable = _t
            assert isinstance(title, str)
            assert isinstance(sortable, bool)

        def cb_sort_btn(button, col):
            '''Aux function'''
            if self.sort_column == col:
                self.reverse()
            else:
                self.sort_by_column(col)

        title_cnt = len(titles)
        for count, flag in enumerate(titles):
            title, sortable = flag
            btn = Button(self,
                         size_hint_weight=EXPAND_HORIZ,
                         size_hint_align=FILL_HORIZ,
                         text=title)
            btn.callback_clicked_add(cb_sort_btn, count)
            if not sortable:
                btn.disabled = True
            btn.show()
            self.header_row.append(btn)

            box = Box(self,
                      size_hint_weight=EXPAND_BOTH,
                      size_hint_align=FILL_BOTH)
            box.show()

            if len(self.list_panes) < title_cnt:
                wdth = 1.0 / (title_cnt - count)
                self.list_panes[count].part_content_set("left", box)
                self.list_panes[count].content_left_size = wdth

                next_list = Panes(self,
                                  size_hint_weight=EXPAND_BOTH,
                                  size_hint_align=FILL_BOTH)
                next_list.callback_unpress_add(self.cb_resize_pane)
                next_list.style_set("flush")
                next_list.show()

                self.list_panes[count].part_content_set("right", next_list)
                self.list_panes.append(next_list)

                self.headers[count].part_content_set("left", btn)
                self.headers[count].content_left_size = wdth

                next_header = Panes(self,
                                    size_hint_weight=EXPAND_HORIZ,
                                    size_hint_align=FILL_HORIZ)
                next_header.callback_unpress_add(self.cb_resize_pane)
                next_header.show()

                self.headers[count].part_content_set("right", next_header)
                self.headers.append(next_header)

                next_list.data["related"] = next_header
                next_header.data["related"] = next_list
            else:
                self.list_panes[count - 1].part_content_set("right", box)
                self.headers[count - 1].part_content_set("right", btn)

            self.lists.append(box)

    # pylint: disable=no-self-use
    def cb_resize_pane(self, obj):
        '''Resize display pane'''
        left = obj.content_left_size
        right = obj.content_right_size
        related = obj.data["related"]

        related.content_left_size = left
        related.content_right_size = right

    def row_pack(self, row, sort=True):
        '''Takes a list of items and packs them to the table.'''

        assert len(row) == len(self.header_row), (
            "The row you are trying to add to this sorted list has the wrong "
            "number of items! expected: %i got: %i" %
            (len(self.header_row), len(row)))

        self.rows.append(row)
        self.add_row(row)

        if sort:
            self.sort_by_column(self.sort_column)

    def add_row(self, row):
        '''Add Row to list'''
        # print("Test %s"%row)
        for count, item in enumerate(row):
            self.lists[count].pack_end(item)

    def row_unpack(self, row, delete=False):
        '''Unpacks and hides, and optionally deletes, a row of items.
        The argument row can either be the row itself or its index number.
        '''
        if isinstance(row, int):
            row_index = row
        else:
            row_index = self.rows.index(row) + 1

        # print("row index: " + str(row_index-1))
        # print("length: " + str(len(self.rows)))
        # print("sort_data: " + str(row[self.sort_column].data["sort_data"]))

        row = self.rows.pop(row_index - 1)

        for count, item in enumerate(row):
            self.lists[count].unpack(item)
            if delete:
                item.delete()
            else:
                item.hide()

        self.sort_by_column(self.sort_column,
                            ascending=self.sort_column_ascending)

    def unpack_all(self):
        '''Clear row'''
        tmplist = list(self.rows)
        for row in tmplist:
            self.row_unpack(row)

    def reverse(self):
        '''Reverse list'''
        rev_order = reversed(list(range(len(self.rows))))
        for box in self.lists:
            box.unpack_all()

        for new_y in rev_order:
            self.add_row(self.rows[new_y])

        label = self.header_row[self.sort_column].part_content_get("icon")
        if label is not None:
            if self.sort_column_ascending:
                label.text = u"⬆"
                self.sort_column_ascending = False
            else:
                label.text = u"⬇"
                self.sort_column_ascending = True

        self.rows.reverse()

    def sort_by_column(self, col, ascending=True):
        '''Sort column'''
        assert col >= 0
        assert col < len(self.header_row)

        self.header_row[self.sort_column].icon = None

        btn = self.header_row[col]
        label = Label(btn)
        btn.part_content_set("labelon", label)
        label.show()

        if ascending:  # sascending:
            label.text = u"⬇"
            self.sort_column_ascending = True
        else:
            label.text = u"⬆"
            self.sort_column_ascending = False

        orig_col = [
            (i, x[col].data.get("sort_data", x[col].text))
            for i, x in enumerate(self.rows)
            ]
        sorted_col = sorted(orig_col, key=lambda e: e[1])
        new_order = [x[0] for x in sorted_col]

        if not ascending:
            new_order.reverse()

        for box in self.lists:
            box.unpack_all()

        for new_y in new_order:
            self.add_row(self.rows[new_y])

        self.rows.sort(key=lambda e: e[col].data.get("sort_data", e[col].text))
        self.sort_column = col

    def update(self):
        '''Update'''
        self.sort_by_column(self.sort_column, self.sort_column_ascending)
