#coding=UTF-8
#python3 print
from __future__ import print_function
import os
import random
import time

MAX = 9
moveList = [(-1, -1), (-1,  0), (-1,  1), ( 0, -1), ( 0,  1), ( 1, -1), ( 1,  0), ( 1,  1)]

def readFile(fileName):
    fo = open(fileName, 'r')
    content = []
    i = 0
    #transform file data into list
    for line in fo:
        #remove '\n' and split with ','
        line = line.strip().split(',')
        content.append(line)
        i += 1
    fo.close()
    return content

def writeFile(fileName, content):
    fo = open(fileName, 'w')
    for line in content:
        #tranform number list to string with ','
        string = ','.join(str(s) for s in line) + '\n'
        fo.writelines(string)
    fo.close()
    return

def countMine(map, x, y):
    count = 0
    for (vert, horiz) in moveList:
        #out of range [0]-[8]
        if x+vert < 0 or y+horiz < 0:
            continue
        elif x+vert > MAX-1 or y+horiz > MAX-1:
            continue
        elif map[x+vert][y+horiz] == '-1':
            count +=  1
    return count

def printGame(play):
    print("踩地雷遊戲".rjust(35))
    #print 012345678
    print('\t', end='')
    print("{0: >3}{1: >4}".format(' ',"丨"), end='')
    for i in range(MAX):
        print("{0: >3}".format(i), end='')
    print()
    #print ---------
    print('\t' + "丨".rjust(7, '-').ljust(35, '-'))
    #print 口口口
    for j in range(MAX):
        print('\t', end='')
        print("{0: >3}{1: >4}".format(j,"丨"), end='')
        for c in play[j]:
            if c == 'c':
                print("{0: <7}".format(" ▇▇"), end='')
            else:
                print("{0: >3}".format(c), end='')
        print()
    return

def checkOpened(play, x, y):
    #check this position was opened or not
    if play[x][y] != 'c':
        return True

def checkMine(standard, x, y, play):
    #standard[x][y] in this function must be 0   
    for (vert, horiz) in moveList:
        #out of range [0]-[8]
        if x+vert < 0 or y+horiz < 0:
            continue
        elif x+vert > MAX-1 or y+horiz > MAX-1:
            continue
        #this position was opened
        elif play[x+vert][y+horiz] != 'c':
            continue
        #this position is 0, open it and find next
        elif standard[x+vert][y+horiz] == '0':
            play[x+vert][y+horiz] = standard[x+vert][y+horiz]
            #recursive check mine
            play = checkMine(standard, x+vert, y+horiz, play)
        else:
            play[x+vert][y+horiz] = standard[x+vert][y+horiz]
    return play

def countScore(play):
    count = 0
    for i in play:
        for j in i:
            if j != 'c':
                count += 1
    score = (float(count) / float(MAX*MAX)) * 30
    return score 

def findAllMine(standard, play):
    for i in range(MAX):
        for j in range(MAX):
            if standard[i][j] == '-1':
                play[i][j] = '-1'
    return play

def winGame(standard, play):
    for i in range(MAX):
        for j in range(MAX):
            #there is the position not opened and it is not mine 
            if play[i][j] == 'c' and standard[i][j] != '-1':
                return False
    return True 

def getHint(play):
    hint = []
    for i in range(MAX):
        for j in range(MAX):
            if play[i][j] != '0' and play[i][j] != 'c':
                hint.append((i, j))
    return hint

def playGame(standard, play, dataIndex):
    while True:
        printGame(play)
        #user inputs (x,y) and transform it into 2 integers
        x,y = map(int, raw_input("\t輸入要踩的位置（例：x,y:0<=x<=8, 0<=y<=8）：").split(',')) 
        while checkOpened(play, x, y):
            print("\t此位置已翻開")
            x,y = map(int, raw_input("\t輸入要踩的位置（例：x,y:0<=x<=8, 0<=y<=8）：").split(',')) 
        #open this position
        play[x][y] = standard[x][y]
        #the position is mine
        if standard[x][y] == '-1':
            score = countScore(play)
            #open all mine
            play = findAllMine(standard, play)
            printGame(play)
            writeFile("result0" + str(dataIndex) + ".txt", play)
            print("\tBOOM!遊戲結束")       
            print("\t你的得分是 %.2f分" %score)
            break
        #win
        elif winGame(standard, play):            
            play = standard
            printGame(play)
            writeFile("result0" + str(dataIndex) + ".txt", play)
            print("\tWIN!遊戲結束")
            print("\t你的得分是 %.2f分" %30)
            break
        #the position is not mine
        elif standard[x][y] != '0':
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
        elif standard[x][y] == '0':
            play = checkMine(standard, x, y, play)
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
    return

