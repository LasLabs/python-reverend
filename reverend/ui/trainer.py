# This module is part of the Divmod project and is Copyright 2003 Amir Bakhtiar:
# amir@divmod.org.  This is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
#

from Tkinter import *
import tkFileDialog
import tkSimpleDialog
import tkMessageBox

import os

from util import Command, StatusBar, Notebook
from tester import TestView


class PoolView(Frame):

    def __init__(self, master=None, guesser=None, app=None):
        Frame.__init__(self, master, bg='lightblue3')
        self.pack()
        self.list_view = Frame(self)
        self.list_view.pack()
        bp = Button(self, text="New Pool", command=self.new_pool)
        bp.pack(side=LEFT, anchor=SE)
        self.add_load_save()
        self.column_headings()
        self.model = {}
        self.guesser = guesser
        self.app = app
        self.reload()

    def reload(self):
        self.list_view.destroy()
        self.list_view = Frame(self)
        self.list_view.pack()
        for pool in self.guesser.pool_names():
            self.add_pool(self.guesser.pools[pool])
        self.add_pool(self.guesser.corpus, 'Total')

    def upload(self):
        pass
    
    def add_load_save(self):
        frame = Frame(self)
        frame.pack(side=RIGHT)
        bp = Button(frame, text="Upload", command=self.upload, state=DISABLED)
        bp.pack(side=BOTTOM, fill=X)
        bp = Button(frame, text="Save", command=self.save)
        bp.pack(side=BOTTOM, fill=X)
        bp = Button(frame, text="Load", command=self.load)
        bp.pack(side=BOTTOM, fill=X)
    
    def add_pool(self, pool, name=None):
        col = None
        line = Frame(self.list_view)
        line.pack()
        if name is None:
            name = pool.name
            idx = self.guesser.pool_names().index(name)
            col = self.default_colors()[idx]
        l = Label(line, text=name, anchor=W, width=10)
        l.grid(row=0, column=0)
        color_stripe = Label(line, text=' ', width=1, bg=col, anchor=W, relief=GROOVE)
        color_stripe.grid(row=0, column=1)
        train = IntVar()
        train.set(pool.train_count)
        l = Label(line, textvariable=train, anchor=E, width=10, relief=SUNKEN)
        l.grid(row=0, column=2)
        u_tok = IntVar()
        u_tok.set(len(pool))
        l = Label(line, textvariable=u_tok, anchor=E, width=12, relief=SUNKEN)
        l.grid(row=0, column=3)
        t_tok = IntVar()
        t_tok.set(pool.token_count)
        l = Label(line, textvariable=t_tok, anchor=E, width=10, relief=SUNKEN)
        l.grid(row=0, column=4)
        self.model[name] = (pool, u_tok, t_tok, train)

    def refresh(self):
        for pool, ut, tt, train in self.model.values():
            ut.set(len(pool))
            tt.set(pool.token_count)
            train.set(pool.train_count)

    def save(self):
        path = tkFileDialog.asksaveasfilename()
        if not path:
            return
        self.guesser.save(path)
        self.app.dirty = False

    def load(self):
        path = tkFileDialog.askopenfilename()
        if not path:
            return
        self.guesser.load(path)
        self.reload()
        self.app.dirty = False
    
    def new_pool(self):
        p = tkSimpleDialog.askstring('Create Pool', 'Name for new pool?')
        if not p:
            return
        if p in self.guesser.pools:
            tkMessageBox.showwarning('Bad pool name!', 'Pool %s already exists.' % p)
        self.guesser.new_pool(p)
        self.reload()
        self.app.pool_added()
        self.app.status.log('New pool created: %s.' % p, clear=3)

    def column_headings(self):
        title = Label(self, text='Pools', relief=RAISED, borderwidth=1)
        title.pack(side=TOP, fill=X)
        msg_line = Frame(self, relief=RAISED, borderwidth=1)
        msg_line.pack(side=TOP)
        curr_col = 0
        col_headings = [('Name', 10), ('', 1), ('Trained', 10), ('Unique Tokens', 12), ('Tokens', 10)]
        for cHdr, width in col_headings:
            l = Label(msg_line, text=cHdr, width=width, bg='lightblue')
            l.grid(row=0, column=curr_col)
            curr_col += 1

    @staticmethod
    def default_colors(self):
        return ['green', 'yellow', 'lightblue', 'red', 'blue', 'orange', 'purple', 'pink']

            
