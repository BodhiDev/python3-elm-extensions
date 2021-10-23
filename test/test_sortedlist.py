'''Test SortedList widget'''
import random
import efl.elementary as elm
from efl.elementary.button import Button
from efl.elementary.label import Label
from efl.elementary.window import StandardWindow
# pylint: disable=no-name-in-module
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from elmextensions import SortedList

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

# Defines how large our table generated will be
ROWS = 50
COLUMNS = 5


# pylint: disable=too-few-public-methods
class MainWindow(object):
    '''Window for SortedList'''

    def __init__(self):
        win = StandardWindow("Testing", "Elementary Sorted Table")
        # pylint: disable=no-member
        win.callback_delete_request_add(lambda o: elm.exit())
        # Build the titles for the table. The titles is a list of tuples
        #   with the following format:
        #       ( <str - Header Text>, <Bool - Sortable> )'''
        titles = []
        for i in range(COLUMNS):
            titles.append(("Column " + str(i), True if i != 2 else False))

        # Create our sorted list object
        slist = SortedList(win,
                           titles=titles,
                           size_hint_weight=EXPAND_BOTH,
                           size_hint_align=FILL_BOTH)

        # Populate the rows in our table
        for _i in range(ROWS):
            # Each row is a list with the number of elements
            #   that must equal the number of headers
            row = []
            for j in range(COLUMNS):
                # Row elements can be ANY elementary object
                if j == 0:
                    # For the first column in each row, we will create a button
                    #    that will delete the row when pressed
                    btn = Button(slist,
                                 size_hint_weight=EXPAND_BOTH,
                                 size_hint_align=FILL_BOTH)
                    btn.text = "Delete row"
                    btn.callback_clicked_add(
                        lambda x, y=row: slist.row_unpack(y, delete=True))
                    btn.show()
                    # Add the btn created to our row
                    row.append(btn)
                else:
                    # For each other row create a label with a random number
                    data = random.randint(0, ROWS * COLUMNS)
                    label = Label(slist,
                                  size_hint_weight=EXPAND_BOTH,
                                  size_hint_align=FILL_BOTH)
                    label.text = str(data)
                    # For integer data we also need to assign value to "sort_data"
                    #     because otherwise things get sorted as text
                    label.data["sort_data"] = data
                    label.show()
                    # Append our label to the row
                    row.append(label)
            # Add the row into the SortedList
            slist.row_pack(row, sort=False)

        # Show the list
        slist.show()
        win.resize_object_add(slist)
        win.resize(600, 400)
        win.show()


if __name__ == "__main__":
    GUI = MainWindow()
    # pylint: disable=no-member
    elm.run()
    elm.shutdown()
