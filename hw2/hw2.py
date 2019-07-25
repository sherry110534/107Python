#coding=UTF-8
from Tkinter import *
import tkMessageBox
import random
import math
import time
import threading

SIZE = 400
LEN = 4
DIVIDER = 5
GAME_BACKGRAND = "#92877d"
CELL_BACKGROUND_COLOR = {
    0: "#9e948a", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179", 16: "#f59563",\
    32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72", 256: "#edcc61", 512: "#edc850",\
    1024: "#edc53f", 2048: "#edc22e" 
}
FONT_COLOR = {
    0: "#9e948a", 2: "#776e65", 4: "#776e65", 8: "#f9f6f2", 16: "#f9f6f2",\
    32: "#f9f6f2", 64: "#f9f6f2", 128: "#f9f6f2", 256: "#f9f6f2", 512: "#f9f6f2",\
    1024: "#f9f6f2", 2048: "#f9f6f2"
}

def eventhandler(event):
    global matrix
    global record
    zero_matrix = [[0]*LEN for i in range(LEN)]
    if checkState(matrix) == 1:
        if event.keysym == 'Left':
            if matrix != left(matrix) or matrix == zero_matrix:
                record = matrix
                matrix = left(matrix)
                randomNext(matrix)
        elif event.keysym == 'Right':
            if matrix != right(matrix) or matrix == zero_matrix:
                record = matrix
                matrix = right(matrix)
                randomNext(matrix)
        elif event.keysym == 'Up':
            if matrix != up(matrix) or matrix == zero_matrix:
                record = matrix
                matrix = up(matrix)
                randomNext(matrix)
        elif event.keysym == 'Down':
            if matrix != down(matrix) or matrix == zero_matrix:
                record = matrix
                matrix = down(matrix)
                randomNext(matrix)
        elif event.keysym == 'space':
            matrix = record
        
        updateWin(matrix) 
        #move done, check now state
        if checkState(matrix) == 2:
            showResult("You win! ", countScore(matrix))
        elif checkState(matrix) == 0:
            showResult("You lose! ", countScore(matrix))
  
#random generate 2 or 4
def randomNext(matrix):
    empty = []
    for i in range(LEN):
        for j in range(LEN):
            if matrix[i][j] == 0:
                empty.append((i, j))
    if len(empty) == 0:
        return matrix
    else: 
        random.seed()
        place = empty[random.randint(0, len(empty)-1)]
        num = random.randrange(2, 5, 2) #4 or 2
        matrix[place[0]][place[1]] = num
        return matrix

#check the game state
def checkState(matrix):
    #0 -> lose
    #1 -> continue
    #2 -> win
 
    #check all matrix
    for i in range(LEN):
        for j in range(LEN):
            if matrix[i][j] == 2048:
                return 2
            elif matrix[i][j] == 0:
                return 1
    #check same neighbor
    for i in range(LEN):
        for j in range(LEN - 1):
            if matrix[i][j] == matrix[i][j+1]:
                return 1
    for i in range(LEN):
        for j in range(LEN - 1):
            if matrix[j][i] == matrix[j+1][i]:
                return 1
    #lose
    return 0

#count score
def countScore(matrix):
    new = []
    for row in matrix:
        new.append(max(row))
    max_num = max(new)
    if max_num < 128:
        return 0
    elif max_num == 128:
        return 5
    elif max_num == 256:
        return 10
    elif max_num == 512:
        return 20
    elif max_num == 1024:
        return 30
    elif max_num == 2048:
        return 40
    return 0

#transpose the matrix(column to row, row to column)
def transpose(matrix):
    matrix = [list(row) for row in zip(*matrix)]
    return matrix

#reverse the matrix(right to left, left to right)
def reverse(matrix):
    matrix = [row[::-1] for row in matrix]
    return matrix

#move the matrix
def move(row):
    #zip -> merge -> zip
    #zip all non-zero to left
    #[0,2,2,4]->[2,2,4,0]
    def zip(row):
        new = [0, 0, 0, 0]
        i = 0
        for r in row:
            if r != 0:
                new[i] = r
                i+=1
        return new

    #merge the same neighbor
    #[2,2,4,0]->[0,4,4,0]
    def merge(row):
        jump = False
        for i in range(LEN-1):
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

def left(matrix):
    new = [[0]*LEN for i in range(LEN)]
    for i in range(LEN):
        new[i] = move(matrix[i])
    return new

def right(matrix):
    matrix = reverse(left(reverse(matrix)))
    return matrix

def up(matrix):
    matrix = transpose(left(transpose(matrix)))
    return matrix

def down(matrix):
    matrix = transpose(right(transpose(matrix)))
    return matrix

