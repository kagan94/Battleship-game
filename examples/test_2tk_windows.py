import tkMessageBox
from Tkinter import *
import time

class Notif:
    def __init__(self):
        self.root = Tk()
        self.root.title("Enter a nickname")

        self.frame = Frame(self.root)
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.pack(pady=10, padx=10)

        self.name = Label(self.root, text="Enter a nickname")
        self.name.pack()
        self.nickname = StringVar()
        self.e = Entry(self.root, textvariable=self.nickname)
        self.e.pack()

        # command = on_nickname_submit

        self.check_nick_button = Button(self.root, text="Choose")
        self.check_nick_button.pack()

        # while True:
        #     self.root.update_idletasks()
        #     self.root.update()
        #     time.sleep(0.1)

        self.temp_mainloop_p = Thread(target=loop, args=(self.root,))
        self.temp_mainloop_p.setDaemon(True)
        self.temp_mainloop_p.start()

def loop(root):
    while True:
        root.update_idletasks()
        root.update()
        time.sleep(0.1)

    # s = Thread(target=root.mainloop)
    # s.setDaemon(True)
    # s.start()

    # root.mainloop()



#
# def nickname_windop():
#     root = Tk()
#     root.title("Enter a nickname")
#
#     frame = Frame(root)
#     frame.grid(column=0, row=0, sticky=(N, W, E, S))
#     frame.columnconfigure(0, weight=1)
#     frame.rowconfigure(0, weight=1)
#     frame.pack(pady=10, padx=10)
#
#     name = Label(root, text="Enter a nickname")
#     name.pack()
#     nickname = StringVar()
#     e = Entry(root, textvariable=nickname)
#     e.pack()
#
#     # command = on_nickname_submit
#
#     check_nick_button = Button(root, text="Choose")
#     check_nick_button.pack()
#
#     # root.mainloop()
#
#     temp_mainloop_p = Thread(target=root.mainloop)
#     temp_mainloop_p.setDaemon(True)
#     temp_mainloop_p.start()
#
#
#     s = Thread(target=root.mainloop)
#     s.setDaemon(True)
#     s.start()
#

from threading import Thread


print 111

s = Notif()

print 222
s2 = Notif()

# nickname_window()
# nickname_window()

# nickname_window()


# class Demo2(Toplevel):
#     def __init__(self):
#         Toplevel.__init__(self)
#         self.title("Demo 2")
#         self.button = Button(self, text="Button 2", # specified self as master
#                                 width=25, command=self.close_window)
#         self.button.pack()
#
#
#
#
#     def close_window(self):
#         self.destroy()
#
# Demo2()
# Demo2()

# temp_mainloop_p = Thread(target=nickname_window)
# temp_mainloop_p.setDaemon(True)
# temp_mainloop_p.start()
#
# ss = Thread(target=nickname_windop)
# ss.setDaemon(True)
# ss.start()









# import Tkinter as tk
#
# class Demo1:
#     def __init__(self, master):
#         self.master = master
#         self.frame = tk.Frame(self.master)
#         self.button1 = tk.Button(self.frame, text = 'New Window', width = 25, command = self.new_window)
#         self.button1.pack()
#         self.frame.pack()
#
#     def new_window(self):
#         self.newWindow = tk.Toplevel(self.master)
#         self.app = Demo2(self.newWindow)
#
# class Demo2:
#     def __init__(self, master):
#         self.master = master
#         self.frame = tk.Frame(self.master)
#         self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
#         self.quitButton.pack()
#         self.frame.pack()
#     def close_windows(self):
#         self.master.destroy()
#
# def main():
#     root = tk.Tk()
#
#     # newWindow = tk.Toplevel(root)
#     # app = Demo2(newWindow)
#
#     app = Demo1(root)
#     root.mainloop()
#
# if __name__ == '__main__':
#     main()