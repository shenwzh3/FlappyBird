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

# constants
pipeCount = 2
pipeHeight = 320
pipeWidth = 52
pipeDistance = 100    #上下管道间的距离
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

def createPipes(layer, gameScene, spriteBird, score):
    global g_score, movePipeFunc, calScoreFunc
    def initPipe():
        for i in range(0, pipeCount):
            #把downPipe和upPipe组合为singlePipe
            downPipe = CollidableRectSprite("pipe_down", 0, (pipeHeight + pipeDistance), pipeWidth/2, pipeHeight/2) #朝下的pipe而非在下方的pipe
            upPipe = CollidableRectSprite("pipe_up", 0, 0, pipeWidth/2, pipeHeight/2)  #朝上的pipe而非在上方的pipe
            singlePipe = CocosNode()
            singlePipe.add(downPipe, name="downPipe")
            singlePipe.add(upPipe, name="upPipe")
            
            #设置管道高度和位置
            singlePipe.position=(common.visibleSize["width"] + i*pipeInterval + waitDistance, heightOffset)
            layer.add(singlePipe, z=10)
            pipes[i] = singlePipe
            pipeState[i] = PIPE_NEW
            upPipeYPosition[i] = heightOffset + pipeHeight/2
            downPipeYPosition[i] = heightOffset + pipeHeight/2 + pipeDistance

    def movePipe(dt):
        moveDistance = common.visibleSize["width"]/(2*60)   # 移动速度和land一致
        for i in range(0, pipeCount):
            pipes[i].position = (pipes[i].position[0]-moveDistance, pipes[i].position[1])
            if pipes[i].position[0] < -pipeWidth/2:
                pipeNode = pipes[i]
                pipeState[i] = PIPE_NEW
                next = i - 1
                if next < 0: next = pipeCount - 1
                pipeNode.position = (pipes[next].position[0] + pipeInterval, heightOffset)
                upPipeYPosition[i] = heightOffset + pipeHeight/2
                downPipeYPosition[i] = heightOffset + pipeHeight/2 + pipeDistance
                break

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