#update the window with new matrix
def updateWin(matrix):
    for i in range(LEN):
        for j in range(LEN):
            if matrix[i][j] == 0:
                txt_matrix[i][j].config(text = '', fg = FONT_COLOR[matrix[i][j]], bg = CELL_BACKGROUND_COLOR[matrix[i][j]])
            else:
                txt_matrix[i][j].config(text = str(matrix[i][j]), fg = FONT_COLOR[matrix[i][j]], bg = CELL_BACKGROUND_COLOR[matrix[i][j]])

def showResult(msg, score):
    tkMessageBox.showinfo(title = "Game Over", message = msg + "Your score is " + str(score))

#count difference in the matrix
def countDifference(matrix):
    total = 0.0
    for i in range(LEN):
        for j in range(LEN-1):
            if matrix[i][j] != 0 and matrix[i][j+1] != 0:
                diff = math.log(matrix[i][j], 2) - math.log(matrix[i][j+1], 2)
                diff = abs(diff)
                total += diff
            if matrix[j][i] != 0 and matrix[j+1][i] != 0:
                diff = math.log(matrix[j][i], 2) - math.log(matrix[j+1][i], 2)
                diff = abs(diff)
                total += diff
    return total*(-1)

#find increase or decrease in the matrix
def findOrder(matrix):
    #                   / top > bottom
    # / top and bottom  \ bottom > top
    # \ left and right  / left > right
    #                   \ right > left
    top_bottom = 0.0
    bottom_top = 0.0
    left_right = 0.0
    right_left = 0.0
    for i in range(LEN):
        for j in range(LEN-1):
            #top-down
            if matrix[i][j] != 0 and matrix[i][j+1] != 0:
                diff = math.log(matrix[i][j], 2) - math.log(matrix[i][j+1], 2)
                diff = abs(diff)
                if matrix[i][j] > matrix[i][j+1]:
                    top_bottom += diff
                else:
                    bottom_top += diff
            #left-right
            if matrix[j][i] != 0 and matrix[j+1][i] != 0:
                diff = math.log(matrix[j][i], 2) - math.log(matrix[j+1][i], 2)
                diff = abs(diff)
                if matrix[j][i] > matrix[j+1][i]:
                    left_right += diff
                else:
                    right_left += diff
    top_bottom *= (-1)
    bottom_top *= (-1)
    left_right *= (-1)
    right_left *= (-1)
    return max(top_bottom, bottom_top) + max(left_right, right_left)

#find empty cell
def findEmpty(matrix):
    count = 0.0
    for r in matrix:
        for c in r:
            if c == 0:
                count += 1
    if count == 0.0:
        return 0
    else:
        return math.log(count)

#find the max value
def findMax(matrix):
    maxNum = 0.0
    for r in matrix:
        maxNum = max(maxNum, max(r))
    if maxNum == 0.0:
        return 0
    else:
        return math.log(maxNum, 2)
    
#count result
def countResult(matrix):
    result = 0.0
    result = countDifference(matrix) * 0.1 + findOrder(matrix) * 1.0 + findEmpty(matrix) * 2.7 + findMax(matrix) * 1.0
    return result

#find the best choose
def findDir(matrix):
    #[up, down, left, right]
    total = [0.0, 0.0, 0.0, 0.0]
    total[0] = countResult(up(matrix))
    total[1] = countResult(down(matrix))
    total[2] = countResult(left(matrix))
    total[3] = countResult(right(matrix))
    dir_ = total.index(max(total))
    while True:
        if dir_ == 0:
            new = up(matrix)
        elif dir_ == 1:
            new = down(matrix)
        elif dir_ == 2:
            new = left(matrix)
        elif dir_ == 3:
            new = right(matrix)
        if new != matrix:
            break
        elif total[0] == total[1] and total[1] == total[2] and total[2] == total[3]:
            dir_ = random.randint(0, 3)
            break
        else:
            total[int(dir_)] = -100
            dir_ = total.index(max(total))
    return dir_, total[dir_]

#find the worst random place
def findWorstRandom(matrix):
    new = list(matrix)
    emptyCell = []
    worst = (0, 0, 2)   #(x, y ,value)
    max = -100
    for i in range(LEN):
        for j in range(LEN):
            if new[i][j] == 0:
                emptyCell.append((i, j))
    for c in emptyCell:
        new[c[0]][c[1]] = 2
        result = countResult(new)
        if result > max:
            worst = (c[0], c[1], 2)
        new[c[0]][c[1]] = 4
        result = countResult(new)
        if result > max:
            worst = (c[0], c[1], 4)
    return worst