class Trainer(Frame):

    def __init__(self, parent, guesser=None, item_class=None):
        self.status = StatusBar(parent)
        self.status.pack(side=BOTTOM, fill=X)
        Frame.__init__(self, parent)
        self.pack(side=TOP, fill=BOTH)
        self.items_per_page = 20
        self.rows = []
        for i in range(self.items_per_page):
            self.rows.append(ItemRow())
        self.items = []
        self.files = []
        self.cursor = 0
        self.dirty = False
        if guesser is None:
            from reverend.thomas import Bayes
            self.guesser = Bayes()
        else:
            self.guesser = guesser
        if item_class is None:
            self.item_class = TextItem
        else:
            self.item_class = item_class
        for row in self.rows:
            row.summary.set('foo')
        self.init_views()

    def init_views(self):
        self.nb = Notebook(self)
#       frame1 = Frame(self.nb())
#       self.poolView = PoolView(frame1, guesser=self.guesser, app=self)
#       self.poolView.pack(side=TOP)
        frame2 = Frame(self.nb())
        self.pool_view = PoolView(frame2, guesser=self.guesser, app=self)
        self.pool_view.pack(side=TOP)
        self.list_view = Canvas(frame2, relief=GROOVE)
        self.list_view.pack(padx=3)
        bn = Button(self.list_view, text="Load training", command=self.load_corpus)
        bn.pack(side=RIGHT, anchor=NE, fill=X)
        self.column_headings()
        self.add_next_prev()
        
        frame3 = Frame(self.nb())
        self.test_view = TestView(frame3, guesser=self.guesser, app=self)
        self.test_view.pack()

        frame4 = Frame(self.nb())
        bp = Button(frame4, text="Quit", command=self.quit_now)
        bp.pack(side=BOTTOM)
        
#       self.nb.add_screen(frame1, 'Reverend')
        self.nb.add_screen(frame2, 'Training')
        self.nb.add_screen(frame3, 'Testing')
        self.nb.add_screen(frame4, 'Quit')

    def add_next_prev(self):
        np_frame = Frame(self.list_view)
        np_frame.pack(side=BOTTOM, fill=X)
        bn = Button(np_frame, text="Prev Page", command=self.prev_page)
        bn.grid(row=0, column=0)
        bn = Button(np_frame, text="Next Page", command=self.next_page)
        bn.grid(row=0, column=1)


    def load_corpus(self):
        path = tkFileDialog.askdirectory()
        if not path:
            return
        self.load_file_list(path)
        self.display_items()
        self.display_rows()

    def bulk_test(self):
        dirs = []
        for pool in self.guesser.pool_names():
            path = tkFileDialog.askdirectory()
            dirs.append((pool, path))
        for pool, path in dirs:
            print pool, path
            

    def display_list(self):
        for item in self.items:
            self.itemRow(item)
            
    def display_rows(self):
        for row in self.rows:
            self.display_row(row)

    def load_file_list(self, path):
        listing = os.listdir(path)
        self.files = [os.path.join(path, file) for file in listing]
        self.cursor = 0

    def prev_page(self):
        self.cursor = max(0, self.cursor - self.items_per_page)
        self.display_items()

    def next_page(self):
        self.cursor = min(len(self.files), self.cursor + self.items_per_page)
        self.display_items()
        
    def display_items(self):
        these_files = self.files[self.cursor:self.cursor + self.items_per_page]
        items = []
        for file_path, row in zip(these_files, self.rows):
            fp = open(file_path, 'rb')
            try:
                item = self.item_class.from_file(fp)
            finally:
                fp.close()
            if item is None:
                continue
            items.append(item)
            guesses = self.guesser.guess(item)
            summary = item.summary()
            cols = item.columnDefs()
            s = ''
            for c, ignore in cols:
                s += summary[c] + ' '
            row.initialize(item, s, guesses, self.guesser.pool_names())
        self.items = items
        
    def quit_now(self):
        if self.dirty:
            if tkMessageBox.askyesno("You have unsaved changes!", "Quit without saving?"):
                self.quit()
        self.quit()

    def column_headings(self):
        line = Frame(self.list_view, relief=RAISED, borderwidth=1)
        line.pack(side=TOP, padx=2, pady=1)
        col_headings = self.item_class.columnDefs()
        curr_col = 0
        for cHdr, width in col_headings:
            l = Label(line, text=cHdr, width=width, bg='lightblue')
            l.grid(row=0, column=curr_col)
            curr_col += 1
        line = Frame(self)
        line.pack(fill=X)

    def training(self, row):
        sel = row.selection.get()
        self.guesser.train(sel, row.original)
        row.current = sel
        self.guess_all()

    def guess_all(self):
        self.pool_view.refresh()
        pools = self.guesser.pool_names()
        for row in self.rows:
            row.set_guess(self.guesser.guess(row.original), pools)
            
    def display_row(self, row, bgc=None):
        # UGH - REWRITE!
        line = Frame(self.list_view, bg=bgc)
        line.pack(pady=1)
        row.line = line
        self.insert_radios(row)
        Label(line, text=row.summary.get(), textvariable=row.summary, width=60, bg=bgc,
              anchor=W).grid(row=0, column=2)
