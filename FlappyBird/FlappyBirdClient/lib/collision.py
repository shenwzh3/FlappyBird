# -*- coding: utf-8 -*-
from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
from cocos.euclid import *
import random
from atlas import *
from bird import *
from score import *
from game_controller import *
from network import *
import common 
import json

# contactListener
collision_manager = None
collision_func = None


def addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2,difficulty):
    global collision_manager, collision_func, upPipeCollided, isCollided, pipeDistance
    #设置land区域对应的刚体
    landSprite = CollidableRectSprite("land", (common.visibleSize["width"])/2, (atlas["land"]["height"] / 4 - 3), (common.visibleSize["width"])/2, (atlas["land"]["height"])/2)

    #pipe对应的刚体在pipe.py中设置
    pipes = getPipes()
    pipeCount = getPipeCount()
    upPipeY = getUpPipeYPosition()
    upPipeCollided = False
    isCollided = False
    pipeDistance = 120 - difficulty * 17

    #初始化碰撞管理器
    collision_manager = CollisionManagerBruteForce()
    #添加刚体到管理器中，从而处理刚体之间的碰撞关系
    collision_manager.add(landSprite)
    collision_manager.add(spriteBird)
    for i in range(0, 2):
        collision_manager.add(pipes[i].get("downPipe"))
        collision_manager.add(pipes[i].get("upPipe"))

    # 增加轮询添加刚体的方法  modified by Joe at 2017.12.12
    def collisionHandler(dt):
        global isCollided, upPipeCollided, collision_func
        # 添加判断，以判断是否有水管跑过去了
        if not (collision_manager.knows(pipes[0].get("downPipe")) and collision_manager.knows(pipes[1].get("downPipe"))):
            for i in range(0, 2):
                collision_manager.add(pipes[i].get("downPipe"))
                collision_manager.add(pipes[i].get("upPipe"))
        spriteBird.cshape.center = Vector2(spriteBird.position[0], spriteBird.position[1])
        for i in range(0, 2):
            pipes[i].get("downPipe").cshape.center = Vector2(pipes[i].position[0], pipes[i].position[1]+(atlas["pipe_up"]["height"] + pipeDistance)) 
            pipes[i].get("upPipe").cshape.center = Vector2(pipes[i].position[0], pipes[i].position[1])

        for other in collision_manager.iter_colliding(spriteBird):
            if other.name == 'land':
                print "on Contact Between Bird And Land Begin"
                spriteBird.gravity = 0
                upPipeCollided = True
            else:
                print "on Contact Between Bird And Pipe Begin"
                birdXPosition = spriteBird.position[0]
                birdYPosition = spriteBird.position[1]
                for i in range(0, pipeCount):
                    if (pipes[i].position[0]-atlas["pipe_up"]["width"]/2) <= birdXPosition and (pipes[i].position[0]+atlas["pipe_up"]["width"]/2) >= birdXPosition:
                        if (birdYPosition - upPipeY[i]) <= 25:
                            upPipeCollided = True
                            spriteBird.gravity = 0
                            break
                        else:
                            upPipeCollided = False
                            break
            isCollided = True

        if isCollided:
            gameOver(gameScene, land_1, land_2, spriteBird, upPipeCollided)

    collision_func = collisionHandler
    gameScene.schedule(collisionHandler)


def storeScoreInClient(scoreInformation):
    filename = common.get_filename('scores_client.json')
    file = open(filename,'r')  
    data = json.load(file)
    file.close()
    
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
                        



# when gameOver store locally and send to server the rate
def gameOver(gameScene, land_1, land_2, spriteBird, upPipeCollided):
    global collision_func
    land_1.stop()
    land_2.stop()
    removeMovePipeFunc(gameScene)
    removeCalScoreFunc(gameScene)
    removeBirdTouchHandler(gameScene)
    if upPipeCollided and collision_func:
        gameScene.unschedule(collision_func)
        spriteBird.stop()
         # ###### yyy add 12/15/17
        import game_controller
        import pipe
        # print game_controller.getUserName(),pipe.getGameScore()
        scoreInformation = {'userName':game_controller.getUserName(),'difficulty':game_controller.getDifficulty(),'score':pipe.getGameScore()}
        storeScoreInClient(scoreInformation)
        sendScoreToServer(scoreInformation)
        # 向服务器发送请求成绩数据
        # sendScoreRequesttoServer()
        # ######
        game_controller.appendScore()
        game_controller.backToMainMenu()    
   



    
# json file format:
# [
#     {
#         "userName": "yyy",
#         "scores": [
#             {
#                 "difficulty": 0,
#                 "scores": [
#                     1
#                 ]
#             },
#             {
#                 "difficulty": 1,
#                 "scores": [
#                     1
#                 ]
#             },
#             {
#                 "difficulty": 2,
#                 "scores": [
#                     1
#                 ]
#             }
#         ]
#     },
#     {
#         "userName": "shenwzh",
#         "scores": [
#             {
#                 "difficulty": 0,
#                 "scores": [
#                     1
#                 ]
#             },
#             {
#                 "difficulty": 1,
#                 "scores": [
#                     1
#                 ]
#             },
#             {
#                 "difficulty": 2,
#                 "scores": [
#                     1
#                 ]
#             }
#         ]
#     }
# ]