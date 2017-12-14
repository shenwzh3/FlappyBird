# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle, os, traceback, json

HOST = "127.0.0.1"
disconnected_list = []#断开连接的客户端列表
onlineUser = {}
sid = 0



def checkSignInAuthentication(signInInformation):
	json_file = open('signinlist.json')
	data = json.load(json_file)
   	userInfoList = data['userInfo']
   	json_file.close()
   	print userInfoList
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
   	print userInfoList
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
						print 'signin authentication:',signInInformation
						if checkSignInAuthentication(signInInformation):
							sendData = {'authenResult':True}
						else:
							sendData = {'authenResult':False}
						netstream.send(onlineUser[number]['connection'],sendData)

					if 'signUpAuthentication' in recvData:
						number = recvData['sid']
						signUpInformation = recvData['signUpAuthentication']
						print 'signup authentication:',signUpInformation
						if checkSignUpAuthentication(signUpInformation):
							sendData = {'signUpSucceed':True}
						else:
							sendData = {'signUpSucceed':False}
						netstream.send(onlineUser[number]['connection'],sendData)



	except Exception:
		traceback.print_exc()
		print 'Error: socket 链接异常'

