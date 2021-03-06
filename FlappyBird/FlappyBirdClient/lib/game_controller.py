# -*- coding: utf-8 -*-
import cocos
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *  
from cocos.text  import *
from cocos.menu import *
import random
from pyglet.window import key
from atlas import *
from land import *
from bird import *
from score import *
from pipe import *
from collision import *
from network import *
import common

#vars
gameLayer = None
gameScene = None
# spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
ipTextField = None
errorLabel = None
isGamseStart = False
diffBuf = ["easy","medium","hard"]
difficulty = 0
userName = ''
password = ''
password_confirm = ''
scoreListOnline = []
scoreListLocal = []

def initGameLayer():
    global gameLayer, land_1, land_2
    # gameLayer: 游戏场景所在的layer
    gameLayer = Layer()
    # add background
    bg = createAtlasSprite("bg_day")
    bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    gameLayer.add(bg, z=0)
    # add moving land
    land_1, land_2 = createLand()
    gameLayer.add(land_1, z=10)
    gameLayer.add(land_2, z=10)
    # add gameLayer to gameScene
    gameScene.add(gameLayer)

def game_start(_gameScene):
    global gameScene
    # 给gameScene赋值
    gameScene = _gameScene
    initGameLayer()
    sign_button = SingleGameSignMenu()
    gameLayer.add(sign_button, z=20, name="sign_button")
    # start_button = SingleGameStartMenu()
    # gameLayer.add(start_button, z=20, name="start_button")

    # 向服务器端请求连接
    connect(gameScene) 

def createLabel(value, x, y):
    label=Label(value,  
        font_name='Times New Roman',  
        font_size=15, 
        color = (0,0,0,255), 
        width = common.visibleSize["width"] - 20,
        multiline = True,
        anchor_x='center',anchor_y='center')
    label.position = (x, y)
    return label

# single game start button的回调函数
def singleGameReady():
    # 给服务其发一个请求该难度下前十的成绩：
    sendScoreRequesttoServer({'difficulty':difficulty})
    setScoreListLocal()
    removeContent()
    ready = createAtlasSprite("text_ready")
    ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

    tutorial = createAtlasSprite("tutorial")
    tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    
    spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])

    #handling touch events
    class ReadyTouchHandler(cocos.layer.Layer):
        is_event_handler = True     #: enable director.window events

        def __init__(self):
            super( ReadyTouchHandler, self).__init__()

        def on_mouse_press (self, x, y, buttons, modifiers):
            """This function is called when any mouse button is pressed

            (x, y) are the physical coordinates of the mouse
            'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
            'modifiers' is a bitwise or of pyglet.window.key modifier constants
               (values like 'SHIFT', 'OPTION', 'ALT')
            """
            self.singleGameStart(buttons, x, y)
    
        # ready layer的回调函数
        def singleGameStart(self, eventType, x, y):
            isGamseStart = True
        
            spriteBird.gravity = gravity #gravity is from bird.py
            # handling bird touch events
            addTouchHandler(gameScene, isGamseStart, spriteBird)
            score = 0   #分数，飞过一个管子得到一分
            # add moving pipes
            pipes = createPipes(gameLayer, gameScene, spriteBird, score, difficulty)
            # 小鸟AI初始化
            # initAI(gameLayer)
            # add score
            createScoreLayer(gameLayer)
            # add collision detect
            addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2, difficulty)
            # remove startLayer
            gameScene.remove(readyLayer)

    readyLayer = ReadyTouchHandler()
    readyLayer.add(ready)
    readyLayer.add(tutorial)
    gameScene.add(readyLayer, z=10)

# 更改游戏结束时的界面 modified by Joe at 2017.12.17
def backToMainMenu():
    restartButton = RestartMenu()
    logOut_menu = logOutMenu()
    drawScorePanel()
    gameLayer.add(restartButton, z=50,name = "restartButton")
    gameLayer.add(logOut_menu,z = 20,name = "logOut_menu")