def playGameRandomAI(standard, play, dataIndex):
    score = 0
    life = 3
    while True:
        printGame(play)
        time.sleep(3)
        random.seed()
        x = random.randint(0,8)
        y = random.randint(0,8)
        #this position is opened, random again
        while checkOpened(play, x, y):
            x = random.randint(0,8)
            y = random.randint(0,8)
        print("\t輸入要踩的位置（例：x,y:0<=x<=8, 0<=y<=8）：", x, ',', y)
        #open this position
        play[x][y] = standard[x][y]
        #the position is mine
        if standard[x][y] == '-1':
            printGame(play)
            if life > 0:
                life -= 1
                #close this position
                play[x][y] = 'c'
                print("\tBOOM！life-1")
                print("\t你還剩 %d次機會" %life)
                continue
            else:
                score = countScore(play)
                #open all mine
                play = findAllMine(standard, play)
                printGame(play)
                writeFile("AI0" + str(dataIndex) + ".txt", play)
                print("\tBOOM!遊戲結束")       
                print("\t你的得分是 %.2f分" %score)
                break
        #win
        elif winGame(standard, play):
            play = standard
            printGame(play)
            writeFile("AI0" + str(dataIndex) + ".txt", play)
            print("\tWIN!遊戲結束")
            print("\t你的得分是 %.2f分" %30)
            score = 30
            break
        #the position is not mine
        elif standard[x][y] != '0':
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
        elif standard[x][y] == '0':
            play = checkMine(standard, x, y, play)
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
    return score

def playGameSmartAI(standard, play, dataIndex, select):
    score = 0
    life = 3
    safe = []
    danger = []
    x = 0
    y = 0
    while True:
        printGame(play)
        time.sleep(3)
        #safe list is empty, find new safe position
        if len(safe) == 0:
            hint = getHint(play)
            #update probability
            for j in range(MAX):
                for k in range(MAX):
                    #these positions were opened, not mine
                    #probability is 0
                    if play[j][k] != 'c':
                        select[j][k] = 0 
            for h in hint:
                unknown = []
                mine = 0
                #record near position
                for (vert, horiz) in moveList:
                    #out of range [0]-[8]
                    if h[0]+vert < 0 or h[1]+horiz < 0:
                        continue
                    elif h[0]+vert > MAX-1 or h[1]+horiz > MAX-1:
                        continue
                    #unknown position
                    elif select[h[0]+vert][h[1]+horiz] == -1:
                        unknown.append((h[0]+vert, h[1]+horiz))
                    #mine position
                    elif select[h[0]+vert][h[1]+horiz] == 100:
                        danger.append((h[0]+vert, h[1]+horiz))
                        mine += 1
                #hint number = mine + unknown
                #all unknown is mine 
                if int(play[h[0]][h[1]]) == (len(unknown) + mine):
                    for u in unknown:
                        danger.append(u)
                        select[u[0]][u[1]] = 100
                #hint number = mine
                #all unknown is safe
                elif int(play[h[0]][h[1]]) == mine:
                    for u in unknown:
                        select[u[0]][u[1]] = 0
                        safe.append(u)       
                #Unkown(A) - Unknown(B) = hint(A) - hint(B)
                #all noncommon position is mine
                else:
                    #find neighbor B
                    x1 = h[0] - 2
                    y1 = h[1] - 2
                    x2 = h[0] + 2
                    y2 = h[1] + 2
                    #out of range [0]-[8]
                    if x1 < 0:
                        x1 = 0
                    if y1 < 0:
                        y1 = 0
                    if x2 > 8:
                        x2 = 8
                    if y2 > 8:
                        y2 = 8
                    for j in range(x1, x2+1):
                        for k in range(y1, y2+1):
                            if j == h[0] and k == h[1]:
                                continue
                            elif play[j][k] == 'c':
                                continue
                            else:
                                unknownB = []
                                #find unknown(B)
                                for (vert, horiz) in moveList:
                                    #out of range [0]-[8]
                                    if j+vert < 0 or k+horiz < 0:
                                        continue
                                    elif j+vert > MAX-1 or k+horiz > MAX-1:
                                        continue
                                    #unknown position
                                    elif select[j+vert][k+horiz] == -1:
                                        unknownB.append((j+vert, k+horiz))
                                if (int(play[h[0]][h[1]])-int(play[j][k])) > 0 and (len(unknown)-len(unknown)) == (int(play[h[0]][h[1]])-int(play[j][k])):
                                    diff = list(set(unknown) - set(unknownB))
                                    for d in diff:
                                        select[d[0]][d[1]] = 100
                                        danger.append(d)
                #if safe list is still null
                if len(safe) != 0:
                    position = safe.pop()
                    x = position[0]
                    y = position[1]
                else:
                    #remove duplicate
                    danger = list(set(danger))
                    random.seed()
                    x = random.randint(0,8)
                    y = random.randint(0,8)
                    while (x,y) in danger:
                        random.seed()
                        x = random.randint(0,8)
                        y = random.randint(0,8)                            
        else:
            position = safe.pop()
            x = position[0]
            y = position[1]
 
        #this position is opened, random again
        while checkOpened(play, x, y):
            random.seed()
            x = random.randint(0,8)
            y = random.randint(0,8)
            while (x,y) in danger:
                random.seed()
                x = random.randint(0,8)
                y = random.randint(0,8)         
        print("\t輸入要踩的位置（例：x,y:0<=x<=8, 0<=y<=8）：", x, ',', y)
        #open this position
        play[x][y] = standard[x][y]
        #the position is mine
        if standard[x][y] == '-1':
            printGame(play)
            if life > 0:
                life -= 1
                #close this position
                play[x][y] = 'c'
                select[x][y] = 100
                print("\tBOOM！life-1")
                print("\t你還剩 %d次機會" %life)
                continue
            else:
                score = countScore(play)
                #open all mine
                play = findAllMine(standard, play)
                printGame(play)
                writeFile("AI0" + str(dataIndex) + ".txt", play)
                print("\tBOOM!遊戲結束")       
                print("\t你的得分是 %.2f分" %score)
                break
        #win
        elif winGame(standard, play):
            play = standard
            printGame(play)
            writeFile("AI0" + str(dataIndex) + ".txt", play)
            print("\tWIN!遊戲結束")
            print("\t你的得分是 %.2f分" %30)
            score = 30
            break
        #the position is not mine
        elif standard[x][y] != '0':
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
        elif standard[x][y] == '0':
            play = checkMine(standard, x, y, play)
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
    return score

