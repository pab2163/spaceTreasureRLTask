import pygame
from settings import *
from taskFunctions.spritesheets import *
from random import choice,randrange

class Coin(pygame.sprite.Sprite):
    def __init__(self,game):
        pygame.sprite.Sprite.__init__(self)
        self.game=game


    def getCoin(self,x,y,images, imageNum):
        self.image = images[imageNum]
        self.image = pygame.transform.scale(images[imageNum], (45,45))
        self.image.set_colorkey(black)
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        #if randrange(100)<power_up_spawn_freq:
        #    PowerUps(self,self.game)

    def getImages(self):
        self.spritesheetsobj = SpriteSheet()
        self.images = [self.spritesheetsobj.imageLoad(698, 1931,84,84)] # coin_gold.png
        return self.images