def showNotice():
    connected = connect(gameScene) # connect is from network.py
    if not connected:
        content = "Cannot connect to server"
        showContent(content)
    else:
        request_notice() # request_notice is from network.py

def showContent(content):
    removeContent()
    notice = createLabel(content, common.visibleSize["width"]/2+5, common.visibleSize["height"] * 9/10)
    gameLayer.add(notice, z=70, name="content")

def removeContent():
    try:
        gameLayer.remove("content")
    except Exception, e:
        pass


# 输入密码框类 modified by Joe at 2017.12.11
class EntryPwdMenuItem(MenuItem):

    value = property(lambda self: u''.join(self._value),
                     lambda self, v: setattr(self, '_value', list(v)))

    def __init__(self, label, callback_func, value, max_length=0):
        self._value = list(value)
        self._label = label
        super(EntryPwdMenuItem, self).__init__("%s %s" % (label, value), callback_func)
        self.max_length = max_length
        # 修改字体大小

    def on_text(self, text):
        if self.max_length == 0 or len(self._value) < self.max_length:
            self._value.append(text)
            self._calculate_value()
        return True

    def on_key_press(self, symbol, modifiers):
        if symbol == key.BACKSPACE:
            try:
                self._value.pop()
            except IndexError:
                pass
            self._calculate_value()
            return True

    def _calculate_value(self):
        self.callback_func(self.value)
        new_text = u"%s %s" % (self._label, '*' * len(self.value))
        self.item.text = new_text
        self.item_selected.text = new_text


 # 登陆输入框类 modified by Joe at 2017.12.11
class SigninMenu(Menu):
     """docstring for SigninMenu"""
     def __init__(self):

        super(SigninMenu, self).__init__()

        self.font_title = {
            'text': 'title',
            'font_name': 'Arial',
            'font_size': 32,
            'color': (192, 192, 192, 255),
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'dpi': 96,
            'x': 0, 'y': 0,
        }

        self.font_item = {
            'font_name': 'Arial',
            'font_size': 16,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 20,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }

        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (EntryMenuItem("Username:",setUserName,"")),
                (EntryPwdMenuItem("Password:",setPassword,"")),
                (ImageMenuItem(common.load_image("button_ok.png"), checkAccount))
                ]
        self.create_menu(items)

def setUserName(value):
    global userName
    userName = value

def setPassword(value):
    global password
    password = value

def getUserName():
    return userName
def getPassword():
    return password
def getDifficulty():
    return difficulty

def checkAccount():
    if len(userName) < 3 or len(userName) > 8:
        showContent('please enter the correct username')
    else:
        removeContent()
        gameLayer.remove("signIn_menu")
        # gameLayer.remove("signIn_menu")
        # # add moving bird
        # removeContent()
        # global spriteBird
        # spriteBird = creatBird()
        # gameLayer.add(spriteBird, z=20)
        # start_button = SingleGameStartMenu()  
        # gameLayer.add(start_button, z=20, name="start_button")
        signIn_Authen({'userName':userName,'password':password})
        waitLabel()
        # if check== False:
        #     showContent("Username or password incorrect!")
                 
def authenticationSucceed():
    # add moving bird
    removeContent()
    gameLayer.remove('wait_text')
    global spriteBird
    spriteBird = creatBird()
    gameLayer.add(spriteBird, z=20)
    start_button = SingleGameStartMenu()
    logOut_menu = logOutMenu()  
    gameLayer.add(start_button, z=20, name="start_button")
    gameLayer.add(logOut_menu,z = 20,name="logOut_menu")
# =======
#     if userName != "shenwzh" and password != "123456":
#         showContent("Username or password incorrect!")
#     else:
#         gameLayer.remove("signIn_menu")
#         # add moving bird
#         removeContent()
#         global spriteBird
#         spriteBird = creatBird()
#         gameLayer.add(spriteBird, z=20)
#         start_button = SingleGameStartMenu()
#         gameLayer.add(start_button, z=20, name="start_button")      
# >>>>>>> 97883b2fd6551d04f250179b02f77f74c3f5961e

