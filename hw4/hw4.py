from Tkinter import Tk, Button, Label
import tkMessageBox
from tkFont import Font
from copy import deepcopy
import random
import thread
import time

class Board:
    #initial the board
    def __init__(self, other = None):
        self.size = 3       #size of board
        self.fields = {}    #dict of board
        self.right = {}     #right location
        self.memField = {}
        self.memStep = 0
        self.step = 0
        self.maps = []
        map1 = {(0, 0):1, (0, 1):5, (0, 2):4, (1, 0):7, (1, 1):9, (1, 2):3, (2, 0):8, (2, 1):2, (2,2):6}
        map2 = {(0, 0):3, (0, 1):5, (0, 2):8, (1, 0):1, (1, 1):9, (1, 2):7, (2, 0):4, (2, 1):6, (2,2):2}
        map3 = {(0, 0):4, (0, 1):3, (0, 2):8, (1, 0):7, (1, 1):9, (1, 2):2, (2, 0):1, (2, 1):5, (2,2):6}
        self.maps.append(map1)
        self.maps.append(map2)
        self.maps.append(map3)
        i = 1
        for x in range(self.size):
            for y in range(self.size):
                self.right[y, x] = i
                i += 1
        self.fields = random.choice(self.maps)
        #copy constructor
        if other:
            self.__dict__ = deepcopy(other.__dict__)

    #update the field
    def move(self, x, y):
        board = Board(self)
        #modify the field and step
        space = self.checkSpace(board.fields, x, y)
        if  space != (3,3):
            board.memStep = board.step
            board.memField = board.fields.copy()
            board.step += 1
            board.fields[space] = board.fields[x, y]
            board.fields[x, y] = 9        
        return board

    def back(self):
        return self.memField, self.memStep
    
    #find space
    def checkSpace(self, field, x, y):
        space = (3, 3)
        if x+1 <= 2 and field[x+1, y] == 9:
            space = (x+1, y)
        elif x-1 >= 0 and field[x-1, y] == 9:
            space = (x-1, y)
        elif y+1 <= 2 and field[x, y+1] == 9:
            space = (x, y+1)
        elif y-1 >= 0 and field[x, y-1] == 9:
            space = (x, y-1) 
        return space

    #check win
    def won(self, field):
        return field == self.right

    def countScore(self, field):
        count = 0
        for (x, y) in field:
            if field[x, y] == self.right[x, y]:
                count += 1
        if count <= 3:
            return count * 10
        else:
            return 30 + (count - 3) * 5