def function1():
    print("".ljust(50, '*'))
    print("function1:")
    for i in range(1,6):
        print("\tcreating standard0" + str(i) + ".txt...")
        standard = [['0' for j in range(MAX)] for k in range(MAX)]
        data = readFile("data0" + str(i)+ ".txt")
        for j in range(MAX):
            for k in range(MAX):
                if data[j][k] == '-1':
                    standard[j][k] = -1
                else:
                    standard[j][k] = countMine(data, j, k)
        writeFile("standard0" + str(i)+ ".txt", standard)
        print("\tcreate successfully\n")        
    print("function1 completed")
    print("".ljust(50, '*'))

def function2():
    print("".ljust(50, '*'))
    print("function2:")
    dataIndex = input("\t請選擇地圖（1~5）：")
    playMode = input("\t1.重新開始\t2.繼續遊戲：")
    standard = readFile("standard0" + str(dataIndex) + ".txt")
    if playMode == 1:
        #initial play
        play = [['c' for j in range(MAX)] for k in range(MAX)]
    elif playMode == 2:
        if os.path.isfile("play0" + str(dataIndex) + ".txt"):
            play = readFile("play0" + str(dataIndex) + ".txt")
        else:
            print("查無遊戲紀錄，重新開始")
            play = [['c' for j in range(MAX)] for k in range(MAX)]
    playGame(standard, play, dataIndex)
    print("function2 completed")
    print("".ljust(50, '*'))

#random AI
def function3():
    print("".ljust(50, '*'))
    print("function3(random):")
    score = [0]*5
    sum = 0
    for i in range(1,6):
        print("\tround" + str(i))
        standard = readFile("standard0" + str(i) + ".txt")
        if os.path.isfile("play0" + str(i) + ".txt"):
            play = readFile("play0" + str(i) + ".txt")
        else:
            play = [['c' for j in range(MAX)] for k in range(MAX)]
        score[i-1] = playGameRandomAI(standard, play, i)
    for s in score:
        sum += s
    sum = float(sum) / 5
    print("\t五次平均分數為 %.2f分" %sum)
    print("function3(random) completed")
    print("".ljust(50, '*'))

#smart AI
def function3_2():
    print("".ljust(50, '*'))
    print("function3(smart):")
    score = [0]*5
    sum = 0
    for i in range(1,6):
        #initial AI probability list, -1 is unknown
        select = [[-1 for j in range(MAX)] for k in range(MAX)]
        print("\tround" + str(i))
        standard = readFile("standard0" + str(i) + ".txt")
        if os.path.isfile("play0" + str(i) + ".txt"):
            play = readFile("play0" + str(i) + ".txt")
            for j in range(MAX):
                for k in range(MAX):
                    #these positions were opened, not mine
                    #probability is 0
                    if play[j][k] != 'c':
                        select[j][k] = 0
        else:
            play = [['c' for j in range(MAX)] for k in range(MAX)]
        score[i-1] = playGameSmartAI(standard, play, i, select)
    for s in score:
        sum += s
    sum = float(sum) / 5
    print("\t五次平均分數為 %.2f分" %sum)
    print("function3(smart) completed")
    print("".ljust(50, '*'))
    return
    
if __name__ == '__main__':
    a = input("請選擇功能\n（1.功能1  2.功能2  3.功能3（random）  4.功能3（smartAI））\n")
    if a == 1:
        function1()
    elif a == 2:
        function2()
    elif a == 3:
        function3()
    elif a == 4:
        function3_2()
    else:
        print("輸入錯誤\n")