# 登陆失败
def authenticationFailed():
    gameLayer.remove('wait_text')
    signIn_menu = SigninMenu()
    gameLayer.add(signIn_menu,z=20,name = 'signIn_menu')
    showContent('Username or password incorrect')
    


class RestartMenu(Menu):
    def __init__(self):  
        super(RestartMenu, self).__init__()

        self.font_item = {
            'font_name': 'Arial',
            'font_size': 40,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (192, 192, 192, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 40,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }

        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
                (ImageMenuItem(common.load_image("button_score.png"), showScore))
                ]  
        self.create_menu(items, layout_strategy = fixedPositionMenuLayout([(74,200),(154,200)]))

    def initMainMenu(self):
        gameScene.remove(gameLayer)
        initGameLayer()
        global spriteBird
        spriteBird = creatBird()
        gameLayer.add(spriteBird, z=20)
        start_button = SingleGameStartMenu()
        logOut_menu = logOutMenu()
        gameLayer.add(start_button, z=20, name="start_button") 
        gameLayer.add(logOut_menu, z=20, name="logOut_menu")
        isGamseStart = False
        # singleGameReady()

# 显示排行
def showScore():
    gameLayer.remove("restartButton")
    gameLayer.remove("logOut_menu")
    gameLayer.remove("scorePanel")
    gameLayer.remove("scoreLabel")
    gameLayer.remove("maxscoreLabel")
    drawRankLocal()
    buttonRankOk = rankOkMenu()
    gameLayer.add(buttonRankOk,z=31,name='buttonRankOk')



