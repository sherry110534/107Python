import socket
import sys
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
0: send_card(server send)
1: read_card
2: get_a_card
3: rec_card(client send)
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

con = threading.Condition()
host = socket.gethostname()
port = 60000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)

data = {
    'player': '',
    'action': 0,
    'status': 0,  
    'send': ''
}

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

def generate_card():
    print 'generate card...'
    card = []
    arrB = ['B'+str(i) for i in range(1,6)] #blue*5
    arrG = ['G'+str(i) for i in range(1,6)] #green*5
    arrR = ['R'+str(i) for i in range(1,6)] #red*5
    arrY = ['Y'+str(i) for i in range(1,6)] #yellow*5
    plusB = ['Plus2_B'] * 2
    plusG = ['Plus2_G'] * 2
    plusR = ['Plus2_R'] * 2
    plusY = ['Plus2_Y'] * 2
    color = ['color'] *2
    card = arrB + arrG + arrR + arrY + plusB + plusG + plusR + plusY + color
    writefile('data.txt', card)
    print 'write ' + ','.join(card) + ' in data.txt.'
    return

def div_card():
    print 'deal the card...'
    content = readfile('data.txt')
    #shuffle the card
    random.shuffle(content)
    d1 = content[0:5]
    d2 = content[5:10]
    d3 = content[10:len(content)]
    writefile('d1.txt', d1)
    print 'write ' + ','.join(d1) + ' in d1.txt.'
    writefile('d2.txt', d2)
    print 'write ' + ','.join(d2) + ' in d2.txt.'
    writefile('d3.txt', d3)
    print 'write ' + ','.join(d3) + ' in d3.txt.'
    return

def send_card(num):
    filename = 'd' + num + '.txt'
    return ','.join(readfile(filename))

def NotifyAll(s):
    global data
    if con.acquire():
        data = s
        con.notifyAll()
        con.release()


def clientThreadIn(conn, nick):
    #handle the requests from client
    global data
    while True:
        try:
            #transfer string to object
            tmp = json.loads(conn.recv(1024))
            if not tmp:
                conn.close()
                return
            #broadcast the data, but player only handles data about himself
            data['player'] = tmp['player']
            #check game status
            if tmp['status'] != 0:
                data['status'] = tmp['status']
            if tmp['action'] == 1:
                #read_card
                print 'player' + tmp['player'] + ' wants to read card.'
                data['action'] = 1
                card = readfile('s_now.txt')
                card = checkisStr(card)
                data['send'] = card
                print 'card is ' + card
            elif tmp['action'] == 2:
                #get_a_card
                print 'player' + tmp['player'] + ' wants to get a card from d3.'
                data['action'] = 2
                cards = readfile('d3.txt')
                cards = checkisList(cards)
                card = cards.pop()
                writefile('d3.txt', cards)
                if len(cards) == 0:
                    #d3 has no card, game over
                    data['status'] = 3
                card = checkisStr(card)
                data['send'] = card
                print 'card is ' + card
            elif tmp['action'] == 3:
                #rec_card
                print 'player' + tmp['player'] + ' sent a card: ' +  tmp['send']              
                data['action'] = 3
                #broadcast the card to other player
                if tmp['player'] == '1':
                    data['player'] = '2'
                else:
                    data['player'] = '1'
                card = tmp['send']
                #write this card into s_now.txt .
                writefile('s_now.txt', card)
                data['send'] = tmp['send']
            #broadcast
            NotifyAll(data)
        except Exception as e:
            print e
            return

def clientThreadOut(conn, nick):
    #send data to clients
    global data
    while True:
        if con.acquire():
            con.wait()
            if data:
                try:
                    #transfer object to string
                    conn.send(json.dumps(data))
                    con.release()
                except:
                    con.release()
                    return

if __name__ == "__main__":
    generate_card()
    div_card()
    while True:
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        tmp = json.loads(conn.recv(1024))
        print 'Welcome player' + tmp['player'] + ' to the game!'
        print str((threading.activeCount() + 1) / 2) + ' person(s)!'
        #initial
        data['player'] = tmp['player']
        data['action'] = 0
        data['send'] = send_card(tmp['player'])
        conn.send(json.dumps(data))
        #thread
        threading.Thread(target = clientThreadIn, args = (conn, tmp['player'])).start()
        threading.Thread(target = clientThreadOut, args = (conn, tmp['player'])).start()
    s.close