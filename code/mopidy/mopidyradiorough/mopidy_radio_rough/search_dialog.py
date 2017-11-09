from tkinter import *
from ttkthemes import themed_tk as tk 
from tkinter import ttk
import os

# search input dialog
class Search(Toplevel):

    def __init__(self,parent,title='search'):

        Toplevel.__init__(self,parent)
        self.title(title)
        self.transient(parent)
        self.searchtext=''
        self.parent=parent

        self.searchbox=ttk.Entry(self)
        self.searchbox.pack(side=LEFT,padx=5)
        w=Button(self, text='search',
            command=self.search,height=1)
        w.pack(side=LEFT,padx=5, pady=5)

        self.bind("<Return>", self.search)
        self.bind("<Escape>", self.cancel)

        self.grab_set()
        self.initial_focus = self.searchbox

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def search(self, event=None):
        self.searchtext=self.searchbox.get()
        self.withdraw()
        self.update_idletasks()
        self.cancel()

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

