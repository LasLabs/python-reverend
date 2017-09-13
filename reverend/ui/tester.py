# This module is part of the Divmod project and is Copyright 2003 Amir Bakhtiar:
# amir@divmod.org.  This is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
#

from __future__ import generators
from Tkinter import *
import tkFileDialog
import tkSimpleDialog
import tkMessageBox
import os
import time


class TestView(Frame):

    def __init__(self, parent=None, guesser=None, app=None):
        Frame.__init__(self, parent)
        self.pack()
        self.guesser = guesser
        self.app = app
        self.size = 300
        self.setup_views()

    def setup_views(self):
        line = Frame(self, relief=RAISED, borderwidth=1)
        line.pack(side=TOP, padx=2, pady=1)
        col_headings = [('Guesses', 8), ('Right', 8), ('Wrong', 8), ('Accuracy %', 10)]
        curr_col = 0
        for text, width in col_headings:
            l = Label(line, text=text, width=width, bg='lightblue')
            l.grid(row=0, column=curr_col)
            curr_col += 1
        line = Frame(self)
        line.pack(fill=X)

        i_guess = IntVar()
        i_right = IntVar()
        i_wrong = IntVar()
        i_acc = IntVar()
        self.model = (i_guess, i_right, i_wrong, i_acc)

        l = Label(line, textvariable=i_guess, anchor=E, width=8, relief=SUNKEN)
        l.grid(row=0, column=0)
        l = Label(line, textvariable=i_right, anchor=E, width=8, relief=SUNKEN)
        l.grid(row=0, column=1) 
        l = Label(line, textvariable=i_wrong, anchor=E, width=8, relief=SUNKEN)
        l.grid(row=0, column=2)   
        l = Label(line, textvariable=i_acc, anchor=E, width=8, relief=SUNKEN)
        l.grid(row=0, column=3)   
        bp = Button(self, text="Run Test", command=self.run_test)
        bp.pack(side=BOTTOM)

        canvas = Canvas(self, width=self.size, height=self.size, bg='lightyellow')
        canvas.pack(expand=YES, fill=BOTH, side=BOTTOM)
        self.canvas = canvas
        
#       slid = Scale(self, label='Wrong', variable=iWrong, to=400, orient=HORIZONTAL, bg='red')
#       slid.pack(side=BOTTOM)
#       slid = Scale(self, label='Right', variable=iRight, to=400, orient=HORIZONTAL, bg='green')
#       slid.pack(side=BOTTOM)

    def run_test(self):
        if len(self.guesser) == 0:
            tkMessageBox.showwarning('Underprepared for examination!',
                                     'Your guesser has had no training. Please train and retry.')
            return
        path = tkFileDialog.askdirectory()
        if not path:
            return
        answer = tkSimpleDialog.askstring('Which Pool do these items belong to?', 'Pool name?',
                                          parent=self.app)

        if not answer:
            return
        if answer not in self.guesser.pools:
            return
        
        de = DirectoryExam(path, answer, self.app.itemClass)
        test_count = len(de)
        scale = self.calc_scale(test_count)
        x = 0
        y = 0
        cum_time = 0
        i_guess, i_right, i_wrong, i_acc = self.model
        for m, ans in de:
            then = time.time()
            g = self.guesser.guess(m)
            cum_time += time.time() - then
            if g:
                g = g[0][0]
                i_guess.set(i_guess.get()+1)
                if g == ans:
                    col = 'green'
                    i_right.set(i_right.get()+1)
                else:
                    col = 'red'
                    i_wrong.set(i_wrong.get()+1)
                i_acc.set(round(100 * i_right.get()/float(i_guess.get()), 3))

            # Plot squares
            self.canvas.create_rectangle(x*scale,y*scale,(x+1)*scale,(y+1)*scale,fill=col)
            if not divmod(i_guess.get(),(int(self.size/scale)))[1]:
                # wrap
                x = 0
                y += 1
            else:
                x += 1
                
            self.update_idletasks()
        guesses = i_guess.get()
        self.app.status.log('%r guesses in %.2f seconds. Avg: %.2f/sec.' % (guesses, cum_time,
                                                                        round(guesses/cum_time, 2)))

    def calc_scale(self, testCount):
        import math
        scale = int(self.size/(math.sqrt(testCount)+1))
        return scale

    
class DirectoryExam(object):
    """Creates a iterator that returns a pair at a time.
    (Item, correctAnswer). This Exam creates items from
    a directory and uses the same answer for each.
    """
    
    def __init__(self, path, answer, item_class):
        self.path = path
        self.answer = answer
        self.item_class = item_class

    def __iter__(self):
        files = os.listdir(self.path)
        for file_name in files:
            fp = open(os.path.join(self.path, file_name), 'rb')
            try:
                item = self.item_class.from_file(fp)
            finally:
                fp.close()
            if item is None:
                continue
            yield (item, self.answer)

    def __len__(self):
        files = os.listdir(self.path)
        return len(files)
