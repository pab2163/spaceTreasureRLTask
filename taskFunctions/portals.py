import pygame
import sys
sys.path.append('..')
from settings import *
from random import choice, randrange, shuffle

class Portal(pygame.sprite.Sprite):
    def __init__(self,game):
        pygame.sprite.Sprite.__init__(self)
        self.game=game


    def getPortal(self,x,y,images, num):
        self.image = pygame.transform.scale(images[num], (120,120))
        self.image.set_colorkey(black)
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

    def getImages(self):
        green = 'images/greenPortal.png'
        yellow = 'images/yellowPortal.png'
        self.colorVec = [green, yellow]

        red = 'images/redPortal.png'
        purple = 'images/purplePortal.png'
        self.practiceColorVec = [red, purple]

        # Shuffle the portal colors so different participants have different combinations of color choices
        shuffle(self.colorVec)
        self.images = [pygame.image.load(self.colorVec[0]).convert_alpha(),
                       pygame.image.load(self.colorVec[1]).convert_alpha(),
                       pygame.image.load(self.practiceColorVec[0]).convert_alpha(),
                       pygame.image.load(self.practiceColorVec[1]).convert_alpha()] 
        return self.images