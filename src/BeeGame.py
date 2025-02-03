from cmu_graphics import *
import random
import math, time
from PIL import Image

def onAppStart(app):
    app.backgroundColor = 'lightSkyBlue'
    app.playerBeeX = app.width/2
    app.playerBeeY = app.height/2
    app.playerBeeRadius = 15
    app.playerBeeColor = None
    app.currentMouseX = None
    app.currentMouseY = None
    app.flowerList = []
    app.counter = 0
    app.toRemove = []
    app.pollenInventoryTop = []
    app.pollenInventoryBee = []
    app.id = 0
    app.toRemovePollen = []
    app.beeList = []
    # image is from: https://www.pngmart.com/image/659338
    # the code from the next line to line 30 is from the 15-112 image demo (basicPILMethods.py)
    app.image = Image.open("bee.png")
    app.imageWidth = app.image.width
    app.imageHeight = app.image.height
    app.imageReversed = app.image.transpose(Image.FLIP_LEFT_RIGHT)
    app.image = CMUImage(app.image)
    app.imageReversed = CMUImage(app.imageReversed)
    app.currentImagePlayer = app.imageReversed
    app.startCounter = 1
    app.countDown = 10

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.backgroundColor)
    playerBee = PlayerBee(app)
    if app.startCounter < 300:
        drawLabel("Welcome to the Bee Game!", app.width/2, app.height*1/8, size = 30, fill = 'darkOrange')
        drawLabel("The player bee will follow the mouse.", app.width/2, app.height*2/8, size = 30, fill = 'darkOrange')
        drawLabel("Collect pollen from flowers with pollen (filled circles).", app.width/2, app.height*3/8, size = 30, fill = 'darkOrange')
        drawLabel("Pollinate flowers that do not have pollen (ringed circles).", app.width/2, app.height*1/2, size = 30, fill = 'darkOrange')
        drawLabel("Helper bees will also help out.", app.width/2, app.height*5/8, size = 30, fill = 'darkOrange')
        drawLabel("Have fun!", app.width/2, app.height*6/8, size = 30, fill = 'darkOrange')
        drawLabel(f"The game will begin in: {app.countDown}", app.width/2, app.height*7/8, size = 30, fill = 'darkOrange')
    else:
        if len(app.flowerList) > 0:
            for flower in app.flowerList:
                flower.drawFlower()
        if len(app.beeList) > 0:
            for bee in app.beeList:
                bee.drawBee(app)
        playerBee.drawPlayer(app)

def onMouseMove(app, mouseX, mouseY):
    app.currentMouseX = mouseX
    app.currentMouseY = mouseY

