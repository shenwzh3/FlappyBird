# -*- coding: utf-8 -*-
from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
import random
from atlas import *
from bird import *
from score import *
from game_controller import *
import common

# take over to add the difficulty feature:easy medium hard
# take over to add the difficulty feature:easy medium hard

# constants
pipeCount = 2
pipeHeight = 320
pipeWidth = 52
# pipeDistance = 150    #上下管道间的距离
pipeInterval = 180    #两根管道的水平距离
waitDistance = 100    #开始时第一根管道距离屏幕最右侧的距离
heightOffset = 25     #管道的高度偏移值
# vars
PIPE_NEW = 0
PIPE_PASS = 1
pipes = {}    #contains nodes of pipes
pipeState = {}    #PIPE_NEW or PIPE_PASS
downPipeYPosition = {}    #朝下pipe的最下侧的y坐标
upPipeYPosition = {}  #朝上pipe的最上侧的y坐标
pipeIndex = 0

class ActorModel(object):
    def __init__(self, cx, cy, half_width, half_height,name):
            self.cshape = CircleShape(eu.Vector2(center_x, center_y), radius)
            self.name = name

def createPipes(layer, gameScene, spriteBird, score, difficulty):
    global g_score, movePipeFunc, calScoreFunc
    pipeDistance = 130 - difficulty * 20
    # 一开始先生成两个pipe，然后移动的过程中，pipe[1]不断替换pipe[0]，
    # 并生成新的pipe[1]    modified by Joe at 2017.12.12
    def initPipe():
        for i in range(0, pipeCount):
            #把downPipe和upPipe组合为singlePipe
            downPipe = CollidableRectSprite("pipe_down", 0, (pipeHeight + pipeDistance), pipeWidth/2, pipeHeight/2) #朝下的pipe而非在下方的pipe
            upPipe = CollidableRectSprite("pipe_up", 0, 0, pipeWidth/2, pipeHeight/2)  #朝上的pipe而非在上方的pipe
            singlePipe = CocosNode()
            singlePipe.add(downPipe, name="downPipe")
            singlePipe.add(upPipe, name="upPipe")
            
            #设置管道高度和位置
            # print 'ok\n'
            heightOffset = random.randint(-60,80)
            singlePipe.position=(common.visibleSize["width"] + i*pipeInterval + waitDistance, heightOffset)
            layer.add(singlePipe, z=10)
            pipes[i] = singlePipe
            pipeState[i] = PIPE_NEW
            upPipeYPosition[i] = heightOffset + pipeHeight/2
            downPipeYPosition[i] = heightOffset + pipeHeight/2 + pipeDistance

    # 每当一个管道移除界面，就重新创建一个管道 modified by Joe at 2017.12.12
    def movePipe(dt):
        moveDistance = common.visibleSize["width"]/(2*60)   # 移动速度和land一致
        pipes[0].position = (pipes[0].position[0]-moveDistance, pipes[0].position[1])
        pipes[1].position = (pipes[1].position[0]-moveDistance, pipes[1].position[1])
        if pipes[0].position[0] < -pipeWidth:
            pipeDel = pipes[0]
            pipes[0] = pipes[1]
            pipeState[0] = pipeState[1]
            upPipeYPosition[0] = upPipeYPosition[1]
            downPipeYPosition[0] = downPipeYPosition[1]
            layer.remove(pipeDel)
            # 开始新建管道
            downPipe = CollidableRectSprite("pipe_down", 0, (pipeHeight + pipeDistance), pipeWidth/2, pipeHeight/2) #朝下的pipe而非在下方的pipe
            upPipe = CollidableRectSprite("pipe_up", 0, 0, pipeWidth/2, pipeHeight/2)  #朝上的pipe而非在上方的pipe
            singlePipe = CocosNode()
            singlePipe.add(downPipe, name="downPipe")
            singlePipe.add(upPipe, name="upPipe")
            
            #设置管道高度和位置
            # print 'ok\n'
            heightOffset = random.randint(-80,80)
            singlePipe.position=(pipes[0].position[0] + pipeInterval, heightOffset)
            layer.add(singlePipe, z=10)
            pipes[1] = singlePipe
            pipeState[1] = PIPE_NEW
            upPipeYPosition[1] = heightOffset + pipeHeight/2
            downPipeYPosition[1] = heightOffset + pipeHeight/2 + pipeDistance


    def calScore(dt):
        global g_score
        birdXPosition = spriteBird.position[0]
        for i in range(0, pipeCount):
            if pipeState[i] == PIPE_NEW and pipes[i].position[0]< birdXPosition:
                pipeState[i] = PIPE_PASS
                g_score = g_score + 1
                setSpriteScores(g_score) #show score on top of screen
    
    g_score = score
    initPipe()
    movePipeFunc = movePipe
    calScoreFunc = calScore
    gameScene.schedule(movePipe)
    gameScene.schedule(calScore)
    return pipes

def removeMovePipeFunc(gameScene):
    global movePipeFunc
    if movePipeFunc != None:
        gameScene.unschedule(movePipeFunc)

def removeCalScoreFunc(gameScene):
    global calScoreFunc
    if calScoreFunc != None:
        gameScene.unschedule(calScoreFunc)

def getPipes():
    return pipes

def getUpPipeYPosition():
    return upPipeYPosition

def getPipeCount():
    return pipeCount

def getPipeWidth():
    return pipeWidth