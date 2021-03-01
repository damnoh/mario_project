import pygame
import os
import random
from pygame import *

pygame.init()
# создание экрана
screen_size = (width, height) = (600, 150)
FPS = 60
gravity = 0.6
black = (0, 0, 0)
white = (255, 255, 255)
back_color = (235, 235, 235)
high_score = 0
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
pygame.display.set_caption("Mario, run! run! ")
# загрузка звуков
jump_sound = pygame.mixer.Sound('components/jump.wav')
die_sound = pygame.mixer.Sound('components/die.wav')
checkpoint_sound = pygame.mixer.Sound('components/checkpoint.wav')
# загрузка фото


def load_img(name, sizex=-1, sizey=-1, colorkey=None):
    fullname = os.path.join('components', name)
    img = pygame.image.load(fullname)
    img = img.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        img = pygame.transform.scale(img, (sizex, sizey))

    return img, img.get_rect()


# загрузка рабочей области
def load_sheet(page, nx, ny, scalex=-1, scaley=-1, colorkey=None):
    fullname = os.path.join('components', page)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()
    sheet_rect = sheet.get_rect()
    components = []
    size_x = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0, ny):
        for j in range(0, nx):
            rect = pygame.Rect((j*size_x, i*sizey, size_x, sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet, (0, 0), rect)

            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image, (scalex, scaley))

            components.append(image)

    sprite_rect = components[0].get_rect()

    return components, sprite_rect


# сообщение о проигрыше
def message(restart_image, gg_image):
    restart_rect = restart_image.get_rect()
    restart_rect.centerx = width / 2
    restart_rect.top = height * 0.52

    gg_rect = gg_image.get_rect()
    gg_rect.centerx = width / 2
    gg_rect.centery = height * 0.35

    screen.blit(restart_image, restart_rect)
    screen.blit(gg_image, gg_rect)


# получение числовых данных о результате
def digits(number):
    if number > -1:
        digits_lst = []
        while number / 10 != 0:
            digits_lst.append(number % 10)
            number = int(number / 10)

        digits_lst.append(number % 10)
        for i in range(len(digits_lst), 5):
            digits_lst.append(0)
        digits_lst.reverse()
        return digits_lst


# реализация игры за Марио, звуки
class Mario:
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = load_sheet('mario.png', 5, 1, sizex, sizey, -1)
        self.images1, self.rect1 = load_sheet('duckmario.png', 2, 1, 59, sizey, -1)
        self.rect.bottom = int(0.98 * height)
        self.rect.left = width / 15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.mo_ve = [0, 0]
        self.jumpSpeed = 11.5

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self):
        screen.blit(self.image, self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.98 * height):
            self.rect.bottom = int(0.98 * height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.mo_ve[1] = self.mo_ve[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1) % 2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1) % 2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2 + 2

        if self.isDead:
            self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[self.index % 2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.mo_ve)
        self.checkbounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking is False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() is not None:
                    checkpoint_sound.play()

        self.counter = (self.counter + 1)


# реализация препятствия(кактуса)
class Cactus(pygame.sprite.Sprite):
    def __init__(self, speed=5, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sheet('cactus1.png', 3, 1, sizex, sizey, -1)
        self.rect.bottom = int(0.98 * height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0, 3)]
        self.mo_ve = [-1 * speed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.mo_ve)

        if self.rect.right < 0:
            self.kill()


# реализация препятствия(гриба)
class Mushroom(pygame.sprite.Sprite):
    def __init__(self, speed=5, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sheet('mushroom.png', 2, 1, sizex, sizey, -1)
        self.mushroom_height = [height * 0.82, height * 0.75, height * 0.60]
        self.rect.centery = self.mushroom_height[random.randrange(0, 3)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.mo_ve = [-1 * speed, 0]
        self.index = 0
        self.counter = 0

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index + 1) % 2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.mo_ve)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