def onStep(app):
    if app.startCounter < 300:
        if app.startCounter % 30 == 0:
            app.countDown -= 1
        app.startCounter += 1 
    else:
        playerBee = PlayerBee(app)
        playerBee.playerOnStep(app)
        if app.counter == 0:
            x = app.width
            y = app.height/2
            radius = 15
            color = None
            pollenInventoryBee = []
            target = None
            image = app.imageReversed
            newBee = Bee(x, y, radius, color, pollenInventoryBee, target, image)
            app.beeList.append(newBee)
        if app.counter == 1:
            x = 0
            y = app.height/2
            radius = 15
            color = None
            pollenInventoryBee = []
            target = None
            image = app.imageReversed
            newBee = Bee(x, y, radius, color, pollenInventoryBee, target, image)
            app.beeList.append(newBee)
        for bee in app.beeList:
            bee.beeOnStep(app)
        if app.counter % 60 == 0:
            x = random.randint(0, app.width)
            y = app.height
            radius = 15
            randomColor = random.randint(0, 2)
            if randomColor == 0:
                color = 'red'
            elif randomColor == 1:
                color = 'blue'
            else:
                color = 'purple'
            isPolinator = random.randint(0, 1)
            isGathered = True 
            if isPolinator == 1:
                isGathered = False
            isPollinated = False
            id = app.id
            app.id += 1
            newFlower = Flower(x, y, radius, color, isPolinator, isGathered, isPollinated, id)
            app.flowerList.append(newFlower)
        bestDistance = 100000
        inList = False
        for bee in app.beeList:
            if bee.target != None:
                for flower in app.flowerList:
                    if flower.id == bee.target.id:
                        inList = True
                        break
                if inList == False:
                    bee.target = None
                elif bee.target.isPolinator == 1 and bee.target.isGathered == True:
                    bee.target = None
                elif bee.target.isPolinator == 0 and bee.target.isPollinated == True:
                    bee.target = None
            else:
                if len(app.flowerList) == 0:
                    bee.target = None
                else:
                    if len(bee.pollenInventoryBee) == 0:
                        for flower in app.flowerList:
                            if distance(bee.x, bee.y, flower.x, flower.y) < bestDistance:
                                if flower.isPolinator == 1 and flower.isGathered == False:
                                    bestDistance = distance(bee.x, bee.y, flower.x, flower.y)
                                    bee.target = flower
                    else:
                        for flower in app.flowerList:
                            if distance(bee.x, bee.y, flower.x, flower.y) < bestDistance:
                                if flower.isPolinator == 0 and flower.isPollinated == False:
                                    for pollen in bee.pollenInventoryBee:
                                        if pollen.color == flower.color:
                                            bestDistance = distance(bee.x, bee.y, flower.x, flower.y)
                                            bee.target = flower
                                            break
                                if bee.target == None:
                                    for flower in app.flowerList:
                                        if distance(bee.x, bee.y, flower.x, flower.y) < bestDistance:
                                            if flower.isPolinator == 1 and flower.isGathered == False:
                                                bestDistance = distance(bee.x, bee.y, flower.x, flower.y)
                                                bee.target = flower

        if len(app.flowerList) > 0:
            for flower in app.flowerList:
                if distance(playerBee.x, playerBee.y, flower.x, flower.y) < playerBee.radius + flower.radius:
                    if flower.isPolinator == 1 and flower.isGathered == False:
                        flower.isGathered = True
                        playerBee.pollenInventoryTop.append(flower)
                        playerBee.pollenInventoryBee.append(flower)
                    if flower.isPolinator == 0 and flower.isPollinated == False and len(app.pollenInventoryTop) > 0:
                        for i in range(len(app.pollenInventoryTop)):
                            if app.pollenInventoryTop[i].color == flower.color:
                                if flower.radius < 30:
                                    for originalFlower in app.flowerList:
                                        if originalFlower.id == app.pollenInventoryTop[i].id:
                                            originalFlower.radius += 1
                                    flower.radius += 1       
                                else:
                                    app.toRemovePollen.append(i)
                                    flower.isPollinated = True
                                    break
                if len(app.toRemovePollen) > 0:
                    for i in app.toRemovePollen:
                        app.pollenInventoryTop.pop(i)
                        app.pollenInventoryBee.pop(i)
                app.toRemovePollen = []
                for bee in app.beeList:
                    if distance(bee.x, bee.y, flower.x, flower.y) < bee.radius + flower.radius:
                        if flower.isPolinator == 1 and flower.isGathered == False:
                            flower.isGathered = True
                            bee.pollenInventoryBee.append(flower)
                        if flower.isPolinator == 0 and flower.isPollinated == False and len(bee.pollenInventoryBee) > 0:
                            for i in range(len(bee.pollenInventoryBee)):
                                if bee.pollenInventoryBee[i].color == flower.color:
                                    if flower.radius < 30:
                                        for originalFlower in app.flowerList:
                                            if originalFlower.id == bee.pollenInventoryBee[i].id:
                                                originalFlower.radius += 1
                                        flower.radius += 1       
                                    else:
                                        app.toRemovePollen.append(i)
                                        flower.isPollinated = True
                                        break
                    if len(app.toRemovePollen) > 0:
                        for i in app.toRemovePollen:
                            bee.pollenInventoryBee.pop(i)
                    app.toRemovePollen = []
                flower.flowerOnStep()
        if len(app.flowerList) > 0:
            for i in range(len(app.flowerList)):
                if app.flowerList[i].y < 0:
                    app.toRemove.append(i)
        if len(app.toRemove) > 0:
            for i in range(len(app.toRemove) - 1, -1, -1):
                app.flowerList.pop(app.toRemove[i])
        app.toRemove = []
        app.counter += 1

