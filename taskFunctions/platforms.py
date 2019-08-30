import pygame
from settings import *
from taskFunctions.spritesheets import *
from random import choice,randrange

class Platform(pygame.sprite.Sprite):
    def __init__(self,game):
        pygame.sprite.Sprite.__init__(self)
        self.game=game


    def getPlatform(self,x,y,images, num):
        self.image = images[num]
        self.image.set_colorkey(black)
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        #if randrange(100)<power_up_spawn_freq:
        #    PowerUps(self,self.game)

    def getImages(self):
        self.spritesheetsobj = SpriteSheet()
        self.images = [self.spritesheetsobj.imageLoad(213, 1764, 201, 100),
                       self.spritesheetsobj.imageLoad(213, 1662, 201, 100),
                       self.spritesheetsobj.imageLoad(218, 1558, 200, 100)]
        return self.images