# This script runs the Space Treasure game (Daw 2-Stage task variant), pulling in custom functions and sound/image files
# Paul A. Bloom
# August 29, 2019

## Built on pygame

# Import libraries and custom functions
import pygame
import numpy as np
import pandas as pd
import random
import datetime
from taskFunctions.lowPlatform import *
from settings import *
from taskFunctions.platforms import *
from taskFunctions.coins import *
from taskFunctions.textInput import *
from taskFunctions.strategyTextInput import *
from taskFunctions.portals import *
from taskFunctions.aliens import *
from os import path

# Define game class
# Importantly: setting max FPS so it doesn't move to fast on very fast computers.
class Game:
    def __init__(self): #initialize game window and other things for the game.
        pygame.init()
        pygame.mixer.init()
        self.maxFPS = 40

        # Initialize participant ID as blank, this will get filled in
        self.participantID = ''

        # Clock Stuff
        # Set start time for a reference point, and also get day for output filename
        self.clock = pygame.time.Clock()
        self.now = datetime.datetime.now()
        self.currentDay = str(self.now.month) + '_'\ + str(self.now.day) +  '_' + str(self.now.year)
        self.startTime = self.now.strftime("%H:%M")

        # Set up game display
        self.gameDisplay = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)
        self.gameDisplay.fill(white)
        self.avatar = ''
        pygame.display.set_caption("SPACE TREASURE!!")

        # Load lots of images!
        # Resize when appropriate
        self.img_avatar=pygame.sprite.Sprite()
        self.img_avatar.image=pygame.image.load('images/pikachu.png').convert_alpha()
        self.img_avatar.image = pygame.transform.scale(self.img_avatar.image, (50, 60))
        self.img_avatar.rect=self.img_avatar.image.get_rect()
        self.background = pygame.image.load('images/space2.jpg').convert()
        self.jupiter = pygame.image.load('images/jupiter.png').convert_alpha()
        self.jupiter = pygame.transform.scale(self.jupiter, (200, 200))
        self.moon = pygame.image.load('images/moon.png').convert_alpha()
        self.moon = pygame.transform.scale(self.moon, (200, 200))
        self.ladderStraight = pygame.image.load('images/ladderStraight.png').convert_alpha()
        self.ladderStraight = pygame.transform.scale(self.ladderStraight, (30, 350))
        self.ladderRight = pygame.image.load('images/ladderRight.png').convert_alpha()
        self.ladderRight = pygame.transform.scale(self.ladderRight, (300, 350))
        self.ladderLeft = pygame.image.load('images/ladderLeft.png').convert_alpha()
        self.ladderLeft = pygame.transform.scale(self.ladderLeft, (300, 350))
        self.ladderImage = pygame.transform.scale(self.ladderLeft, (200, 350))
        self.avatarChoiceScreen = pygame.image.load('images/avatarChoiceSlide.jpg').convert()
        self.avatarChoiceScreen  = pygame.transform.scale(self.avatarChoiceScreen, (display_width, display_height))
        self.smallerImage = pygame.transform.scale(self.avatarChoiceScreen, (display_width, display_height))

        # Define sprites
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.coins = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group() # only 1 platform for ground here
        self.portals = pygame.sprite.Group()
        self.playerSprite=pygame.sprite.Group()
        self.playerSprite.add(self.img_avatar)
        p1 = lowPlatform(0, display_height - 40, display_width, 40)
        coins_obj = Coin(self)
        platform_obj=Platform(self)
        portals_obj = Portal(self)

        # Get sprite images
        self.coins_images = coins_obj.getImages()
        self.platform_images=platform_obj.getImages()
        self.portals_images=portals_obj.getImages()
        self.portalColorVec = portals_obj.colorVec
        self.platforms.add(p1)
        self.aliens = pygame.sprite.Group()
        aliens_obj = Alien(self)
        self.aliens_images = aliens_obj.getImages()


        # Initialize other global variables
        vec=pygame.math.Vector2
        self.resize = False
        self.score=0
        self.bestLevel=0
        self.greenScore = False
        self.redScore = False
        self.font_name=pygame.font.match_font(Font_Name)
        self.numTrials = 200
        self.font = pygame.font.SysFont(None, 25)
        self.gameExit = False
        self.pos=vec(display_width/2 - 15,display_height)
        self.img_avatar.rect.topleft=[self.pos.x,self.pos.y]
        self.vel=vec(0,0)
        self.acc=vec(0,0)
        self.stage1Option = ''
        self.start_time = 0
        self.levelUps = 0
        self.load_data()

        # Read in reward probabilities
        self.rewardProbs = pd.read_csv('rewardProbs/rewardProbabilities2019-03-26.csv')

        # Sort columns for each of stage2 choices (1-4), keeping pairs together
        colRandomizer = np.random.random(1)[0]
        if colRandomizer <= .25:
            cols = ['stateCchoice1','stateCchoice2','stateBchoice1','stateBchoice2', 'trialNum']
            self.rewardProbs = self.rewardProbs[cols]
        elif colRandomizer > .25 and colRandomizer <= .5:
            cols = ['stateCchoice2','stateCchoice1','stateBchoice2','stateBchoice1','trialNum']
            self.rewardProbs = self.rewardProbs[cols]
        elif colRandomizer > .5 and colRandomizer <= .75:
            cols = ['stateBchoice1','stateBchoice2','stateCchoice1','stateCchoice2','trialNum']
            self.rewardProbs = self.rewardProbs[cols]
        elif colRandomizer > .75:
            cols = ['stateBchoice2','stateBchoice1','stateCchoice2','stateCchoice1','trialNum']
            self.rewardProbs = self.rewardProbs[cols]

        # From left to right (1 = most left, etc) define alien reward probability column names
        self.rewardProbs.columns = ['alien1Prob', 'alien2Prob', 'alien3Prob', 'alien4Prob', 'trialNum']
        print(colRandomizer)
        print(self.rewardProbs.head())

    # Loads sound and image data
    def load_data(self):
        self.dir = path.dirname(__file__)

        # load coin pile image
        self.coinPile =pygame.image.load('images/coinPile.png').convert_alpha()
        self.coinPile = pygame.transform.scale(self.coinPile, (150, 150))

        # load sounds/music
        self.sound_dir=path.join(self.dir,'sound')
        self.coin_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'smrpg_coin.wav'))
        self.error_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'comp_alert.wav'))
        self.levelUp_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'smb_powerup.wav'))
        self.portal1Sound = pygame.mixer.Sound(path.join(self.sound_dir, 'portal1.wav'))
        self.portal2Sound = pygame.mixer.Sound(path.join(self.sound_dir, 'portal2.wav'))
        self.ray = pygame.mixer.Sound(path.join(self.sound_dir, 'ray.wav'))
        self.rocket = pygame.mixer.Sound(path.join(self.sound_dir, 'rocket.wav'))
        self.powerup = pygame.mixer.Sound(path.join(self.sound_dir, 'powerup.wav'))
        self.lossSound = pygame.mixer.Sound(path.join(self.sound_dir,'lossSound.wav'))
        self.lossSound.set_volume(.5)
        self.whee = pygame.mixer.Sound(path.join(self.sound_dir,'whee.wav'))
        self.music = pygame.mixer.music.load(path.join(self.sound_dir,'music/gameMusic.wav'))


        # Set up transition probabilities
        self.transitionsVector = self.makeTransitions(self.numTrials)

        # Load intro slides
        self.introSlideImages = [pygame.image.load('images/instructions/Slide01.jpg').convert(),
                                 pygame.image.load('images/instructions/Slide02.jpg').convert(),
                                 pygame.image.load('images/instructions/Slide06.jpg').convert(),
                                 pygame.image.load('images/instructions/Slide07.jpg').convert()]

        # Load Question Slides
        self.postQuestionImages = [pygame.image.load('images/postQuestions/Slide09.jpg').convert(),
                                 pygame.image.load('images/postQuestions/Slide10.jpg').convert(),
                                 pygame.image.load('images/postQuestions/Slide11.jpg').convert(),
                                 pygame.image.load('images/postQuestions/Slide12.jpg').convert(),
                                 pygame.image.load('images/postQuestions/Slide14.jpg').convert(),
                                 pygame.image.load('images/postQuestions/Slide13.jpg').convert()]

        self.reminderImages =  [pygame.image.load('images/reminders/Slide06.jpg').convert(),
                                 pygame.image.load('images/reminders/Slide07.jpg').convert()]

    # Returns a vector of transitions predetermined before task starts for nTrials trials (200 in our case)
    # 1 = common, 0 = rare
    # Each particint will always have exactly 70% common, 30% rare
    # First 10 trials will also contain exactly 7 common, 3 rare
    def makeTransitions(self, nTrials):
        # First 10 trials: exactly 7 will be common, 3 will be rare
        first10Common = np.repeat(1,7)
        first10Rare = np.repeat(0,3)
        first10 = np.concatenate((first10Common,first10Rare), axis = 0)
        np.random.shuffle(first10)

        # Exactly 70% of all trials will also be common, 30% rare.
        # Other than first 10 trials, common/rare transitions shuffled
        commonTrials = np.repeat(1,.7*(nTrials - 10))
        rareTrials = np.repeat(0, .3*(nTrials -10))
        laterTrials = np.concatenate((commonTrials, rareTrials), axis = 0)
        np.random.shuffle(laterTrials)
        allTrials = np.concatenate((first10, laterTrials), axis = 0)
        return(allTrials)

    # Refreshes items on screen, background
    # Order is important here, some things are refreshed and displayed conditionally depending on the stage of the task (i.e. ladders)
    def updateScreen(self, cur_background):

        # Get time and update platforms, coins
        now_time=pygame.time.get_ticks()
        self.img_avatar.rect.midbottom = [self.pos.x, self.pos.y]
        self.platforms.update()
        self.coins.update()
        self.playerSprite.update( )

        # Draw background first, then planets, then coins/platforms/portals/aliens
        self.gameDisplay.blit(self.background,(0,0))
        self.gameDisplay.blit(self.jupiter, (display_width/2 + 50, display_height/2 - 200))
        self.gameDisplay.blit(self.moon, (display_width/2 - 250, display_height/2 - 200))
        self.coins.draw(self.gameDisplay)
        self.platforms.draw(self.gameDisplay)
        self.portals.draw(self.gameDisplay)
        self.aliens.draw(self.gameDisplay)


        # Ladder Display conditional on choice and transition
        if (self.ladderImage == self.ladderRight) or (self.ladderImage == self.ladderLeft):
            self.gameDisplay.blit(self.ladderImage, (display_width/2 - 150, display_height - 400))
        elif self.ladderImage == self.ladderStraight:
            if self.ladderPos == 'r':
                self.gameDisplay.blit(self.ladderStraight, (display_width/2 + 110, display_height - 400))
            else:
                self.gameDisplay.blit(self.ladderStraight, (display_width/2 - 160, display_height - 400))
        # Draw sprite
        self.playerSprite.draw(self.gameDisplay)

        # Draw score
        if self.greenScore:
           self.messageToScreen("SCORE : "+(str)(self.score), 50, black, display_width / 2 , 15, green)
        elif self.redScore:
            self.messageToScreen("SCORE : "+(str)(self.score), 50, black, display_width / 2 , 15, red)
        else:
            self.messageToScreen("SCORE : "+(str)(self.score), 50, white, display_width / 2 , 15, black)
        pygame.display.update()

    # Run game!
    # This is after avatar and participant ID selection
    def run(self):
        # check to make sure frameRate isn't too low
        #print(self.clock.get_fps())
        compFPS = self.clock.get_fps()
        if compFPS < 40:
            self.lowFPS(compFPS)
        #print(self.avatar)
        if self.avatar == 'pikachu':
            self.img_avatar.image=pygame.image.load('images/pikachu.png').convert_alpha()
            self.img_avatar.image = pygame.transform.scale(self.img_avatar.image, (50, 60))
            self.bigAvatar =pygame.image.load('images/pikachu.png').convert_alpha()
            self.bigAvatar = pygame.transform.scale(self.bigAvatar, (150, 180))
        elif self.avatar == 'blackPanther':
            self.img_avatar.image=pygame.image.load('images/blackPanther2.png').convert_alpha()
            self.img_avatar.image = pygame.transform.scale(self.img_avatar.image, (60, 70))
            self.bigAvatar =pygame.image.load('images/blackPanther2.png').convert_alpha()
            self.bigAvatar = pygame.transform.scale(self.bigAvatar, (180, 210))
        elif self.avatar == 'spiderMan':
            self.img_avatar.image=pygame.image.load('images/spiderMan2.png').convert_alpha()
            self.img_avatar.image = pygame.transform.scale(self.img_avatar.image, (65, 65))
            self.bigAvatar =pygame.image.load('images/spiderMan2.png').convert_alpha()
            self.bigAvatar = pygame.transform.scale(self.bigAvatar, (135, 135))
        elif self.avatar == 'chloe':
            self.img_avatar.image=pygame.image.load('images/chloe.png').convert_alpha()
            self.img_avatar.image = pygame.transform.scale(self.img_avatar.image, (70, 70))
            self.bigAvatar =pygame.image.load('images/chloe.png').convert_alpha()
            self.bigAvatar = pygame.transform.scale(self.bigAvatar, (210, 210))
        self.img_avatar.rect=self.img_avatar.image.get_rect()

        # Initialize dataframe for output
        col_names = ['participantID']
        self.taskDataFrame  = pd.DataFrame(columns = col_names, index = range(1,self.numTrials + 1))
        self.taskDataFrame['participantID'] = self.participantID
        self.taskDataFrame['date'] = self.currentDay
        self.taskDataFrame['avatar'] = self.avatar
        self.taskDataFrame['startTime'] = self.startTime
        self.taskDataFrame['color0'] = self.portalColorVec[0]
        self.taskDataFrame['color1'] = self.portalColorVec[1]

        # append reward probabilities for each alien to the output dataframe
        reindexedRewardProbs = self.rewardProbs
        reindexedRewardProbs.index = np.arange(1, len(reindexedRewardProbs) + 1)
        self.taskDataFrame = pd.concat([self.taskDataFrame, reindexedRewardProbs], axis = 1)

        # Run a block of the task!
        self.gameOver = False
        self.block()

        # End game and do post-questions
        pygame.mixer.music.fadeout(500)
        self.postQuestions()

        # Timing to complete whole game
        finalTime = pygame.time.get_ticks()
        self.taskDataFrame['taskDuration'] = finalTime

        # Write out data, whether quit early or complete (mark if incomplete in file name)
        if self.gameExit:
            self.taskDataFrame.to_csv('../data/%s_incomplete_%s.csv'%(self.participantID, self.currentDay), index = False)
        else:
            self.taskDataFrame.to_csv('../data/%s_%s.csv'%(self.participantID, self.currentDay), index = False)

        # Quit
        pygame.quit()
        quit()

    # Run the task! Including practice
    def block(self):
        # Practice trials! Slides/advancing contingent on spacebar presses
        self.img_avatar.rect.midbottom = [self.pos.x, self.pos.y]
        now_time=pygame.time.get_ticks()
        self.playerSprite.update( )
        self.playerSprite.update( )
        self.gameDisplay.blit(self.background,(0,0))
        self.alienSprites = [Alien(self), Alien(self), Alien(self), Alien(self)]
        self.alienSprites[0].getAlien(10, 100, self.aliens_images, 6, 255)
        self.alienSprites[1].getAlien(100, 100, self.aliens_images, 7, 255)
        self.alienSprites[2].getAlien(300, 100, self.aliens_images, 4, 255)
        self.alienSprites[3].getAlien(390, 100, self.aliens_images, 5, 255)
        self.aliens.add(self.alienSprites)
        self.aliens.update()
        self.aliens.draw(self.gameDisplay)
        self.playerSprite.draw(self.gameDisplay)
        self.updateScreen(self.background)
        self.practiceTrials(1)
        self.practiceTrials(2)
        self.aliens.empty()
        self.alienSprites = [Alien(self), Alien(self), Alien(self), Alien(self)]
        self.alienSprites[0].getAlien(10, 100, self.aliens_images, 0, 255)
        self.alienSprites[1].getAlien(100, 100, self.aliens_images, 1, 255)
        self.alienSprites[2].getAlien(300, 100, self.aliens_images, 2, 255)
        self.alienSprites[3].getAlien(390, 100, self.aliens_images, 3, 255)
        self.aliens.add(self.alienSprites)
        self.aliens.update()
        self.aliens.draw(self.gameDisplay)
        leftPortalColor = 0
        rightPortalColor = 1
        slideImage= pygame.transform.scale(self.introSlideImages[2], (display_width, display_height))
        self.portalLeft = Portal(self)
        self.portalLeft.getPortal(display_width/2 - 200, display_height - 100, self.portals_images, leftPortalColor)
        self.portalRight = Portal(self)
        self.portalRight.getPortal(display_width/2 + 75, display_height - 100, self.portals_images, rightPortalColor)
        self.portals.add(self.portalLeft)
        self.portals.add(self.portalRight)
        self.gameDisplay.blit(slideImage,(0,0))
        self.portals.draw(self.gameDisplay)
        pygame.display.update()
        self.waitForSpace()
        self.portals.empty()
        self.ray.play()
        slideImage= pygame.transform.scale(self.introSlideImages[3], (display_width, display_height))
        self.gameDisplay.blit(slideImage,(0,0))
        pygame.display.update()
        self.waitForSpace()
        self.ray.play()
        pygame.mixer.music.play(loops=-1)

        # Actually run all trials of the task in loop
        for trial in range(1, self.numTrials + 1):
            if trial == 6:
                self.ruleReminder()
            if not self.gameExit:
                self.taskDataFrame.loc[trial, 'trialStartTime'] = pygame.time.get_ticks()
                self.stage1(trial)
                self.taskDataFrame.loc[trial, 'trialEndTime'] = pygame.time.get_ticks()
                self.taskDataFrame.loc[trial, 'trialDuration'] = self.taskDataFrame.loc[trial, 'trialEndTime'] - self.taskDataFrame.loc[trial, 'trialStartTime']
                if trial == int(self.numTrials)/2:
                    self.takeABreak()
        self.pos = vec(display_width/2 - 15, display_height)

    # Function for stage 1 of each trial (portal selection)
    def stage1(self, trial):
        self.alienSprites[0].getAlien(10, 100, self.aliens_images, 0, 100)
        self.alienSprites[1].getAlien(100, 100, self.aliens_images, 1, 100)
        self.alienSprites[2].getAlien(300, 100, self.aliens_images, 2, 100)
        self.alienSprites[3].getAlien(390, 100, self.aliens_images, 3, 100)
        self.aliens.update()
        self.aliens.draw(self.gameDisplay)
        self.ladderImage = self.coinPile
        self.pos = vec(display_width/2 - 15, display_height)
        self.greenScore = False
        self.redScore = False
        self.img_avatar.image = pygame.transform.scale(self.img_avatar.image, (70,70))
        randStage1leftRight = np.random.random(1)[0]

        # Left portal always color 0
        leftPortalColor = 0
        rightPortalColor = 1


        # Draw Portals
        self.portalLeft = Portal(self)
        self.portalLeft.getPortal(display_width/2 - 200, self.pos.y - 120 , self.portals_images, leftPortalColor)
        self.portalRight = Portal(self)
        self.portalRight.getPortal(display_width/2 + 75, self.pos.y - 120 , self.portals_images, rightPortalColor)
        self.portals.add(self.portalLeft)
        self.portals.add(self.portalRight)
        self.portals.update()
        self.platforms.draw(self.gameDisplay)
        self.updateScreen(self.background)

        # Portals jump!
        for i in range(1,9):
            self.clock.tick_busy_loop(self.maxFPS)
            self.portalLeft.rect.y -= 10*np.sin(i*1.5)
            self.portalRight.rect.y -= 10*np.sin(i*1.5)
            self.updateScreen(self.background)


        self.getAction1(trial, practice = False)

        # Update data
        self.taskDataFrame.loc[trial, 'curScore'] = self.score
        self.taskDataFrame.loc[trial, 'leftPortalColor'] = leftPortalColor
        self.taskDataFrame.loc[trial, 'rightPortalColor'] = rightPortalColor

        #print(str(self.taskDataFrame.loc[trial, 'leftPortalColor']) + ' left')
        # Go to 2nd stage state probabilisitcally based on chosen portal
        # Common
        if self.transitionsVector[trial-1] == 1:
            self.taskDataFrame.loc[trial, 'transitionType'] = 'common'
            #print('common!')
            if self.keyname == 'l':
                if leftPortalColor == 0:
                    stage2Type = 1
                elif leftPortalColor == 1:
                    stage2Type = 2
                self.stage2(trial,stage2Type, leftPortalColor)
            elif self.keyname == 'r':
                if leftPortalColor == 0:
                    stage2Type = 2
                elif leftPortalColor == 1:
                    stage2Type = 1
                self.stage2(trial,stage2Type, rightPortalColor)
        # Rare
        else:
            self.taskDataFrame.loc[trial, 'transitionType'] = 'rare'
            #print('rare!')
            if self.keyname == 'l':
                if leftPortalColor == 0:
                    stage2Type = 2
                elif leftPortalColor == 1:
                    stage2Type = 1
                self.stage2(trial,stage2Type, leftPortalColor)
            elif self.keyname == 'r':
                if leftPortalColor == 0:
                    stage2Type = 1
                elif leftPortalColor == 1:
                    stage2Type = 2
                self.stage2(trial,stage2Type, rightPortalColor)

    # Function for getting participant choice at stage1
    def getAction1(self, trial, practice):
        self.acc=vec(0,gravity)
        pygame.event.clear()
        beginWait = pygame.time.get_ticks()
        reminded = False
        while True:
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                self.gameExit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.keyname = 'l'
                    break
                if event.key == pygame.K_RIGHT:
                    self.keyname = 'r'
                    break
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT and mods & pygame.KMOD_ALT:
                    waiting=False
                    self.gameExit=True
            if practice == False:
                waitTime = pygame.time.get_ticks() - beginWait
                if (waitTime > 2500) and (reminded == False):
                    self.speedReminder()
                    reminded = True
        self.taskDataFrame.loc[trial, 'rtStage1'] = pygame.time.get_ticks() - beginWait

    # Function for stage 2 (alien choice at planets)
    def stage2(self, trial, stage2Type, portalColor):
        #print("stage2type" + str(stage2Type))
        # Update data
        self.taskDataFrame.loc[trial, 'choiceSideStage1'] = self.keyname
        if self.taskDataFrame.loc[trial, 'choiceSideStage1'] == 'l':
            self.taskDataFrame.loc[trial, 'choicePortal'] = self.taskDataFrame.loc[trial, 'leftPortalColor']
        elif self.taskDataFrame.loc[trial, 'choiceSideStage1'] == 'r':
            self.taskDataFrame.loc[trial, 'choicePortal'] = self.taskDataFrame.loc[trial, 'rightPortalColor']
        #print('Choice Portal:' + str(self.taskDataFrame.loc[trial, 'choicePortal']))
        self.taskDataFrame.loc[trial, 'stage2Type'] = stage2Type
        self.ladderPos = self.keyname
        beginLoop = pygame.time.get_ticks()
        loopTime = 0
        if self.keyname == 'l':
            self.vel.x = -35
            self.vel.y = 0
        else:
            self.vel.x = 35
            self.vel.y = 0
        self.portal2Sound.play()
        for i in range(1,5):
            self.clock.tick_busy_loop(self.maxFPS)
            self.pos+=self.vel
            self.updateScreen(self.background)
        if self.ladderPos == 'l':
            self.portals.remove(self.portalRight)
        else:
            self.portals.remove(self.portalLeft)
        upperPortal = Portal(self)
        pygame.time.wait(100)
        if stage2Type == 2:
            if self.ladderPos == 'r':
                self.ladderImage = self.ladderStraight
                self.vel.y = -90
                self.vel.x = 0
            else:
                self.ladderImage = self.ladderRight
                self.vel.y = -90
                self.vel.x = 70
            for i in range(1, 5):
                self.clock.tick_busy_loop(self.maxFPS)
                self.pos+=self.vel
                self.updateScreen(self.background)
            upperPortal.getPortal(display_width/2 + 75, display_height/2 - 100, self.portals_images, portalColor)
        else:
            if self.ladderPos == 'l':
                self.ladderImage = self.ladderStraight
                self.vel.y = -90
                self.vel.x = 0
            else:
                self.ladderImage = self.ladderLeft
                self.vel.y = -90
                self.vel.x = -70
            for i in range(1, 5):
                self.clock.tick_busy_loop(self.maxFPS)
                self.pos+=self.vel
                self.updateScreen(self.background)
            upperPortal.getPortal(display_width/2 - 200, display_height/2 - 100, self.portals_images, portalColor)
        self.vel.y = 0
        self.vel.x = 0
        self.portals.add(upperPortal)
        self.portals.update()
        self.portals.draw(self.gameDisplay)

        # Brighten aliens on chosen planet
        if stage2Type == 1:
            self.alienSprites[0].getAlien(10, 100, self.aliens_images, 0, 255)
            self.alienSprites[1].getAlien(100, 100, self.aliens_images, 1, 255)
        else:
            self.alienSprites[2].getAlien(300, 100, self.aliens_images, 2, 255)
            self.alienSprites[3].getAlien(390, 100, self.aliens_images, 3, 255)
        self.aliens.update()
        self.aliens.draw(self.gameDisplay)
        self.updateScreen(self.background)

        # Get choice for stage2

        self.getAction2(trial)

        # Animation for stage2 action and outcome
        self.choice2Movement(trial, stage2Type)

        # Outcome of trial
        self.stage2Outcome(trial, stage2Type)

        #if stage2Type == 1:
        self.updateScreen(self.background)
        pygame.time.wait(500)

        # clear for next trial
        self.coins.empty()
        self.portals.empty()

    # Function to get participant action at stage 2
    def getAction2(self, trial):
        pygame.event.clear()
        beginWait = pygame.time.get_ticks()
        reminded = False
        while True:
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                self.gameExit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.keyname = 'l'
                    break
                if event.key == pygame.K_RIGHT:
                    self.keyname = 'r'
                    break
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT and mods & pygame.KMOD_ALT:
                    waiting=False
                    self.gameExit=True
            waitTime = pygame.time.get_ticks() - beginWait
            if (waitTime > 2500) and (reminded == False):
                self.speedReminder()
                reminded = True
        self.taskDataFrame.loc[trial, 'rtStage2'] = pygame.time.get_ticks() - beginWait


    # Control movement of participnat to alien depending on stage2 choice
    def choice2Movement(self, trial, stage2Type):
        # Movement of avatar to alien
        if self.keyname == 'l':
            self.vel.y = -30
            self.vel.x = -10
        elif self.keyname == 'r':
            self.vel.y = -30
            self.vel.x = 10
        for i in range(1, 5):
            self.clock.tick_busy_loop(self.maxFPS)
            self.pos+=self.vel
            self.updateScreen(self.background)
        self.taskDataFrame.loc[trial, 'choiceSideStage2'] = self.keyname

    # Outcome of participant's choice at stage 2 (reward vs. no reward)
    def stage2Outcome(self, trial, stage2Type):
        self.rewardVec = self.rewardProbs.iloc[trial-1, 0:4]

        # Define alien choice
        if self.keyname == 'l':
            if stage2Type == 1:
                alienChoice = 1
            elif stage2Type == 2:
                alienChoice = 3
        elif self.keyname == 'r':
            if stage2Type == 1:
                alienChoice = 2
            elif stage2Type == 2:
                alienChoice = 4
        self.taskDataFrame.loc[trial, 'choiceStage2'] = alienChoice
        #print('alienChoice' + str(alienChoice))
        # Determine if reward or no
        if alienChoice == 1:
            trialRewardProb = self.rewardVec[0]
        elif alienChoice == 2:
            trialRewardProb = self.rewardVec[1]
        elif alienChoice == 3:
            trialRewardProb = self.rewardVec[2]
        elif alienChoice == 4:
            trialRewardProb = self.rewardVec[3]
        if trialRewardProb > np.random.random(1)[0]:
            self.taskDataFrame.loc[trial, 'reward'] = 1
        else:
            self.taskDataFrame.loc[trial, 'reward'] = 0

        # which alien image to move
        if self.taskDataFrame.loc[trial, 'choiceStage2'] == 1:
            alien2Move = self.alienSprites[0]
        elif self.taskDataFrame.loc[trial, 'choiceStage2'] == 2:
           alien2Move = self.alienSprites[1]
        elif self.taskDataFrame.loc[trial, 'choiceStage2'] == 3:
           alien2Move = self.alienSprites[2]
        elif self.taskDataFrame.loc[trial, 'choiceStage2'] == 4:
           alien2Move = self.alienSprites[3]

        # Reward animation
        if self.taskDataFrame.loc[trial, 'reward'] == 1:
            self.reward(trial, alien2Move)
        # No reward animation
        else:
            self.noReward(trial, alien2Move)

    # Reward animation and scoring
    def reward(self, trial, alien2Move):
        self.whee.play()
        for i in range(1,9):
            self.clock.tick_busy_loop(self.maxFPS)
            alien2Move.rect.y -= 10*np.sin(i*1.5)
            self.updateScreen(self.background)
        alien2Move.rect.y = 100
        self.coin_sound.play()
        coinReward = Coin(self)
        coinReward.getCoin(alien2Move.rect.x + 10, alien2Move.rect.y - 25, self.coins_images, 0)
        self.coins.add(coinReward)
        self.coins.update()
        self.coins.draw(self.gameDisplay)
        self.score += 1
        if (self.score % 20 == 0) and (self.score != self.bestLevel):
            self.levelUp()

    # No reward animation
    def noReward(self, trial, alien2Move):
        prevX = alien2Move.rect.x
        self.lossSound.play()
        for i in range(1,9):
            alien2Move.rect.x
            self.clock.tick_busy_loop(self.maxFPS)
            alien2Move.rect.x -= 10*np.sin(i*1.5)
            self.updateScreen(self.background)
        alien2Move.rect.x = prevX

    # Level up at intervals of 20 points!
    def levelUp(self):
        self.levelUp_sound.play()
        self.gameDisplay.blit(self.background,(0,0))
        self.messageToScreen("Your mission is going well!", 40, white, display_width / 2, display_height / 2-200, black)
        self.messageToScreen("You have " + str(self.score) + " points!", 40, white, display_width / 2, display_height / 2 - 100, black)
        self.gameDisplay.blit(self.bigAvatar, (display_width/2 - 200, display_height/2))
        self.gameDisplay.blit(self.coinPile, (display_width/2, display_height/2 + 20))
        pygame.display.update()
        pygame.time.wait(2000)
        self.levelUps = self.levelUps + 1

    # Helper function for printing a message to the game screen
    def messageToScreen(self,msg,size, color, x, y, rect_color):
        font=pygame.font.Font(self.font_name,size)
        text_surface=font.render(msg,True,color)
        text_rect=text_surface.get_rect()
        text_rect.midtop=(x,y)
        pygame.draw.rect(self.gameDisplay, rect_color, (text_rect.left - 20, text_rect.top - 20, text_rect.width + 40, text_rect.height + 40))
        self.gameDisplay.blit(text_surface,text_rect)

    # Initiall screen participant see in demo
    def startScreen(self):
        self.getParticipantID()
        slideImage= pygame.transform.scale(self.introSlideImages[0], (display_width, display_height))
        self.gameDisplay.blit(slideImage,(0,0))
        pygame.display.update()
        self.ray.play()
        self.rocket.play()
        self.waitForSpace()
        self.chooseAvatar()
        self.gameDisplay.fill(black)
        pygame.display.update()
        self.showIntroSlides()
        self.gameDisplay.blit(self.background,(0,0))
        self.messageToScreen("This is a VERY important mission!", 35, white, display_width / 2, display_height / 2, red)
        self.messageToScreen("To prepare you, we have a short demo", 35, white, display_width / 2, display_height / 2 + 50, red)
        self.messageToScreen("Ready for the demo?", 35, white, display_width / 2, display_height / 2 + 100, red)
        pygame.display.update()
        self.waitForSpace()
        g.run()

    # Check for low FPS to ensure smooth gameplay
    def lowFPS(self, frames):
        self.gameDisplay.fill(orange)
        self.messageToScreen(("WARNING!!, low refresh rate of only " + str(frames) + " frames/second"),25,white,display_width/2,display_height/2, black)
        self.messageToScreen(('Game may perform at a different speed'),20,white,display_width/2,display_height/1.5, black)
        pygame.display.update()
        pygame.time.wait(5000)

    # Show demo slides
    def showIntroSlides(self):
        for i in range(1,2):
            self.rocket.play()
            slideImage= pygame.transform.scale(self.introSlideImages[i], (display_width, display_height))
            self.gameDisplay.blit(slideImage,(0,0))
            self.waitForSpace()
            pygame.display.update()
        self.waitForSpace()
        pygame.display.update()

    # Get participand ID before starting game
    def getParticipantID(self):
        textinput = TextInput(self)
        while True:
            self.gameDisplay.fill((225, 225, 225))

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            # Feed it with events every frame
            textReturn = textinput.update(events)

            # Blit its surface onto the screen
            self.gameDisplay.blit(textinput.get_surface(), (10, 10))


            pygame.display.update()
            if textReturn:
                self.participantID = textinput.get_text().replace(" ", "")
                break

    # At the end of the game, get the participant's self-reported strategy (experimenter types)
    def getStrategyResponse(self):
        self.strategy = ''
        textinput = StrategyTextInput(self)
        while True:
            self.gameDisplay.fill((225, 225, 225))

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            # Feed it with events every frame
            textReturn = textinput.update(events)


            # Blit multiple surfaces onto the screen
            surfaces = textinput.get_surface()
            for surfIndex, surface in enumerate(surfaces):
                self.gameDisplay.blit(surface, (10, 20*surfIndex))

            pygame.display.update()
            if textReturn:
                self.strategy= textinput.get_text()
                self.taskDataFrame['strategyResponse'] = self.strategy
                break

    # Halfway through the task, participant gets a break
    def takeABreak(self):
        self.powerup.play()
        self.gameDisplay.blit(self.background,(0,0))
        self.messageToScreen(("Great job with your mission!"),35,white,display_width/2,display_height/2, black)
        self.messageToScreen(("You're halfway there!"),35,white,display_width/2,display_height/2 + 50, black)
        self.messageToScreen(("(space)"),20,white,display_width/2, 550, black)
        pygame.display.update()
        waiting=True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    waiting=False
                    self.gameExit=True
                if event.type==pygame.KEYUP:
                    if event.key==pygame.K_SPACE:
                        waiting=False
                    self.gameOver=False
                    self.gameExit=False

    # Print reminder to participant to choose faster
    def speedReminder(self):
        self.messageToScreen(("Please choose faster!"),50,white,display_width/2,self.pos.y - 300, red)
        pygame.display.update()
        self.error_sound.play()

    # Runs post-questions after finishing all 200 trials
    # Questions ask for explicit recognition of task structure
    def postQuestions(self):
        leftPortalColor = 0
        rightPortalColor = 1
        if not self.gameExit:
            self.rocket.play()
            self.congratsScreen()
            for i in range(0,len(self.postQuestionImages)):
                if i == 5:
                    self.getStrategyResponse()
                self.rocket.play()
                slideImage= pygame.transform.scale(self.postQuestionImages[i], (display_width, display_height))
                self.gameDisplay.blit(slideImage,(0,0))
                pygame.display.update()
                if i < 5:
                    if (i == 2) or (i == 3):
                        self.portalLeft = Portal(self)
                        self.portalLeft.getPortal(display_width/2 - 200, display_height - 100, self.portals_images, leftPortalColor)
                        self.portalRight = Portal(self)
                        self.portalRight.getPortal(display_width/2 + 75, display_height - 100, self.portals_images, rightPortalColor)
                        self.portals.add(self.portalLeft)
                        self.portals.add(self.portalRight)
                        self.portals.draw(self.gameDisplay)
                        pygame.display.update()
                    self.getPostQuestionResponse()
                    if i == 0:
                        self.taskDataFrame['yellowPortalDestResp'] = self.keyname
                    elif i == 1:
                        self.taskDataFrame['greenPortalDestResp'] = self.keyname
                    elif i == 2:
                        self.taskDataFrame['stage2Type1PortalResp'] = self.keyname
                    elif i == 3:
                        self.taskDataFrame['stage2Type2PortalResp'] = self.keyname
                    elif i == 4:
                        # LEFT is correct for this (mosf of the time, vertical ladder, not horizontal)
                        self.taskDataFrame['ladderResponse'] = self.keyname
                else:
                    self.waitForKeyPress()
            if self.taskDataFrame.loc[1, 'color0'] == 'images/yellowPortal.png':
                self.taskDataFrame['yellowPortalDest'] = 'l'
                self.taskDataFrame['greenPortalDest'] = 'r'
            elif self.taskDataFrame.loc[1, 'color1'] == 'images/yellowPortal.png':
                self.taskDataFrame['yellowPortalDest'] = 'r'
                self.taskDataFrame['greenPortalDest'] = 'l'
            self.waitForSpace()

    # Get responses to post questions
    def getPostQuestionResponse(self):
        waiting=True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    waiting=False
                    self.gameExit=True
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_LEFT:
                        self.keyname = 'l'
                        waiting=False
                        self.gameOver=False
                        self.gameExit=False
                    elif event.key == pygame.K_RIGHT:
                        self.keyname = 'r'
                        waiting=False
                        self.gameOver=False
                        self.gameExit=False


    # Congratulate participant for finishing game!
    def congratsScreen(self):
        self.powerup.play()
        self.gameDisplay.blit(self.background,(0,0))
        self.gameDisplay.blit(self.bigAvatar, (display_width/2 - 200, display_height/2))
        self.gameDisplay.blit(self.coinPile, (display_width/2, display_height/2 + 20))
        self.messageToScreen(("Congrats! Mission successfull!"),40,white,display_width/2,display_height/2 - 100, black)
        pygame.display.update()
        pygame.time.wait(3000)
        self.waitForKeyPress()
        pygame.display.update()

    # Let participant choose game avatar at the beginning of the task
    def chooseAvatar(self):
        self.ray.play()
        self.avatar = 'undeclared'
        self.gameDisplay.blit(self.avatarChoiceScreen,(0,0))
        pygame.display.update()
        waiting=True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    waiting=False
                    self.gameExit=True
                if event.type==pygame.KEYUP:
                    if event.key==pygame.K_1:
                        self.avatar = 'pikachu'
                    elif event.key ==  pygame.K_2:
                        self.avatar = 'blackPanther'
                    elif event.key == pygame.K_3:
                        self.avatar = 'spiderMan'
                    elif event.key == pygame.K_4:
                        self.avatar = 'chloe'
                    if self.avatar != 'undeclared':
                        waiting=False
                        self.gameOver=False
                        self.gameExit=False
        self.powerup.play()

    # Five trials in, give reminder of rules
    def ruleReminder(self):
        self.ray.play()
        reminderImage= pygame.transform.scale(self.reminderImages[0], (display_width, display_height))
        self.gameDisplay.blit(reminderImage,(0,0))
        leftPortalColor = 0
        rightPortalColor = 1
        self.portalLeft = Portal(self)
        self.portalLeft.getPortal(display_width/2 - 200, display_height - 100, self.portals_images, leftPortalColor)
        self.portalRight = Portal(self)
        self.portalRight.getPortal(display_width/2 + 75, display_height - 100, self.portals_images, rightPortalColor)
        self.portals.add(self.portalLeft)
        self.portals.add(self.portalRight)
        self.portals.draw(self.gameDisplay)
        self.messageToScreen(("(space)"),20,white,display_width/2, 550, black)
        pygame.display.update()
        self.waitForSpace()
        reminderImage= pygame.transform.scale(self.reminderImages[1], (display_width, display_height))
        self.gameDisplay.blit(reminderImage,(0,0))
        self.portalLeft = Portal(self)
        self.portalLeft.getPortal(display_width/2 - 200, display_height - 100, self.portals_images, leftPortalColor)
        self.portalRight = Portal(self)
        self.portalRight.getPortal(display_width/2 + 75, display_height - 100, self.portals_images, rightPortalColor)
        self.portals.add(self.portalLeft)
        self.portals.add(self.portalRight)
        self.portals.draw(self.gameDisplay)
        self.messageToScreen(("(space)"),20,white,display_width/2, 550, black)
        pygame.display.update()
        self.waitForSpace()
        self.portals.empty()

    # 2 practice trials before the task
    def practiceTrials(self, practiceTrial):
        self.rocket.play()
        self.ladderImage = self.coinPile
        self.pos = vec(display_width/2 - 15, display_height)
        self.greenScore = False
        self.redScore = False
        self.img_avatar.image = pygame.transform.scale(self.img_avatar.image, (70,70))

        # Left portal for practice is color2, right portal is color3
        leftPortalColor = 2
        rightPortalColor = 3

        # Draw Portals
        self.portalLeft = Portal(self)
        self.portalLeft.getPortal(display_width/2 - 200, self.pos.y - 120 , self.portals_images, 2)
        self.portalRight = Portal(self)
        self.portalRight.getPortal(display_width/2 + 75, self.pos.y - 120 , self.portals_images, 3)
        self.portals.add(self.portalLeft)
        self.portals.add(self.portalRight)
        self.portals.update()
        self.platforms.draw(self.gameDisplay)
        self.updateScreen(self.background)
        self.messageToScreen(("Use the arrow keys to choose a portal!"),30,white,display_width/2, 400, red)
        self.messageToScreen(("Each color portal usually goes to the same planet"),30,white,display_width/2,450, red)
        self.messageToScreen(("(space)"),20,white,display_width/2, 550, black)
        pygame.display.update()
        self.waitForSpace()
        self.updateScreen(self.background)
        self.getAction1(1, practice = True)


        self.ladderPos = self.keyname
        beginLoop = pygame.time.get_ticks()
        loopTime = 0
        if self.keyname == 'l':
            self.vel.x = -35
            self.vel.y = 0
            portalColor = leftPortalColor
        else:
            self.vel.x = 35
            self.vel.y = 0
            portalColor = rightPortalColor


        if portalColor == 2:
            stage2Type = 1
        else:
            stage2Type = 2

        self.portal2Sound.play()
        for i in range(1,5):
            self.clock.tick_busy_loop(self.maxFPS)
            self.pos+=self.vel
            self.updateScreen(self.background)
        if self.ladderPos == 'l':
            self.portals.remove(self.portalRight)
        else:
            self.portals.remove(self.portalLeft)
        upperPortal = Portal(self)
        pygame.time.wait(100)
        if stage2Type == 2:
            if self.ladderPos == 'r':
                self.ladderImage = self.ladderStraight
                self.vel.y = -90
                self.vel.x = 0
            else:
                self.ladderImage = self.ladderRight
                self.vel.y = -90
                self.vel.x = 70
            for i in range(1, 5):
                self.clock.tick_busy_loop(self.maxFPS)
                self.pos+=self.vel
                self.updateScreen(self.background)
            upperPortal.getPortal(display_width/2 + 75, display_height/2 - 100, self.portals_images, portalColor)
        else:
            if self.ladderPos == 'l':
                self.ladderImage = self.ladderStraight
                self.vel.y = -90
                self.vel.x = 0
            else:
                self.ladderImage = self.ladderLeft
                self.vel.y = -90
                self.vel.x = -70
            for i in range(1, 5):
                self.clock.tick_busy_loop(self.maxFPS)
                self.pos+=self.vel
                self.updateScreen(self.background)
            upperPortal.getPortal(display_width/2 - 200, display_height/2 - 100, self.portals_images, portalColor)
        self.vel.y = 0
        self.vel.x = 0
        self.portals.add(upperPortal)
        self.portals.update()
        self.portals.draw(self.gameDisplay)
        self.updateScreen(self.background)
        self.rocket.play()
        self.messageToScreen(("Next, you choose an alien!"),35,white,display_width/2, 400, red)
        self.messageToScreen(("The aliens will try to find you a coin!"),35,white,display_width/2,450, red)
        self.messageToScreen(("(space)"),20,white,display_width/2, 550, black)
        pygame.display.update()
        self.waitForSpace()
        self.updateScreen(self.background)
        self.getAction1(1, practice = True)

        # Movement of avatar to alien
        if self.keyname == 'l':
            self.vel.y = -30
            self.vel.x = -10
        elif self.keyname == 'r':
            self.vel.y = -30
            self.vel.x = 10
        for i in range(1, 5):
            self.clock.tick_busy_loop(self.maxFPS)
            self.pos+=self.vel
            self.updateScreen(self.background)

        if stage2Type == 1:
            if self.keyname == 'l':
                alien2Move = self.alienSprites[0]
            else:
                alien2Move = self.alienSprites[1]
        else:
            if self.keyname == 'l':
                alien2Move = self.alienSprites[2]
            else:
                alien2Move = self.alienSprites[3]

        if practiceTrial == 1:
            self.whee.play()
            for i in range(1,9):
                self.clock.tick_busy_loop(self.maxFPS)
                alien2Move.rect.y -= 10*np.sin(i*1.5)
                self.updateScreen(self.background)
            alien2Move.rect.y = 100
            self.coin_sound.play()
            coinReward = Coin(self)
            coinReward.getCoin(alien2Move.rect.x + 10, alien2Move.rect.y - 25, self.coins_images, 0)
            self.coins.add(coinReward)
            self.coins.update()
            self.coins.draw(self.gameDisplay)
            self.messageToScreen(("This alien found you a coin!"),35,white,display_width/2, 400, red)
            self.messageToScreen(("(space)"),20,white,display_width/2, 600, black)
            pygame.display.update()
        else:
            prevX = alien2Move.rect.x
            self.lossSound.play()
            for i in range(1,9):
                alien2Move.rect.x
                self.clock.tick_busy_loop(self.maxFPS)
                alien2Move.rect.x -= 10*np.sin(i*1.5)
                self.updateScreen(self.background)
            alien2Move.rect.x = prevX
            self.messageToScreen(("This alien didn't find a coin"),30,white,display_width/2, 400, red)
            self.messageToScreen(("(space)"),20,white,display_width/2, 600, black)
            pygame.display.update()
            self.waitForSpace()
            self.messageToScreen(("Try to pay attention!"),30,white,display_width/2, 450, red)
            self.messageToScreen(("The best alien will change over time"),30,white,display_width/2, 500, red)
            self.messageToScreen(("(space)"),20,white,display_width/2, 600, black)
            pygame.display.update()
        self.waitForSpace()
        self.coins.empty()
        self.portals.empty()

    # Helper function to wait for a key press (any key)
    def waitForKeyPress(self):
        waiting=True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    waiting=False
                    self.gameExit=True
                if event.type==pygame.KEYUP:
                    waiting=False
                    self.gameOver=False
                    self.gameExit=False

    # Helper function to wait until spacebar is pressed
    def waitForSpace(self):
        waiting=True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    waiting=False
                    self.gameExit=True
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_SPACE:
                        waiting=False
                        self.gameOver=False
                        self.gameExit=False
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT and mods & pygame.KMOD_ALT:
                        waiting=False
                        self.gameExit=True

# Create an instance of game, and start!
g=Game()
g.startScreen()
