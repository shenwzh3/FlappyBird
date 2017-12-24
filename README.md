【安装与启动】


0.安装python2.7.14、cocos2d、pycrypto。


1.通过FlappyBirdServer/start_server.bat启动服务端。

【功能说明】


0.进入主界面后通过log in和log out来选择登陆或注册。

1.进入登录或注册界面后，输入必要信息，点击ok进入游戏，并进入难度选择界面

2.目前共有三种难度：easy、medium、hard，用户选择完难度即开始游戏，每次重新开始游戏都要选择难度


3.点击客户端界面空白处可以触发小鸟跳跃，避开栏杆。



4.单局游戏结束后通过点击 restart可以重新开始

5.单局游戏结束后点击排行图标可以查看排行榜

6.点击右上角log out可以返回主界面切换用户



【代码说明】

0.[客户端]逻辑代码在flappy_bird\lib目录下。


1.[客户端]资源文件在flappy_bird\data目录下。


2.[服务端]代码在flappy_bird\FlappyBirdServer目录下。




【代码架构】

0.使用C/S架构，即客户端/服务器架构

1.客户端受限于cocos库的功能限制，并没有使用如今流行的MVC架构来开发，但也做到了对各个组件进行分别封装，并在不同文件中实现



【实现细节】

客户端：

0.客户端利用cocos库的功能实现了登陆、注册、切换用户、难度选择、查看成绩、查看排行等几大功能模块，分别封装为cocos.Menu的子类，同时针对cocos的功能的局限性对一些类进行了重写，例如重写了EntryMenuItme以实现可以输入密码的输入框EntryPswMenuItem

1.修改了原有生成管道和碰撞模型的方法，新的方法会轮询查看管道的位置，并维护一个管道的队列，在一个管道的位置超过屏幕左边时，将其弹出队列，同时压入一个新的管道，并更新碰撞模型记录的变量，从而可以持续生成不同高度的管道

2.管道高度采用随机生成法，在声明一个新的管道对象时定义高度
3.用变量difficulty记录难度，0=easy 1=medium 2=hard，管道的空隙和移动速度根据难度进行调整，公式分别为：
          pipeDistance = 120 - difficulty * 17 
    
      moveDistance = common.visibleSize["width"]/(2*60*(1-difficulty*0.13))

4.客户端成绩储存与服务器端成绩储存方法同

5.客户端每局游戏开始时向服务器端请求成绩数据，服务器端组织当前难度下前十的成绩和用户为一个包发给客户端，客户端也以相同方法组织一个本地成绩包，用于稍后游戏结束时创建排行榜

6.用户注册/登陆信息传给服务端，给服务器发送成绩排名请求 于 network.py 实现

7.在与服务器通信的时候信息传输时是以json格式传输的。
在用户在进行登陆/注册操作是可以用字典，也就是键值对的形式作为传输载体。

登陆时：send_data['signInAuthentication'] = signInInformation

注册时：send_data['signUpAuthentication'] = signUpInformation

请求排名时：send_data['scoreRequest'] = scoreRequest

服务器可以根据key知道客户端发来的信息类型



服务端：
注册登陆请求的验证和回复，接收成绩并储存，给客户端发送所有成绩排名信息 于 server.py 实现
储存文件为signinlist.json，用于储存用户消息，scores_server.json，用于存储所有用户的成绩
signinlist.json的结构是这样的：{"userInfo": [{"userName": "shenwzh", "password": "123456"}, {"userName": "yyy", "password": "yyy"}]}
一个名为'userInfo'的json列表，其中存着（用户名，密码）的json对象。用户shenwzh和yyy是开发者，作为测试用户
scores_server.json的结构：[{"userName": "yyy", "scores": [{"difficulty": 0, "scores": [2, 2, 1, 10]}, {"difficulty": 1, "scores": [0, 1, 2]}, {"difficulty": 2, "scores": []}]}, {"userName": "shenwzh", "scores": [{"difficulty": 0, "scores": [0, 24]},{"difficulty": 1, "scores": [0]}, {"difficulty": 2, "scores": [8]}]}] 
一个json列表，列表存每个用户的成绩信息，是形如（用户名，得分）的json对象，得分又是一个json列表，存3个难度下的每次得分。
在服务端，收到来自客户端的消息，根据key进行回复。
如：key为'signInAuthentication'时，知道客户端在进行登陆操作，对其signInInformation与signinlist.json文件进行验证，若signInInformation存在signinlist.json中，则发回sendData = {'authenResult':True}，否则发回sendData = {'authenResult':False}
注册，发成绩等操作也是类似的。

AES对称加密解密（客户端&服务端共享私钥）：
AES128加密解密 于 myAES.py 实现
在所有socket通信消息发送之前进行AES加密，接受消息解密 于 netstream.py 实现