# реализация пола
class Floor:
    def __init__(self, speed=-5):
        self.image, self.rect = load_img('floor.png', -1, -1, -1)
        self.image1, self.rect1 = load_img('floor.png', -1, -1, -1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


# реализация неба
class Sky(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_img('sky.png', int(90*30/42), 30, -1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.mo_ve = [-1 * self.speed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.mo_ve)
        if self.rect.right < 0:
            self.kill()


# реализация показателей результата
class Scoreboard:
    def __init__(self, x=-1, y=-1):
        self.score = 0
        self.tempimages, self.temprect = load_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
        self.image = pygame.Surface((55, int(11 * 6 / 5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width * 0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height * 0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self, score):
        score_digits = digits(score)
        self.image.fill(back_color)
        for i in score_digits:
            self.image.blit(self.tempimages[i], self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0


# загрузочный экран
def introscreen():
    mario_temp = Mario(44, 47)
    mario_temp.isBlinking = True
    gameStart = False

    temp_floor, temp_floor_rect = load_sheet('floor.png', 15, 1, -1, -1, -1)
    temp_floor_rect.left = width / 20
    temp_floor_rect.bottom = height

    logo, logo_rect = load_img('logo.png', 300, 140, -1)
    logo_rect.centerx = width * 0.6
    logo_rect.centery = height * 0.6
    while not gameStart:
        if pygame.display.get_surface() is None:
            print("OOps...")
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        mario_temp.isJumping = True
                        mario_temp.isBlinking = False
                        mario_temp.mo_ve[1] = -1 * mario_temp.jumpSpeed

        mario_temp.update()

        if pygame.display.get_surface() is not None:
            screen.fill(back_color)
            screen.blit(temp_floor[0], temp_floor_rect)
            if mario_temp.isBlinking:
                screen.blit(logo, logo_rect)
            mario_temp.draw()

            pygame.display.update()

        clock.tick(FPS)
        if mario_temp.isJumping is False and mario_temp.isBlinking is False:
            gameStart = True


# процесс игры
def gameplay():
    global high_score
    gamespeed = 4
    startMenu = False
    gg = False
    gameQuit = False
    playerMario = Mario(44, 47)
    new_floor = Floor(-1 * gamespeed)
    scb = Scoreboard()
    highsc = Scoreboard(width * 0.78)
    counter = 0

    cactus = pygame.sprite.Group()
    mushrooms = pygame.sprite.Group()
    skys = pygame.sprite.Group()
    last_obstacle = pygame.sprite.Group()

    Cactus.containers = cactus
    Mushroom.containers = mushrooms
    Sky.containers = skys

    restart_image, restart_rect = load_img('restart.png', 35, 31, -1)
    gg_image, gg_rect = load_img('gg.png', 190, 11, -1)

    temp_images, temp_rect = load_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
    HI_image = pygame.Surface((22, int(11 * 6 / 5)))
    HI_rect = HI_image.get_rect()
    HI_image.fill(back_color)
    HI_image.blit(temp_images[10], temp_rect)
    temp_rect.left += temp_rect.width
    HI_image.blit(temp_images[11], temp_rect)
    HI_rect.top = height*0.1
    HI_rect.left = width*0.73

    while not gameQuit:
        while startMenu:
            pass
        while not gg:
            if pygame.display.get_surface() is None:
                print("OOps...")
                gameQuit = True
                gg = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gg = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if playerMario.rect.bottom == int(0.98 * height):
                                playerMario.isJumping = True
                                if pygame.mixer.get_init() is not None:
                                    jump_sound.play()
                                playerMario.mo_ve[1] = -1 * playerMario.jumpSpeed

                        if event.key == pygame.K_DOWN:
                            if not (playerMario.isJumping and playerMario.isDead):
                                playerMario.isDucking = True

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN:
                            playerMario.isDucking = False
            for i in cactus:
                i.mo_ve[0] = -1 * gamespeed
                if pygame.sprite.collide_mask(playerMario, i):
                    playerMario.isDead = True
                    if pygame.mixer.get_init() is not None:
                        die_sound.play()

            for i in mushrooms:
                i.mo_ve[0] = -1 * gamespeed
                if pygame.sprite.collide_mask(playerMario, i):
                    playerMario.isDead = True
                    if pygame.mixer.get_init() is not None:
                        die_sound.play()

            if len(cactus) < 2:
                if len(cactus) == 0:
                    last_obstacle.empty()
                    last_obstacle.add(Cactus(gamespeed, 40, 40))
                else:
                    for i in last_obstacle:
                        if i.rect.right < width * 0.7 and random.randrange(0, 50) == 10:
                            last_obstacle.empty()
                            last_obstacle.add(Cactus(gamespeed, 40, 40))

            if len(mushrooms) == 0 and random.randrange(0, 200) == 10 and counter > 500:
                for i in last_obstacle:
                    if i.rect.right < width*0.8:
                        last_obstacle.empty()
                        last_obstacle.add(Mushroom(gamespeed, 46, 40))

            if len(skys) < 5 and random.randrange(0, 300) == 10:
                Sky(width, random.randrange(height / 5, height/2))

            playerMario.update()
            cactus.update()
            mushrooms.update()
            skys.update()
            new_floor.update()
            scb.update(playerMario.score)
            highsc.update(high_score)

            if pygame.display.get_surface() is not None:
                screen.fill(back_color)
                new_floor.draw()
                skys.draw(screen)
                scb.draw()
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image, HI_rect)
                cactus.draw(screen)
                mushrooms.draw(screen)
                playerMario.draw()

                pygame.display.update()
            clock.tick(FPS)

            if playerMario.isDead:
                gg = True
                if playerMario.score > high_score:
                    high_score = playerMario.score

            if counter % 700 == 699:
                new_floor.speed -= 1
                gamespeed += 1

            counter = (counter + 1)

        if gameQuit:
            break

        while gg:
            if pygame.display.get_surface() is None:
                print("OOps...")
                gameQuit = True
                gg = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gg = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            gameQuit = True
                            gg = False

                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            gg = False
                            gameplay()
            highsc.update(high_score)
            if pygame.display.get_surface() != None:
                message(restart_image, gg_image)
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image, HI_rect)
                pygame.display.update()
            clock.tick(FPS)

    pygame.quit()
    quit()

def main():
    isGameQuit = introscreen()
    if not isGameQuit:
        gameplay()

main()