#       Label(line, text=row.guess, width=7, bg=bgc, anchor=W).grid(row=0, column=1)
        color_stripe = Label(line, text=' ', width=1, bg=bgc, anchor=W, relief=GROOVE)
        color_stripe.grid(row=0, column=1)
        line.color_stripe = color_stripe
        pools = self.guesser.pool_names()
        row.refresh_color(pools)

    def pool_added(self):
        if not self.items:
            return
        pools = self.guesser.pool_names()
        for row in self.rows:
            for r in row.radios:
                r.destroy()
            self.insert_radios(row)
            row.refresh_color(pools)
        self.dirty = True

    def insert_radios(self, row):
        radio_frame = Frame(row.line)
        radio_frame.grid(row=0, column=0)
        curr_col = 0
        radios = []
        v = row.selection
        ci = 0
        pools = self.guesser.pool_names()
        for pool in pools:
            rb = Radiobutton(radio_frame, text=pool, variable=v, value=pool, command=Command(self.training, row), bg=None)
            rb.grid(row=0, column=curr_col)
            radios.append(rb)
            curr_col += 1
            ci += 1
        row.radios = radios
        

class TextItem(object):

    def __init__(self, text):
        self.text = text
        
    def summary(self):
        return {'Text': self.text}

    def column_names(self):
        return ['Text']

    def lower(self):
        return self.text.lower()

    @classmethod
    def from_file(cls, fp):
        """Return the first line of the file."""
        ti = cls(fp.readline())
        return ti


class ItemRow(object):

    def __init__(self, orig=None):
        self.line = None
        self.radios = []
        self.original = orig
        self.current = ''
        self.guess = []
        self.summary = StringVar()
        self.selection = StringVar()

    def initialize(self, item=None, summary='', guess=None, pools=[]):
        self.selection.set('')
        self.original = item
        self.summary.set(summary)
        self.set_guess(guess, pools)

    def set_guess(self, guess, pools):
        if not guess:
            guess = [['']]
        self.guess = guess
        self.selection.set(self.best_guess())
        self.current = self.best_guess()
        self.refresh_color(pools)

    def refresh_color(self, pools):
        col = None
        if self.guess[0][0] in pools:
            idx = pools.index(self.guess[0][0])
            col = self.default_colors()[idx]
        if self.line:
            self.line.colourStripe.config(bg=col)

    def __repr__(self):
        return self.original.__repr__()

    def default_colors(self):
        return ['green', 'yellow', 'lightblue', 'red', 'blue', 'orange', 'purple', 'pink']

    def best_guess(self):
        if self.guess:
            return self.guess[0][0]
        else:
            return None


if __name__ == "__main__":
    root = Tk()
    root.title('Reverend Trainer')
    root.minsize(width=300, height=300)
    #  root.maxsize(width=600, height=600)
    display = Trainer(root)
    root.mainloop()