class SingleGameStartMenu(Menu):
    def __init__(self):  
        super(SingleGameStartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        # 舍弃原有的start按钮，直接从选择难度进入游戏 modified by Joe at 2017.12.11
        items = [
                (ImageMenuItem(common.load_image("button_easy.png"), self.gameStartEasy)),
                (ImageMenuItem(common.load_image("button_medium.png"), self.gameStartMedium)),
                (ImageMenuItem(common.load_image("button_hard.png"), self.gameStartHard)),
                # (MultipleMenuItem('difficulty',on_diff_choose(),diffBuf,0))
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def gameStartEasy(self):
        gameLayer.remove("start_button")
        gameLayer.remove("logOut_menu")
        global difficulty
        difficulty = 0
        # gameLayer.remove("diff_menu")
        singleGameReady()

    def gameStartMedium(self):
        gameLayer.remove("start_button")
        gameLayer.remove("logOut_menu")
        global difficulty
        difficulty = 1
        # gameLayer.remove("diff_menu")
        singleGameReady() 

    def gameStartHard(self):
        gameLayer.remove("start_button")
        gameLayer.remove("logOut_menu")
        global difficulty
        difficulty = 2
        # gameLayer.remove("diff_menu")
        singleGameReady()  


#注册、登陆菜单  modified by Joe at 2017/12/10
class SingleGameSignMenu(Menu):
    """docstring for SingleGameSignMenu"""
    def __init__(self):
        super(SingleGameSignMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_SignUp.png"), self.signUp)),
                (ImageMenuItem(common.load_image("button_SignIn.png"), self.signIn))
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())
    
    def signIn(self): #登陆
        gameLayer.remove("sign_button")
        # start_button = SingleGameStartMenu()
        # gameLayer.add(start_button, z=20, name="start_button")
        signIn_menu = SigninMenu()
        gameLayer.add(signIn_menu,z=20, name = "signIn_menu")

    def signUp(self): #注册
        gameLayer.remove("sign_button")
        signUp_menu = SignUpMenu()
        gameLayer.add(signUp_menu,z=20, name = "signUp_menu") 


 # 注册输入框类 modified by Joe at 2017.12.13
class SignUpMenu(Menu):
     """docstring for SignUpMenu"""
     def __init__(self):

        super(SignUpMenu, self).__init__()

        self.font_title = {
            'text': 'title',
            'font_name': 'Arial',
            'font_size': 32,
            'color': (192, 192, 192, 255),
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'dpi': 96,
            'x': 0, 'y': 0,
        }

        self.font_item = {
            'font_name': 'Arial',
            'font_size': 16,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 20,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }

        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (EntryMenuItem("Username:",setUserName,"")),
                (EntryPwdMenuItem("Password:",setPassword,"")),
                (EntryPwdMenuItem("PswConfirm:",confirmPassword,"")),
                (ImageMenuItem(common.load_image("button_ok.png"), checkSignUp))
                ]
        self.create_menu(items)

# 获取密码验证
def confirmPassword(value):
    global password_confirm
    password_confirm = value

# 进行注册
def checkSignUp():
    removeContent()
    if len(userName) > 8 or len(userName) < 3:
        showContent('username should be at least 3 characters and not longer than 8 characters')
    elif len(password) > 10 or len(password) < 6:
        showContent('password should be at least 6 characters and not longer than 10 characters')
    elif not password == password_confirm:
        showContent('the passwords you entered are different!')
    else:
        signUp_Authen({'userName':userName,'password':password})
        gameLayer.remove('signUp_menu')
        waitLabel()

# 注册失败
def signUpFailed():
    gameLayer.remove('wait_text')
    signUp_menu = SignUpMenu()
    gameLayer.add(signUp_menu,z = 20,name = 'signUp_menu')
    showContent('Username already existed')

# 注册成功
def signUpSucceed():
    gameLayer.remove('wait_text')
    global spriteBird
    spriteBird = creatBird()
    gameLayer.add(spriteBird, z=20)
    start_button = SingleGameStartMenu()
    logOut_menu = logOutMenu()  
    gameLayer.add(start_button, z=20, name="start_button")
    gameLayer.add(logOut_menu, z=20, name="logOut_menu")


# 为防止用户频繁点击按钮造成通讯错误，使用一个等待界面来过渡
# modified by Joe at 2017.12.13
def waitLabel():
    removeContent()
    wait_text = Label(
        "Waiting....",
        (common.visibleSize["width"]/2, common.visibleSize["height"]/2),
        font_size = 20,
        font_name = 'Arial',
        anchor_x = 'center',
        anchor_y = 'center'
        )
    gameLayer.add(wait_text,z=20,name ='wait_text')

# 切换用户菜单 modified by Joe at 2017.12.14
class logOutMenu(Menu):
    """docstring for logOutMenu"""
    def __init__(self):
        super(logOutMenu, self).__init__()

        self.font_title = {
            'text': 'title',
            'font_name': 'Arial',
            'font_size': 32,
            'color': (192, 192, 192, 255),
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'dpi': 96,
            'x': 0, 'y': 0,
        }

        self.font_item = {
            'font_name': 'Arial',
            'font_size': 32,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'right',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 35,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'right',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }

        self.menu_valign = TOP  
        self.menu_halign = RIGHT
        items = [
                (EntryMenuItem("",nofunc,userName)),
                (ImageMenuItem(common.load_image("button_logOut.png"), logOut))
                ]
        self.create_menu(items)  

# 咩事都冇
def nofunc():
    pass

# 登出函数
def logOut():
    global userName,Password,password_confirm
    userName = ""
    password = ""
    password_confirm = ""
    gameScene.remove(gameLayer)
    initGameLayer()
    # global spriteBird
    # spriteBird = creatBird()
    # gameLayer.add(spriteBird, z=20)
    sign_button = SingleGameSignMenu()
    gameLayer.add(sign_button, z=20, name="sign_button")
    isGamseStart = False

# 设置分数排行 modified by Joe at 2017.12.17
def setScoreListOnline(data):
    global scoreListOnline
    scoreListOnline = data
    # print 'scoreListOnline:',scoreListOnline

def setScoreListLocal():
    global scoreListLocal
    filename = common.get_filename('scores_client.json')
    file = open(filename,'r')  
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
    scoreListLocal = toReturn
    # print 'scoreListLocal:',scoreListLocal

# 显示分数板 modified by Joe at 2017.12.17
def drawScorePanel():
    score = getGameScore()
    maxlocal = 0
    maxscore = max(score,scoreListLocal[0][1],scoreListOnline[0][1])
    scorePanel = createAtlasSprite('score_panel')
    scorePanel.position = (common.visibleSize["width"]/2, common.visibleSize["height"] /2 + 30)
    gameLayer.add(scorePanel,z=30,name = 'scorePanel')
    scoreLabel = Label(str(score),
                            (180,292),
                            font_name='Arial',
                            bold = True,
                            color = (255,255,255,255),
                            font_size = 16)
    maxscoreLabel = Label(str(maxscore),
                            (180,257),
                            font_name='Arial',
                            bold = True,
                            color = (255,255,255,255),
                            font_size = 16)
    gameLayer.add(scoreLabel,z=31,name = 'scoreLabel')
    gameLayer.add(maxscoreLabel,z=31,name = 'maxscoreLabel')

# 画本地排名 modified by Joe at 2017.12.18
def drawRankLocal():
    def cmp(s):
        return s[1]
    toprint = sorted(scoreListLocal,key = cmp,reverse = True)
    listTitle = Label(
                'Mode: '+diffBuf[difficulty],
                (35,370),
                font_name='Arial',
                bold = True,
                color = (255,255,255,255),
                font_size = 20
                )
    gameLayer.add(listTitle,z=30,name="listTitle")

    listType = Label(
                'Local rank:',
                (60,340),
                font_name='Arial',
                bold = True,
                color = (255,255,255,255),
                font_size = 16
                )
    gameLayer.add(listType,z=30,name="listType")

    i = 0
    while i < 10 and i < len(toprint):
        userNameText = Label(
                        toprint[i][0],
                        (45,320 - i*17),
                        font_name='Arial',
                        color = (0,0,0,255),
                        font_size = 16
                        )
        scoreText = Label(
                    str(toprint[i][1]),
                    (155,320 - i*17),
                    font_name='Arial',
                    color = (0,0,0,255),
                    font_size = 16
                    )
        gameLayer.add(userNameText,z=30,name='userNameText'+str(i))
        gameLayer.add(scoreText,z=30,name='scoreText'+str(i))
        i = i + 1

    while i < 10:
        userNameText = Label(
                        '......',
                        (45,320 - i*17),
                        font_name='Arial',
                        color = (0,0,0,255),
                        font_size = 16
                        )
        scoreText = Label(
                    '......',
                    (155,320 - i*17),
                    font_name='Arial',
                    color = (0,0,0,255),
                    font_size = 16
                    )
        gameLayer.add(userNameText,z=30,name='userNameText'+str(i))
        gameLayer.add(scoreText,z=30,name='scoreText'+str(i))
        i = i + 1

    buttonRightArrow = rightArrowMenu()
    gameLayer.add(buttonRightArrow,z=30,name='buttonRightArrow')
    global buttonRightExist
    buttonRightExist = True

# 画线上排名 modified by Joe at 2017.12.18
def drawRankOnline():
    def cmp(s):
        return s[1]
    toprint = sorted(scoreListOnline,key = cmp,reverse = True)
    listTitle = Label(
                'Mode: '+diffBuf[difficulty],
                (35,370),
                font_name='Arial',
                bold = True,
                color = (255,255,255,255),
                font_size = 20
                )
    gameLayer.add(listTitle,z=30,name="listTitle")

    listType = Label(
                'Online rank:',
                (60,340),
                font_name='Arial',
                bold = True,
                color = (255,255,255,255),
                font_size = 16
                )
    gameLayer.add(listType,z=30,name="listType")

    i = 0
    while i < 10 and i < len(toprint):
        userNameText = Label(
                        toprint[i][0],
                        (45,320 - i*17),
                        font_name='Arial',
                        color = (0,0,0,255),
                        font_size = 16
                        )
        scoreText = Label(
                    str(toprint[i][1]),
                    (155,320 - i*17),
                    font_name='Arial',
                    color = (0,0,0,255),
                    font_size = 16
                    )
        gameLayer.add(userNameText,z=30,name='userNameText'+str(i))
        gameLayer.add(scoreText,z=30,name='scoreText'+str(i))
        i = i + 1

    while i < 10:
        userNameText = Label(
                        '......',
                        (45,320 - i*17),
                        font_name='Arial',
                        color = (0,0,0,255),
                        font_size = 16
                        )
        scoreText = Label(
                    '......',
                    (155,320 - i*17),
                    font_name='Arial',
                    color = (0,0,0,255),
                    font_size = 16
                    )
        gameLayer.add(userNameText,z=30,name='userNameText'+str(i))
        gameLayer.add(scoreText,z=30,name='scoreText'+str(i))
        i = i + 1

    buttonLeftArrow = leftArrowMenu()
    gameLayer.add(buttonLeftArrow,z=30,name='buttonLeftArrow')
    global buttonRightExist
    buttonRightExist = False

def deleteRank():
    if(buttonRightExist):
        gameLayer.remove('buttonRightArrow')
    else:
        gameLayer.remove('buttonLeftArrow')
    gameLayer.remove('listTitle')
    gameLayer.remove('listType')
    for i in range(0,10):
        gameLayer.remove('userNameText'+str(i))
        gameLayer.remove('scoreText'+str(i))

# 排名的右箭头 modified by Joe at 2017.12.18
class rightArrowMenu(Menu):
    """docstring for rightArrowMenu"""
    def __init__(self):
        super(rightArrowMenu, self).__init__()
        self.font_item = {
            'font_name': 'Arial',
            'font_size': 32,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'right',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 32,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'right',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }

        self.menu_valign = CENTER  
        self.menu_halign = RIGHT
        items = [
                (ImageMenuItem(common.load_image("button_right.png"), self.goRight)),
                ]
        self.create_menu(items)

    def goRight(self):
        deleteRank()
        drawRankOnline()

# 排名的左箭头  modified by Joe at 2017.12.18
class leftArrowMenu(Menu):
    """docstring for rightArrowMenu"""
    def __init__(self):
        super(leftArrowMenu, self).__init__()
        self.font_item = {
            'font_name': 'Arial',
            'font_size': 32,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'right',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 32,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'right',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }

        self.menu_valign = CENTER  
        self.menu_halign = LEFT
        items = [
                (ImageMenuItem(common.load_image("button_left.png"), self.goLeft)),
                ]
        self.create_menu(items)

    def goLeft(self):
        deleteRank()
        drawRankLocal()

# 排名底下的ok按键
class rankOkMenu(Menu):
    """docstring for rankOkMenu"""
    def __init__(self):
        super(rankOkMenu, self).__init__()
        self.font_item = {
            'font_name': 'Arial',
            'font_size': 18,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 22,
            'bold': False,
            'italic': False,
            'anchor_y': 'center',
            'anchor_x': 'center',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }

        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_ok.png"), self.goRestart))
                ]
        self.create_menu(items,layout_strategy = fixedPositionMenuLayout([(114,140)]))
    
    def goRestart(self):
        deleteRank()
        gameLayer.remove('buttonRankOk')
        backToMainMenu()    

# 为了话排名的时候不出bug modified by Joe at 2017.12.18
def appendScore():
    global scoreListLocal,scoreListOnline
    score = getGameScore()
    scoreListLocal.append((userName,score))
    scoreListOnline.append((userName,score))