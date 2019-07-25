import random
import time
import copy

moves = [(-1, -1), (-1,  0), (-1,  1), ( 0, -1), ( 0,  1), ( 1, -1), ( 1,  0), ( 1,  1)]
MAX = 9

def readFile(fileName):
    content = []
    with open(fileName, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            content.append(line)
    return content

def writeFile(fileName, content):
    with open(fileName, 'w') as f:
        for line in content:
            string = ','.join(str(s) for s in line) + '\n'
            f.writelines(string)
    return 

def printGame(game):
    print 'Mine game'
    print '  ',
    for i in range(MAX):
        print ' ' + str(i),
    print ''
    for i in range(MAX):
        print str(i) + ' ',
        for c in game[i]:
            if c == 'c':
                print  ' ' + u'\u23F9',
            elif c == '-1':
                print '-1',
            else:
                print ' ' + str(c),
        print ''
    return

def countMine(play, x, y):
    count = 0
    for v, h in moves:
        if x + v < 0 or y + h < 0 or x + v > MAX-1 or y + h > MAX-1:
            continue
        elif play[x+v][y+h] == '-1':
            count += 1
    return count

def checkOpen(play, x, y):
    if play[x][y] != 'c':    #open
        return True
    else:
        return False        #not open

def checkMine(standard, x, y, play):
    for v, h in moves:
        if x + v < 0 or y + h < 0 or x + v > MAX-1 or y + h > MAX-1:
            continue
        elif checkOpen(play, x+v, y+h):
            continue
        elif standard[x+v][y+h] == '0':
            play[x+v][y+h] = 0
            play = checkMine(standard, x+v, y+h, play)
        else:
            play[x+v][y+h] = standard[x+v][y+h]
    return play

def countScore(play):
    count = 0.0
    for line in play:
        for c in line:
            if c != 'c':
                count += 1
    score = count / (MAX*MAX) * 15
    return score 

def findAllMine(standard, play):
    for i in range(MAX):
        for j in range(MAX):
            if standard[i][j] == '-1':
                play[i][j] = '-1'
    return play

def win(standard, play):
    for i in range(MAX):
        for j in range(MAX):
            if play[i][j] == 'c' and standard[i][j] != '-1':
                return False
    return True

def playGame(standard, play, dataIndex):
    while True:
        printGame(play)
        inp = input('input the position ex. 0,2 :')
        x = inp[0]
        y = inp[1]
        play[x][y] = standard[x][y]
        if standard[x][y] == '-1':
            score = countScore(play)
            play = findAllMine(standard, play)
            printGame(play)
            writeFile('result0' + str(dataIndex) + '.txt', play)
            print 'game over'
            print 'your score is ' + str(score)
            break
        elif win(standard, play):
            play = copy.copy(standard) 
            printGame(play)
            writeFile('result0' + str(dataIndex) + '.txt', play)
            print('win')
            print 'your score is ' + str(score)
            break
        elif standard[x][y] != '0':
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
        elif standard[x][y] == '0':
            play = checkMine(standard, x, y, play)
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
    return

def playGameAI(standard, play, dataIndex):
    score = 0
    life  = 3
    danger = []
    while True:
        printGame(play)
        #time.sleep(1)
        x = 0
        y = 0
        while(True):
            x = random.randint(0, 8)
            y = random.randint(0, 8)
            if not checkOpen(play, x, y) and (x, y) not in danger:
                break
        print 'the position is ' + str(x) + ', ' + str(y)
        play[x][y] = standard[x][y]
        if standard[x][y] == '-1':
            printGame(play)
            if life == 0:
                score = countScore(play)
                play = findAllMine(standard, play)
                printGame(play)
                writeFile('result0' + str(dataIndex) + '.txt', play)
                print 'game over'
                print 'your score is ' + str(score)
                break
            else:
                life -= 1
                play[x][y] = 'c'
                danger.append((x, y))
                print('boom!life -1')
                continue
        elif win(standard, play):
            play = copy.copy(standard) 
            printGame(play)
            writeFile('result0' + str(dataIndex) + '.txt', play)
            print('win')
            print 'your score is ' + str(score)
            break
        elif standard[x][y] != '0':
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
        elif standard[x][y] == '0':
            play = checkMine(standard, x, y, play)
            writeFile("play0" + str(dataIndex) + ".txt", play)
            continue
    return score

def function1():
    print 'funciton 1'
    for i in range(5):
        play = readFile('data0' + str(i+1) + '.txt')
        for j in range(MAX):
            for k in range(MAX):
                if play[j][k] != '-1':
                    play[j][k] = countMine(play, j, k)
        writeFile('standard0' + str(i+1) + '.txt', play)

def function2():
    print 'function 2'
    dataIndex = input('select a map (1~5):')
    standard = readFile('standard0' + str(dataIndex) + '.txt')
    play = [['c' for i in range(MAX)] for j in range(MAX)]
    playGame(standard, play, dataIndex)

def function3():
    print 'function 3'
    score = 0.0
    for i in range(5):
        standard = readFile('standard0' + str(i+1) + '.txt')
        play = [['c' for j in range(MAX)] for k in range(MAX)]
        score += playGameAI(standard, play, i+1)   
    print 'score is '  + str(score/5)

function3()