class Bee:
    def __init__(self, x, y, radius, color, pollenInventoryBee, target, image):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.pollenInventoryBee = pollenInventoryBee
        self.target = target
        self.image = image

    def drawBee(self, app):
        drawCircle(self.x, self.y, self.radius, fill=self.color)
        drawImage(self.image, self.x, self.y-5, width=app.imageWidth/30, height=app.imageHeight/30, align='center')

        if len(self.pollenInventoryBee) > 0:
            pollenBeeX = self.x - 10
            pollenBeeY = self.y + self.radius
            for pollen in self.pollenInventoryBee:
                drawCircle(pollenBeeX, pollenBeeY, 15/2, fill=pollen.color)
                pollenBeeX += 5
    
    def beeOnStep(self, app):
        # adjust how fast the be moves
        speed = 30
        if self.target == None:
            self.x = self.x
            self.y = self.y
        else:
            if self.target.x > self.x:
                difference = abs(self.target.x - self.x)
                self.x = self.x + (1/speed)*difference
                self.image = app.image
            else:
                difference = abs(self.target.x - self.x)
                self.x = self.x - (1/speed)*difference
                self.image = app.imageReversed
            if self.target.y > self.y:
                difference = abs(self.target.y - self.y)
                self.y = self.y + (1/speed)*difference
            else:
                difference = abs(self.target.y - self.y)
                self.y = self.y - (1/speed)*difference

class PlayerBee:
    def __init__(self, app):
        self.x = app.playerBeeX
        self.y = app.playerBeeY
        self.radius = app.playerBeeRadius
        self.color = app.playerBeeColor
        self.pollenInventoryTop = app.pollenInventoryTop
        self.pollenInventoryBee = app.pollenInventoryBee

    def drawPlayer(self, app):
        drawCircle(self.x, self.y, self.radius, fill=self.color)
        drawImage(app.currentImagePlayer, self.x, self.y-5 , width=app.imageWidth/30, height=app.imageHeight/30, align='center')
        if len(self.pollenInventoryTop) > 0:
            pollenBeeX = self.x - 10
            pollenBeeY = self.y + self.radius
            for pollen in self.pollenInventoryBee:
                drawCircle(pollenBeeX, pollenBeeY, 15/2, fill=pollen.color)
                pollenBeeX += 5
            pollenTopX = 30
            pollenTopY = 30
            for pollen in self.pollenInventoryTop:
                drawCircle(pollenTopX, pollenTopY, 15, fill=pollen.color)
                drawCircle(pollenTopX, pollenTopY, 15*0.5, fill='lightSkyBlue')
                pollenTopX += pollen.radius*1.5 
    
    def playerOnStep(self, app):
        # adjust how fast the be moves
        speed = 30
        if app.currentMouseX != None:
            if app.currentMouseX > app.playerBeeX:
                difference = abs(app.currentMouseX - app.playerBeeX)
                app.playerBeeX = app.playerBeeX + (1/speed)*difference
                app.currentImagePlayer = app.image
            else:
                difference = abs(app.currentMouseX - app.playerBeeX)
                app.playerBeeX = app.playerBeeX - (1/speed)*difference
                app.currentImagePlayer = app.imageReversed
            if app.currentMouseY > app.playerBeeY:
                difference = abs(app.currentMouseY - app.playerBeeY)
                app.playerBeeY = app.playerBeeY + (1/speed)*difference
            else:
                difference = abs(app.currentMouseY - app.playerBeeY)
                app.playerBeeY = app.playerBeeY - (1/speed)*difference

class Flower:
    def __init__(self, x, y, radius, color, isPolinator, isGathered, isPollinated, id):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.isPolinator = isPolinator
        self.isGathered = isGathered
        self.isPollinated = isPollinated
        self.id = id

    def drawFlower(self):
        # 0 is false and 1 is true
        if self.isPolinator == 0:
            if self.isPollinated == True:
                drawCircle(self.x, self.y, self.radius, fill=self.color)
                drawCircle(self.x, self.y, self.radius*0.75, fill='lightSkyBlue')
                drawCircle(self.x, self.y, self.radius*0.50, fill=self.color)
            else:
                drawCircle(self.x, self.y, self.radius, fill=self.color)
                drawCircle(self.x, self.y, self.radius*0.75, fill='lightSkyBlue')
                drawCircle(self.x, self.y, self.radius*0.50, fill=self.color)
        else:
            if self.isGathered == True:
                drawCircle(self.x, self.y, self.radius, fill=self.color)
                drawCircle(self.x, self.y, self.radius*0.5, fill='lightSkyBlue')
            else:
                drawCircle(self.x, self.y, self.radius, fill=self.color)

    def flowerOnStep(self):
        self.x += math.sin(0.1*self.y)*2
        self.y -= 0.6

# This function was copied from homework 3.4.3 Moving Highlighting Dot
def distance(x0, y0, x1, y1):
    return ((x1 - x0)**2 + (y1 - y0)**2)**0.5

# Resize canvas here! (Change the two numbers in runApp())
def main():
    runApp(800, 800)

main()