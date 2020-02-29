# Define Alien class

import pygame
from settings import *
from taskFunctions.spritesheets import *
from random import choice,randrange
import numpy as np

class Alien(pygame.sprite.Sprite):
    def __init__(self,game):
        pygame.sprite.Sprite.__init__(self)
        self.game=game

    # Alien has x-y coordinates, an image file (indexed by num), and an opacity value (alpha)
    def getAlien(self,x,y,images, num, alpha):
        self.image = pygame.transform.scale(images[num], (100,100))
        self.image.set_colorkey(black)
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.image.set_alpha(alpha)

    # Get the images for each alien (psuedorandomized for position)
    def getImages(self):
        self.spritesheetsobj = SpriteSheet()
        if np.random.random(1)[0] > .5:
            self.images = [pygame.image.load('images/aliens/alien3.png').convert(),
                           pygame.image.load('images/aliens/alien4.png').convert(),
                           pygame.image.load('images/aliens/alien1.png').convert(),
                           pygame.image.load('images/aliens/alien2.png').convert(),
                           pygame.image.load('images/aliens/alien5.png').convert(),
                           pygame.image.load('images/aliens/alien6.png').convert(),
                           pygame.image.load('images/aliens/alien7.png').convert(),
                           pygame.image.load('images/aliens/alien8.png').convert()]
        else:
            self.images = [pygame.image.load('images/aliens/alien1.png').convert(),
                           pygame.image.load('images/aliens/alien2.png').convert(),
                           pygame.image.load('images/aliens/alien3.png').convert(),
                           pygame.image.load('images/aliens/alien4.png').convert(),
                           pygame.image.load('images/aliens/alien5.png').convert(),
                           pygame.image.load('images/aliens/alien6.png').convert(),
                           pygame.image.load('images/aliens/alien7.png').convert(),
                           pygame.image.load('images/aliens/alien8.png').convert()]
        return self.images
