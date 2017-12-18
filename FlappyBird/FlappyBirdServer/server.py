# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle, os, traceback, json

HOST = "127.0.0.1"
disconnected_list = []#断开连接的客户端列表
onlineUser = {}
sid = 0

# 取得某一个难度下成绩的前十名 modified by Joe at 2017.12.17
def getScoreData(difficulty):
    file = open('scores_server.json','r')
    data = json.load(file)
    file.close()
    scorelist = []
    for user in data:
        userName = user['userName']
        for score in user['scores']:
            if score['difficulty'] == difficulty:
                for i in range(0,len(score['scores'])):
                    scorelist.append((userName,score['scores'][i]))
    # print 'scorelist:',scorelist
    def cmp(s):
        return s[1]
    sortedlist = sorted(scorelist,key = cmp,reverse = True)
    toReturn = sortedlist[:10]
    # print 'toReturn:',toReturn
    return toReturn

def checkSignInAuthentication(signInInformation):
    json_file = open('signinlist.json')
    data = json.load(json_file)
    userInfoList = data['userInfo']
    json_file.close()
    # print userInfoList
    # signInInformation = {'userName':userName,'password':password]}
    for i in range(len(userInfoList)):
        if signInInformation['userName'] == userInfoList[i]['userName'] and signInInformation['password'] == userInfoList[i]['password']:
            return True
    return False

def checkSignUpAuthentication(signUpInformation):
    json_file = open('signinlist.json')
    data = json.load(json_file)
    userInfoList = data['userInfo']
    json_file.close()
    # print userInfoList
    # signUpInformation = {'userName':userName,'password':password]}
    for i in range(len(userInfoList)):
        if signUpInformation['userName'] == userInfoList[i]['userName']:
            return False
    # write the new signUp into signinlist.json file
    json_file = open('signinlist.json','w')
    data['userInfo'].append(signUpInformation)
    json_file.write(json.dumps(data))
    json_file.close()
    return True

def storeScoreInServer(scoreInformation):
    filename = 'scores_server.json'
    file = open(filename,'r')  
    data = json.load(file)
    file.close()
    firstTime = True
    for user in data:
        if user['userName']==scoreInformation['userName']:
            firstTime = False
            for dif in user['scores']:
                if dif['difficulty']==scoreInformation['difficulty'] :
                    dif['scores'].append(scoreInformation['score'])#dif['scores'] is a list of score
    if firstTime:
        dif0 = {'difficulty':0,'scores':[]}
        dif1 = {'difficulty':1,'scores':[]}
        dif2 = {'difficulty':2,'scores':[]}
        diflst = [dif0,dif1,dif2]
        for dif in diflst:
            if dif['difficulty']==scoreInformation['difficulty'] :
                dif['scores'].append(scoreInformation['score'])
        d = {}
        d['userName'] = scoreInformation['userName']
        d['scores'] = diflst
        data.append(d)
    file = open(filename,'w')
    json.dump(data,file,ensure_ascii=False)  
    file.close()  
  

if __name__ == "__main__":
    s = socket.socket()

    host = HOST
    port = 9237

    s.bind((host, port))
    s.listen(4)

    inputs = []
    inputs.append(s)
    print 'server start! listening host:', host, ' port:', port

while inputs:
    try:
        rs, ws, es = select.select(inputs, [], [])
        for r in rs:
            if r is s:
                print 'sid:', sid
                # accept
                connection, addr = s.accept()
                print 'Got connection from' + str(addr)
                inputs.append(connection)
                sendData = {}
                sendData['sid'] = sid
                netstream.send(connection, sendData)

                cInfo = {}
                cInfo['connection'] = connection
                cInfo['addr'] = str(addr)
                cInfo['ready'] = False
                onlineUser[sid] = cInfo
                print(str(onlineUser))
                sid += 1
            else:
                # receive data
                recvData = netstream.read(r)
                # print 'Read data from ' + str(r.getpeername()) + '\tdata is: ' + str(recvData)
                # socket关闭
                if recvData == netstream.CLOSED or recvData == netstream.TIMEOUT:
                    if r.getpeername() not in disconnected_list:
                        print str(r.getpeername()) + 'disconnected'
                        disconnected_list.append(r.getpeername())
                else:  # 根据收到的request发送response
                    #公告
                    if 'notice'in recvData:
                        number = recvData['sid']
                        print 'receive notice request from user id:', number
                        sendData = {"notice_content": "This is a notice from server. Good luck!"}
                        netstream.send(onlineUser[number]['connection'], sendData)

                    if 'signInAuthentication' in recvData:
                        number = recvData['sid']
                        signInInformation = recvData['signInAuthentication']
                        # print 'signin authentication:',signInInformation
                        if checkSignInAuthentication(signInInformation):
                            sendData = {'authenResult':True}
                        else:
                            sendData = {'authenResult':False}
                        netstream.send(onlineUser[number]['connection'],sendData)

                    if 'signUpAuthentication' in recvData:
                        number = recvData['sid']
                        signUpInformation = recvData['signUpAuthentication']
                        # print 'signup authentication:',signUpInformation
                        if checkSignUpAuthentication(signUpInformation):
                            sendData = {'signUpSucceed':True}
                        else:
                            sendData = {'signUpSucceed':False}
                        netstream.send(onlineUser[number]['connection'],sendData)

                    if 'scoreInformation' in recvData:
                        number = recvData['sid']
                        scoreInformation = recvData['scoreInformation']
                        # print 'score:',scoreInformation
                        storeScoreInServer(scoreInformation)

                    if 'scoreRequest' in recvData:
                        number = recvData['sid']
                        scoreData = getScoreData(recvData['scoreRequest']['difficulty'])
                        sendData = {'scoreList':scoreData}
                        netstream.send(onlineUser[number]['connection'],sendData)

    except Exception:
        traceback.print_exc()
        print 'Error: socket 链接异常'

