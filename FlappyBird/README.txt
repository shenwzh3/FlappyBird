【安装与启动】
0.安装python2.7.14、cocos2d、pycrypto。

1.通过FlappyBirdServer/start_server.bat启动服务端。

2.通过FlappyBirdClient/start_client.bat启动客户端。


【功能说明】
1.点击“notice”按钮显示服务器公告，该功能用于演示服务器客户端通讯功能。
2.点击客户端界面空白处可以触发小鸟跳跃，避开栏杆。


【代码说明】
1.[客户端]逻辑代码在flappy_bird\lib目录下。
2.[客户端]资源文件在flappy_bird\data目录下。
3.[服务端]代码在flappy_bird\FlappyBirdServer目录下。



【实现细节】
客户端：
用户注册/登陆信息传给服务端，给服务器发送成绩排名请求 于 network.py 实现

服务端：
注册登陆请求的验证和回复，接收成绩并储存，给客户端发送所有成绩排名信息 于 server.py 实现

AES对称加密解密（客户端&服务端共享私钥）：
AES128加密解密 于 myAES.py 实现
在所有socket通信消息发送之前进行AES加密，接受消息解密 于 netstream.py 实现



