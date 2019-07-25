import socket
import threading
import json
import random

'''
status=>
0: no player win the game
1: player1 win the game
2: player2 win the game
3: end in a draw

action=>
0: send_card
1: read_card
2: get_a_card
3: rec_card
4: game_over

server -> client
{
    'player': '',
    'action': 0,
    'status': 0,   
    'send': ''
}
client -> server
{
    'player': '',
    'action': 0,
    'status': 0,   
    'send': ''
}
'''

port = 60000
host = socket.gethostname()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

inString = ''
outString = {
    'player': '',
    'action': 0,
    'status': 0,   
    'send': ''
}
player = ''

def writefile(fileName, data):
    #transfer list to string
    content = checkisStr(data)
    with open(fileName, 'wb') as f:
        f.write(content)
    return

def readfile(fileName):
    data = []
    with open(fileName, 'rb') as f:
        content = f.read(1024)
        content = content.replace('\n', '').split(',')
        data.extend(content)
    #return a list
    return data 

def checkisStr(s):
    if type(s) is list:
        return ','.join(s)
    else:
        return s

def checkisList(s):
    if type(s) is str:
        return s.split(',')
    else:
        return s

def see_mycard():
    global player
    card = readfile('c' + player + '.txt')
    card = checkisStr(card)
    print card
    return

def recommend_card():
    cur_card = readfile('now.txt')
    cur_card = checkisStr(cur_card)
    my_card = readfile('c' + player + '.txt')
    if ('color' in cur_card) or ('Plus' in cur_card):
        #color-B or Plus2_B, B is color 
        #find the same color
        rec_card = [c for c in my_card if cur_card[6] in c]
    else:
        #find the same number or the same color
        rec_card = [c for c in my_card if (cur_card[0] or cur_card[1]) in c]
    color_card = [c for c in my_card if 'color' in c]
    rec_card = rec_card + color_card
    return rec_card

def dealOut(s):
    #send data to server
    global player, outString
    while True:
        myCard = readfile('c' + player + '.txt')
        choose = raw_input('(1)see_mycard (2)read_current (3)recommend_card (4)send_card:\n')
        if choose == 'see_mycard':
            see_mycard()
        elif choose == 'read_current':
            outString['action'] = 1
            s.send(json.dumps(outString))
        elif choose == 'recommend_card':
            rec_card = recommend_card()
            if len(rec_card) == 0:
                print 'you have no card to send, get a card from d3'
                outString['action'] = 2
                s.send(json.dumps(outString))
            else:
                print 'recommend: ' + checkisStr(rec_card)
        elif choose == 'send_card':
            select_card = raw_input('Input a card. If you want to select a color card, also choose a color, eg.color-B, color-G, color-R, color-Y:\n')
            if (select_card in myCard) or (('color' in myCard) and ('color' in select_card)):
                if select_card in myCard:
                    myCard.remove(select_card)
                else:
                    myCard.remove('color')
                writefile('c' + player + '.txt', myCard)
                if len(myCard) == 0:
                    #check status
                    print 'you win'
                    outString['status'] = int(player)
                outString['action'] = 3
                outString['send'] = select_card
                s.send(json.dumps(outString))
            else:
                print 'you do not have this card'
        else:
            print 'action error'

def dealIn(s):
    global inString
    while True:
        try:
            inString = json.loads(s.recv(1024))
            if not inString:
                break
            #check the data is myselves
            if inString['player'] == player:
                #check status
                if inString['status'] != 0:
                    if inString['status'] == 3:
                        print 'end in a draw'
                    elif inString['status'] == int(player):
                        print 'you win'
                    else:
                        print 'you lose' 
                else:
                    if inString['action'] == 1:
                        #read_card
                        now = inString['send']
                        writefile('now.txt', now)
                        print now
                    elif inString['action'] == 2:
                        #get_a_card
                        myCard = readfile('c' + player + '.txt')
                        myCard = checkisList(myCard)
                        myCard.append(checkisStr(inString['send']))
                        print 'get card: ' + checkisStr(inString['send'])
                        writefile('c' + player + '.txt', myCard)
                    elif inString['action'] == 3:
                        #rec_card
                        now = inString['send']
                        writefile('now.txt', now)
                        print now
                        if now == 'Plus2_B':
                            card = readfile('c' + player + '.txt')
                            card = checkisList(card)
                            new_card = 'B' + str(random.randint(1,5))
                            print 'get a card: ' + new_card
                            card.append(new_card)
                            new_card = 'B' + str(random.randint(1,5))
                            print 'get a card: ' + new_card
                            card.append(new_card)
                            writefile('c' + player + '.txt', card)
                        elif now == 'Plus2_G':
                            card = readfile('c' + player + '.txt')
                            card = checkisList(card)
                            new_card = 'G' + str(random.randint(1,5))
                            print 'get a card: ' + new_card
                            card.append(new_card)
                            new_card = 'G' + str(random.randint(1,5))
                            print 'get a card: ' + new_card
                            card.append(new_card)
                            writefile('c' + player + '.txt', card)
                        elif now == 'Plus2_R':
                            card = readfile('c' + player + '.txt')
                            card = checkisList(card)
                            new_card = 'R' + str(random.randint(1,5))
                            print 'get a card: ' + new_card
                            card.append(new_card)
                            new_card = 'R' + str(random.randint(1,5))
                            print 'get a card: ' + new_card
                            card.append(new_card)
                            writefile('c' + player + '.txt', card)
                        elif now == 'Plus2_Y':
                            card = readfile('c' + player + '.txt')
                            card = checkisList(card)
                            new_card = 'Y' + str(random.randint(1,5))
                            print 'get a card: ' + new_card
                            card.append(new_card)
                            new_card = 'Y' + str(random.randint(1,5))
                            print 'get a card: ' + new_card
                            card.append(new_card)
                            writefile('c' + player + '.txt', card)
        except Exception as e:
            print e
            break

if __name__ == "__main__":
    player = raw_input("input player1 or player2: ")
    s.connect((host, port))
    outString['player'] = player
    s.send(json.dumps(outString))
    tmp = json.loads(s.recv(1024))
    if tmp['player'] == player:
        c = tmp['send']
        writefile('c' + player + '.txt', c)
        
    threading.Thread(target = dealIn, args = (s,)).start()
    threading.Thread(target = dealOut, args = (s,)).start()

    raw_input()