#depth
def depthSearch(matrix):
    def move(choose, matrix):
        if choose == 2:
            matrix = left(matrix)
        elif choose == 3:
            matrix = right(matrix)
        elif choose == 0:
            matrix = up(matrix)
        elif choose == 1:
            matrix = down(matrix)
        return matrix

    minTime = 0.2
    start = time.time()
    bestDir = 0
    new_up = list(matrix)
    new_down = list(matrix)
    new_left = list(matrix)
    new_right = list(matrix)
    new_up = up(new_up)
    new_down = down(new_down)
    new_left = left(new_left)
    new_right = right(new_right)  
    #[up, down, left, right]
    total = [0.0, 0.0, 0.0, 0.0]
    total[0] = countResult(up(new_up))
    total[1] = countResult(down(new_down))
    total[2] = countResult(left(new_left))
    total[3] = countResult(right(new_right))
    
    while True:
        #limit the time of depth funtion
        if (time.time() - start) > minTime:
            break
        #create random number cell
        worst_up = findWorstRandom(new_up)
        worst_down = findWorstRandom(new_down)
        worst_left = findWorstRandom(new_left)
        worst_right = findWorstRandom(new_right)
        new_up[worst_up[0]][worst_up[1]] = worst_up[2]
        new_down[worst_down[0]][worst_down[1]] = worst_down[2]
        new_left[worst_left[0]][worst_left[1]] = worst_left[2]
        new_right[worst_right[0]][worst_right[1]] = worst_right[2]
        #next best dir
        tmp_up_dir, tmp_up_total = findDir(new_up)
        tmp_down_dir, tmp_down_total = findDir(new_down)
        tmp_left_dir, tmp_left_total = findDir(new_left)
        tmp_right_dir, tmp_right_total = findDir(new_right)

        total[0] += tmp_up_total
        total[1] += tmp_down_total
        total[2] += tmp_left_total
        total[3] += tmp_right_total

        new_up = move(tmp_up_dir, new_up)
        new_down = move(tmp_down_dir, new_down)
        new_left = move(tmp_left_dir, new_left)
        new_right = move(tmp_right_dir, new_right)
        
    bestDir = total.index(max(total))
    new = []
    while True:
        if bestDir == 0:
            new = up(matrix)
        elif bestDir == 1:
            new = down(matrix)
        elif bestDir == 2:
            new = left(matrix)
        elif bestDir == 3:
            new = right(matrix)
        if new != matrix:
            break
        elif total[0] == total[1] and total[1] == total[2] and total[2] == total[3]:
            bestDir = random.randint(0, 3)
            break
        else:
            total[int(bestDir)] = -10000000
            bestDir = total.index(max(total))
    return bestDir

#AI play
def AIControl():
    global matrix
    zero_matrix = [[0]*LEN for i in range(LEN)]
    order_dir = 0
    if matrix == zero_matrix:
        randomNext(matrix)
        updateWin(matrix)
    while checkState(matrix) == 1:
        time.sleep(0.5)
        if order_dir == 3:
            order_dir = 0
        #choose = depthSearch(matrix)
        choose, total = findDir(matrix)
        #choose = order_dir
        if choose == 2:
            matrix = left(matrix)          
        elif choose == 3:
            matrix = right(matrix)
        elif choose == 0:
            matrix = up(matrix)
        elif choose == 1:
            matrix = down(matrix)
        randomNext(matrix)
        updateWin(matrix) 
        #move done, check now state
        if checkState(matrix) == 2:
            showResult("You win! ", countScore(matrix))
        elif checkState(matrix) == 0:
            showResult("You lose! ", countScore(matrix)) 
        order_dir += 1
    return

#prevent to be stuck  
def thread(func, *args):
    t = threading.Thread(target = func, args = args)
    t.setDaemon(True)
    t.start()

if __name__ == "__main__":
    #initial game
    matrix = [[0]*LEN for i in range(LEN)]
    record = [[0]*LEN for i in range(LEN)]
    
    #create window
    win = Tk()
    win.title("2048 game")
    win.resizable(0,0)  #forbid user to change size 
    win.geometry('600x650') #window size
    win.bind('<KeyPress>', eventhandler) #event 
    title = Label(win, text = "2048", font="Helvetica 60 bold", fg = GAME_BACKGRAND) 
    title.pack()
    AIButton = Button(win, text = "AI play", command = lambda:thread(AIControl)).pack()
    #create frame in window
    background = Frame(win, bg = GAME_BACKGRAND, width = SIZE, height = SIZE)    
    #create small frames in background frame
    txt_matrix = []
    for i in range(LEN):
        txt_row = []
        for j in range(LEN):
            cell = Frame(background, bg = CELL_BACKGROUND_COLOR[0], width = SIZE/LEN, height = SIZE/LEN)
            cell.grid(row = i, column = j, padx = DIVIDER, pady = DIVIDER)  #margin
            cell.pack_propagate(0)  #do not shrink
            #initial window
            txt = Label(cell, text = '', bg = CELL_BACKGROUND_COLOR[0], font="Helvetica 30 bold", width = 5, height = 5)
            txt.pack()
            txt_row.append(txt)
        txt_matrix.append(txt_row)
    background.pack(side = BOTTOM, pady = 30)
    win.mainloop()

    

    
    