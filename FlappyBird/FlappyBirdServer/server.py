# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle, os, traceback, json

HOST = "127.0.0.1"
disconnected_list = []#断开连接的客户端列表
onlineUser = {}
sid = 0



# a little bug here
def checkAuthentication(signInInformation):
	json_file = open('signinlist.json')
	data = json.load(json_file)
   	userInfoList = data['userInfo']
   	print userInfoList
    # signInInformation = {'userName':userName,'password':password]}
	for i in range(len(userInfoList)):
		if signInInformation['userName'] in userInfoList[i]['userName'] and signInInformation['password'] in userInfoList[i]['password']:
			return True
	return False

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
						print 'authentication:',signInInformation
						if checkAuthentication(signInInformation):
							sendData = {'authenResult':True}
							netstream.send(onlineUser[number]['connection'],sendData)
						else:
							sendData = {'authenResult':False}
							netstream.send(onlineUser[number]['connection'],sendData)


	except Exception:
		traceback.print_exc()
		print 'Error: socket 链接异常'