class puzzleAI:
    def __init__(self, board, sx, sy):
        self.board = board
        #position of 9
        self.sx = sx
        self.sy = sy
        #move action of space
        self.command = ['down', 'up', 'right', 'left']
        #move action
        self.dx = [-1, 1, 0, 0]
        self.dy = [0, 0, -1, 1]
        self.rev_dir = [1, 0, 3, 2]  #index of reverse direction
        self.solution = [4] * 40     #right move, 0 ~ 3 mean the direction
    
    #check this board is no solution
    def check_permutation_inversion(self, board):
        inversion = 0
        #check all position
        for a in range(9):
            for b in range(a):
                #position of index a
                i = int(a / 3)   #row
                j = int(a % 3)   #col
                #position of index b
                ii = int(b / 3)  #row
                jj = int(b % 3)  #col
                #number on index a and b is not 0, and num[b] > num[a]
                if board[i][j] and board[ii][jj] and board[i][j] < board[ii][jj]:
                    inversion += 1
        row_number_of_0 = 0
        for a in range(9):
            i = int(a / 3)
            j = int(a % 3)
            if board[i][j] == 0:
                row_number_of_0 = i + 1
                break
        return (inversion + row_number_of_0) % 2 == 0   #odd is no solution

    #heuristic function
    def h(self, board):
        right_pos = [[2,2],[0, 0],[0, 1],[0, 2],[1, 0],[1, 1],[1, 2],[2, 0],[2, 1]]
        cost = 0
        for i in range(3):
            for j in range(3):
                #ignore 0
                if board[i][j]:
                    cost += self.taxicab_distance(i, j, right_pos[board[i][j]][0], right_pos[board[i][j]][1])
        return cost

    #count distance
    def taxicab_distance(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    #check this position is on the board
    def onboard(self, x, y):
        return x >= 0 and x < 3 and y >= 0 and y < 3

    #A* algorithm
    def IDAstar(self, x, y, gx, pre_dir, bound, ans):
        hx = self.h(self.board)
        if gx + hx > bound:     #over bound, return next bound
            return gx + hx, ans
        if hx == 0:             #find the best solution
            ans = True
            return gx, ans
        next_bound = 1000000000
        for i in range(4):      #4 directions
            #new position of space
            nx = x - self.dx[i]
            ny = y - self.dy[i]
            if self.rev_dir[i] == pre_dir:
                continue
            if not self.onboard(nx, ny):
                continue
            self.solution[gx] = i   #record
            #move
            self.board[x][y], self.board[nx][ny] = self.board[nx][ny], self.board[x][y]   #swap
            c, ans = self.IDAstar(nx, ny, gx+1, i, bound, ans)
            if ans:
                return c, ans
            next_bound = min(next_bound, c)
            #reverse
            self.board[x][y], self.board[nx][ny] = self.board[nx][ny], self.board[x][y]   #swap
        return next_bound, ans

    def puzzle(self):
        if not self.check_permutation_inversion(self.board):
            print "no solution"
            return 0, 0
        ans = False
        bound = 0
        while (not ans) and (bound <= 200):
            bound, ans = self.IDAstar(self.sx, self.sy, 0, -1, bound, ans)
        if not ans:
            print "no solution in 200"
            return 1, 0
        #print the result
        for i in range(bound):
            print self.command[self.solution[i]],      
        return self.solution, bound

class GUI:
    #initial the GUI
    def __init__(self):
        self.app = Tk()
        self.app.title('8-puzzle')
        self.app.resizable(width = False, height = False)
        self.font = Font(family = "Helvetica", size = 32)
        self.buttons = {}
        self.board = Board() 
        #reset button
        resetHandler = lambda: self.reset()
        resetButton = Button(self.app, text = 'reset', command = resetHandler)
        resetButton.grid(row = 0, column = 0, columnspan = self.board.size, sticky = 'W', padx = 10, pady = 1)
        #step label
        stepLabel = Label(self.app, text = 'step:', font="Helvetica 20")
        stepLabel.grid(row = 0, column = 1, sticky = 'E')
        self.countLabel = Label(self.app, text = '0', font="Helvetica 20")
        self.countLabel.grid(row = 0, column = 2, sticky = 'E', ipadx = 5)
        #initial board button
        for x, y in self.board.fields:
            handler = lambda x = x, y = y: self.move(x,y)
            button = Button(self.app, command = handler, font = self.font, width = 2, height = 1, cursor = "hand1")
            button.grid(row = y+1, column = x)
            self.buttons[x, y] = button
        #function key
        playHandler = lambda: self.play()
        playButton = Button(self.app, text = 'play', command = playHandler)
        playButton.grid(row = self.board.size + 2, column = 0, columnspan = self.board.size, sticky = 'WE', padx = 10, pady = 1)
        returnHandler = lambda: self.return_()
        returnButton = Button(self.app, text = 'return', command = returnHandler)
        returnButton.grid(row = self.board.size + 3, column = 0, columnspan = self.board.size, sticky = 'WE', padx = 10, pady = 1)
        threadHandler = lambda: self.thead_4()
        threadButton = Button(self.app, text = '4_thread', command = threadHandler)
        threadButton.grid(row = self.board.size + 4, column = 0, columnspan = self.board.size, sticky = 'WE', padx = 10, pady = 1)
        AIHandler = lambda: self.AI()
        AIButton = Button(self.app, text = 'AI', command = AIHandler)
        AIButton.grid(row = self.board.size + 5, column = 0, columnspan = self.board.size, sticky = 'WE', padx = 10, pady = 1)
        
        #for AI
        self.th_buttons = []
        self.th_stepLabels = []
        self.th_countLables = []
        self.th_boards = []
        self.th_scoreLabels = []
        for i in range(4):
            #initial 4 buttons
            self.th_buttons.append({})
            #initial 4 labels
            self.th_stepLabels.append(Label(self.app, text = 'step:', font="Helvetica 20"))
            self.th_countLables.append(Label(self.app, text = '0', font="Helvetica 20"))
            #initial 4 thread board
            board = deepcopy(self.board) 
            self.th_boards.append(board)
            #initial 4 score labels
            self.th_scoreLabels.append(Label(self.app, text = '', font="Helvetica 15"))
        #move dir[D, U, R, L]
        self.mx = [0, 0, 1, -1]
        self.my = [1, -1, 0, 0]
        self.re_dir = [1, 0, 3, 2]
        #event bind
        self.stop = False 
        self.app.bind('<KeyPress>', self.eventhandler) #event
        #game over
        self.end = False
    
    #stop control
    def eventhandler(self, event):
        self.stop = not self.stop

    #reset the game
    def reset(self):
        self.board = Board()
        self.update()

    #start the game
    def play(self):
        self.update()
    
    def return_(self):
        self.app.config(cursor = "watch")       #set the style of cursor
        self.app.update()
        self.board.fields, self.board.step = self.board.back()
        self.update()
        self.app.config(cursor = "")

    def move(self, x, y):
        self.app.config(cursor = "watch")       #set the style of cursor
        self.app.update()
        self.board = self.board.move(x, y)
        self.update()
        self.app.config(cursor = "")

    #update each button
    def update(self):
        for (x, y) in self.board.fields:
            #modify the text
            text = ''
            if self.board.fields[x, y] != 9:
                text = self.board.fields[x, y]
            self.buttons[x, y]['text'] = text
            #check location and modify the color
            if self.board.fields[x, y] == self.board.right[x, y] and self.board.right[x, y] != 9:
                self.buttons[x, y]['bg'] = 'lightblue'
            else:
                self.buttons[x, y]['bg'] = 'lightgray'
        self.countLabel['text'] = self.board.step
        #check win 
        winning = self.board.won(self.board.fields)
        if winning:
            for x,y in self.board.fields:
                self.buttons[x, y]['bg'] = 'lightblue' 
            score = self.board.countScore(self.board.fields)
            tkMessageBox.showinfo(title = "You win!", message = "Your score is " + str(score))
                 
    def mainloop(self):
        self.app.mainloop()

    def AImove(self, board, buttons, dir, x, y, labels, id):
        # x, y is the position of space
        x = x + self.mx[dir]
        y = y + self.my[dir]
        board = board.move(x, y)
        self.AIupdate(board, buttons, labels, id)
        return board

    def AIupdate(self, board, buttons, labels, id):
        for (x, y) in board.fields:
            text = ''
            if board.fields[x, y] != 9:
                text = board.fields[x, y]
            buttons[x, y]['text'] = text
            if board.fields[x, y] == board.right[x, y] and board.right[x, y] != 9:
                buttons[x, y]['bg'] = 'lightblue'
            else:
                buttons[x, y]['bg'] = 'lightgray' 
        labels['text'] = board.step
        #check win
        winning = board.won(board.fields)
        if winning:
            self.end = True         #stop all
            print('end')
            for x,y in board.fields:
                buttons[x, y]['bg'] = 'lightblue' 
                score = board.countScore(board.fields)
                self.th_scoreLabels[id]['text'] = 'th' + str(id+1) + ' score is ' + str(score)
                self.th_scoreLabels[id].grid(row = 2, column = id*3, columnspan = self.board.size, sticky = 'WE', padx = 10, pady = 1)
                self.th_scoreLabels[id].tkraise()        

    #thread and AI function
    def thead_4(self):
        for i in range(4):
            #initial step label
            self.th_stepLabels[i].grid(row = 0, column = 1 + 3*i, sticky = 'E')
            self.th_countLables[i].grid(row = 0, column = 2 + 3*i, sticky = 'E', ipadx = 5)
            #initial buttons
            for x, y in self.th_boards[i].fields:
                button = Button(self.app, font = self.font, width = 2, height = 1, cursor = "hand1")
                button.grid(row = y+1, column = x + 3*i)
                self.th_buttons[i][x, y] = button 
            x, y = self.findSpace(self.th_boards[i].fields)
            self.th_boards[i] = self.AImove(self.th_boards[i], self.th_buttons[i], i, x, y, self.th_countLables[i], i)        

    def findSolution(self, field):
        #transfer map
        new_field = []
        for i in range(self.board.size):
            row = []
            for j in range(self.board.size):
                if field[j, i] == 9:
                    row.append(0)
                else:
                    row.append(field[j, i])
            new_field.append(row)
        #find position of zero
        zx, zy = self.findSpace(field)
        puzzle = puzzleAI(new_field, zx, zy)
        solution, bound = puzzle.puzzle()
        print ''
        return solution, bound

    #AI action
    def AIaction(self, board, buttons, labels, id):
        x, y = self.findSpace(board.fields)
        board = self.AImove(board, buttons, id, x, y, labels, id) 
        time.sleep(1)
        solution, bound = self.findSolution(board.fields)
        for i in range(bound):
            if self.stop:
                while True:
                    if not self.stop:
                        break           #stop
            if self.end:
                score = board.countScore(board.fields)
                self.th_scoreLabels[id]['text'] = 'th' + str(id+1) + ' score is ' + str(score)
                self.th_scoreLabels[id].grid(row = 2, column = id*3, columnspan = self.board.size, sticky = 'WE', padx = 10, pady = 1)
                self.th_scoreLabels[id].tkraise()               
            x, y = self.findSpace(board.fields)
            board = self.AImove(board, buttons, solution[i], x, y, labels, id)
            time.sleep(1)
    
    #find the position of space
    def findSpace(self, field):
        for i in range(self.board.size):
            for j in range(self.board.size):
                if field[j, i] == 9:
                    zx = j
                    zy = i
                    return zx, zy

    def AI(self):
        for i in range(4):
            thread.start_new_thread(self.AIaction, (self.th_boards[i], self.th_buttons[i], self.th_countLables[i], self.re_dir[i]))

if __name__ == '__main__':
    app = GUI()
    app.mainloop()

        
    
