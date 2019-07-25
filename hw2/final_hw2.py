from Tkinter import Tk, Button, Label
from tkFont import Font
from copy import deepcopy
import time, random, tkMessageBox
import thread

CELL_COLOR = {
    0: 'lightgray', 2: 'lightblue', 4: 'pink', 8: 'brown', 16: 'gold',\
    32: 'blue', 64: 'white',  128: 'gray', 256: 'red', 512: 'orange', \
    1024: 'yellow', 2048: 'green'
}

class Board:
    def __init__(self, other = None):
        self.size = 4
        self.fields = {}
        self.record = {}
        self.zero = {}
        for x in range(self.size):
            for y in range(self.size):
                self.fields[x, y] = 0
                self.zero[x, y] = 0
        if other:
            self.__dict__ = deepcopy(other.__dict__)

    def zip_and_merge(self, row):
        #zip -> merge -> zip
        def zip(row):
            new = [0, 0, 0, 0]
            i = 0
            for r in row:
                if r != 0:
                    new[i] = r
                    i += 1
            return new
        def merge(row):
            jump = False
            for i in range(self.size - 1):
                if jump:
                    jump = False
                    continue
                else:
                    if row[i] == row[i+1]:
                        row[i+1] = 2 * row[i]
                        row[i] = 0
                        jump = True
            return row
        return zip(merge(zip(row)))

    def left(self, field):
        new = {}
        for x in range(self.size):
            row = []
            for y in range(self.size):
                row.append(field[x, y])
            row = self.zip_and_merge(row)
            for y in range(self.size):
                new[x, y] = row[y]
        return new

    def right(self, field):
        return self.reverse(self.left(self.reverse(field)))
        
    def up(self, field):
        return self.transport(self.left(self.transport(field)))

    def down(self, field):
        return self.transport(self.right(self.transport(field)))    
    
    def transport(self, field):
        newField = {}
        for x, y in field:
            newField[x, y] = field[y, x]
        return newField

    def reverse(self, field):
        newField = {}
        for x, y in field:
            newField[x, y] = field[x, self.size-1-y]
        return newField

    def move(self, dir):
        board = Board(self)
        #dir 0:l, 1:r, 2:u, 3:d, 4:s
        if dir == 0:
            if board.fields != self.left(board.fields) or board.fields == self.zero:
                board.record = deepcopy(board.fields)
                board.fields = self.left(board.fields)
                board.fields = self.randomNext(board.fields)
        elif dir == 1:
            if board.fields != self.right(board.fields) or board.fields == self.zero:
                board.record = deepcopy(board.fields)
                board.fields = self.right(board.fields)
                board.fields = self.randomNext(board.fields)
        elif dir == 2:
            if board.fields != self.up(board.fields) or board.fields == self.zero:
                board.record = deepcopy(board.fields)
                board.fields = self.up(board.fields)
                board.fields = self.randomNext(board.fields)
        elif dir == 3:
            if board.fields != self.down(board.fields) or board.fields == self.zero:
                board.record = deepcopy(board.fields)
                board.fields = self.down(board.fields)
                board.fields = self.randomNext(board.fields)
        elif dir == 4:
            board.fields = deepcopy(board.record)
        return board
    
    def checkStatus(self, field):
        #status 0:lose, 1:continue, 2:win
        for x, y in field:
            if field[x, y] == 2048:
                return 2
            elif field[x, y] == 0:
                return 1
        for i in range(self.size):
            for j in range(self.size - 1):
                if field[i, j] == field[i, j+1]:
                    return 1
                if field[j, i] == field[j+1, i]:
                    return 1
        return 0 

    def randomNext(self, field):
        empty = []
        numlist = [2, 4]
        for x, y in field:
            if field[x, y] == 0:
                empty.append((x, y)) 
        if len(empty) == 0:
            return field
        else:
            position = random.choice(empty)
            num = random.choice(numlist)
            field[position] = num
            return field

    def countScore(self, field):
        max_num = 0
        for x, y in field:
            max_num = max(max_num, field[x, y]) 
        if max_num < 128:
            return 5
        elif max_num == 128:
            return 10
        elif max_num == 256:
            return 15
        elif max_num == 512:
            return 20
        elif max_num >= 1024:
            return 25

class GUI:
    def __init__(self):
        self.app = Tk()
        self.app.title('2048')
        self.app.resizable(width = False, height = False)
        self.app.bind('<KeyPress>', self.eventhandler)
        self.board = Board()
        self.font = Font(family = 'Helvetica', size = 32)
        self.buttons = {}
        for x, y in self.board.fields:
            button = Button(self.app, font = self.font, width = 4, height = 2)
            button.grid(row = x, column = y)
            self.buttons[x, y] = button
        AIhandler = lambda: self.thread(self.AI)
        button = Button(self.app, text = 'AI play', command = AIhandler)
        button.grid(row = self.board.size + 1, column = 0, columnspan = self.board.size, sticky = 'WE')
        self.update()

    def eventhandler(self, event):
        if event.keysym == 'Left':
            self.board = self.board.move(0)
        elif event.keysym == 'Right':
            self.board = self.board.move(1)
        elif event.keysym == 'Up':
            self.board = self.board.move(2)
        elif event.keysym == 'Down':
            self.board = self.board.move(3)
        elif event.keysym == 'space':
            self.board = self.board.move(4)
        self.update()
        status = self.board.checkStatus(self.board.fields)
        if status == 0:
            tkMessageBox.showinfo(title = 'Game over', message = 'your score is ' + str(self.board.countScore(self.board.fields)))

    def thread(self, func, *args):
        thread.start_new_thread(func, args)

    def AI(self):
        end = False
        moves = [0, 3]   #l, d
        others = [1, 2]
        while True:
            count = 0
            if end:
                break
            for i in moves:
                new = self.board.move(i)
                if self.board.fields == new.fields:
                    count += 1
                    continue
                self.board = new
                self.update()
                status = self.board.checkStatus(self.board.fields)
                if status == 0:
                    end = True
                    tkMessageBox.showinfo(title = 'Game over', message = 'your score is ' + str(self.board.countScore(self.board.fields)))
                    break
                time.sleep(0.5)
            if count >= 2:
                for i in others:
                    new = self.board.move(i)
                    if self.board.fields == new.fields:
                        continue
                    else:
                        self.board = new
                        self.update()
                        status = self.board.checkStatus(self.board.fields)
                        if status == 0:
                            end = True
                            tkMessageBox.showinfo(title = 'Game over', message = 'your score is ' + str(self.board.countScore(self.board.fields)))
                            break
                        time.sleep(0.5)
                        break
                    

    def update(self):
        for (x, y) in self.board.fields:
            text = self.board.fields[x, y]
            self.buttons[x, y]['text'] = text
            self.buttons[x, y]['bg'] = CELL_COLOR[self.board.fields[x, y]]
            if self.board.fields[x, y] == 0:
                self.buttons[x, y]['fg'] = 'lightgray'
            else:
                self.buttons[x, y]['fg'] = 'black'
    
    def mainloop(self):
        self.app.mainloop()

GUI = GUI()
GUI.mainloop()


