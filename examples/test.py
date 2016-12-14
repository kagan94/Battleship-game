# from ocempgui.widgets import *
# from ocempgui.widgets.components import TextListItem
# from ocempgui.widgets.Constants import *
#
# __count = 0
#
# def _add_item (slist):
#     global __count
#     slist.items.append (TextListItem ("SrolledList element %d" % __count))
#     __count += 1
#
# def _remove_item (slist, button2):
#     selection = slist.get_selected ()
#     for item in selection:
#         slist.items.remove (item)
#     button2.sensitive = False
#
# def _update_button (slist, button):
#     button.sensitive = len (slist.get_selected ()) > 0
#
# def create_scrolledlist_view ():
#     # Create a ScrolledList with always scrolling and single selection.
#     always = ScrolledList (200, 200)
#     always.scrolling = SCROLL_ALWAYS
#     always.selectionmode = SELECTION_SINGLE
#     for i in xrange (15):
#         item = None
#         if i % 2 == 0:
#             item = TextListItem ("Short item %d" % i)
#         else:
#             text = "Very, " +3 * "very, very," + "long item %d" % i
#             item = TextListItem (text)
#         always.items.append (item)
#
#     return always
#
# if __name__ == "__main__":
#     # Initialize the drawing window.
#     re = Renderer ()
#     re.create_screen (620, 500)
#     re.title = "ScrolledList examples"
#     re.color = (234, 228, 223)
#     table = create_scrolledlist_view ()
#     table.topleft = 5, 5
#     re.add_widget (table)
#     re.start ()




# Hello World example.
from ocempgui.widgets import *

# Initialize the drawing window.
re = Renderer ()
re.create_screen (100, 50)
re.title = "Hello World"
re.color = (250, 250, 250)

button = Button ("Hello World")
button.topleft = (10, 10)
re.add_widget (button)

# Start the main rendering loop.
re.start ()