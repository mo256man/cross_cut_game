import pygame
import pygame.gfxdraw
from pygame.locals import *
import random
import numpy as np
import sys
import math
import cv2

pygame.init()
WIDTH, HEIGHT = 1024, 768
is_fullscreen = False
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
clock = pygame.time.Clock()
myfont = r".\font\tamanegi.ttf"     # 玉ねぎ楷書激無料版v6

class Sprite(pygame.sprite.Sprite):
    def __init__(self, name, image, xy, vxy, angle=0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.name = name
        if isinstance(image, str):
            self.image = pygame.image.load(image).convert_alpha()
        else:
            self.image = image
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.xy = xy
        self.vxy = vxy
        self.angle = angle
        self.t = 0

        # OpenCV画像（numpy配列）にして面積を求める
        alpha = pygame.surfarray.array_alpha(self.image)
        self.area = np.sum(alpha)   # 正確には面積ではないけど
    
    def update(self):
        self.t += 1
        x, y = self.xy
        vx, vy = self.vxy
        if "gaya" in self.name:
            v = 100 *(abs(math.sin(self.t/20)) - abs(math.sin((self.t-1)/20)))
            x += vx*v
            y += vy*v
        else:
            x += vx
            y += vy
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.xy = (x, y)

    def add_text(self, total_area):
        font = pygame.font.Font(None, 100)
        self.msg = f"{round(self.area/total_area*100)}%"
        self.text = font.render(self.msg, True, (0,0,0))
        x, y = self.xy          # 画像の中心座標
        vx, vy = self.vxy       # 進行方向（±1, ±1）　ここではオフセット方向として使う
        w, h = self.image.get_size()
        tx, ty = x+vx*w*0.25, y+vy*h*0.25
        self.text_rect = self.text.get_rect(center=(tx,ty))
        self.vxy = (0,0)        # これ以上は動かない


class Stage():
    def __init__(self, s):
        if s==1:
            self.backimage = r"./image/table.png"
            self.circle = r"./image/cake.png"
            self.gaya1 = r"./image/child1.png"
            self.gaya2 = r"./image/child2.png"
            self.gaya3 = r"./image/child3.png"
            self.gaya4 = r"./image/child4.png"
            self.text1 = "皆で仲良く"
            self.text2 = "ケーキカット"
            self.fontcolor = (0,0,0)
        if s==2:
            self.backimage = r"./image/space.png"
            self.circle = r"./image/earth.png"
            self.gaya1 = r"./image/god1.png"
            self.gaya2 = r"./image/god2.png"
            self.gaya3 = r"./image/god3.png"
            self.gaya4 = r"./image/god4.png"
            self.text1 = "神々の戯れ"
            self.text2 = "地球分割計画"
            self.fontcolor = (255,0,0)

def divide_surface(sprite):
    # 図形を分割する と同時に面積を求める（元図形の面積ではなく分割後の各面積の計）
    x, y = sprite.xy
    w, h = sprite.image.get_size()
    angle1 = random.random()*30-15
    angle2 = random.random()*30-15

    # 切断ポイント
    x1, y1 = w//2, 0        # 上（左右中央で固定）
    x2, y2 = 0, h//2        # 左（上下中央で固定）
    x3, y3 = int((1-2*math.tan(math.radians(angle1)))*w/2), h   # 下
    x4, y4 = w, int((1-2*math.tan(math.radians(angle2)))*h/2)   # 右

    # 左上方向のベクトル
    vx1, vy1 = x1+x2-x3-x4, y1+y2-y3-y4
    v1 = math.sqrt(vx1**2 + vy1**2)
    vx1, vy1 = vx1/v1, vy1/v1

    # 右上方向のベクトル
    vx2, vy2 = x1-x2-x3+x4, y1-y2-y3+y4
    v2 = math.sqrt(vx2**2 + vy2**2)
    vx2, vy2 = vx2/v2, vy2/v2

    # 捨てる四角形
    cutU = [(0,0), (x2,y2), (x4,y4), (w,0)]     # 上
    cutD = [(x2,y2), (0,h), (w,h), (x4,y4)]     # 下
    cutL = [(0,0), (0,h), (x3,y3), (x1,y1)]     # 左
    cutR = [(x1,y1), (x3,y3), (w,h), (w,0)]     # 右

    # カットする
    img = sprite.image
    partRD = Sprite("partLD", cut_surface(img.copy(), [cutL, cutU]), (x,y), (1,1))
    partLD = Sprite("partRD", cut_surface(img.copy(), [cutR, cutU]), (x,y), (-1,1))
    partRU = Sprite("partRU", cut_surface(img.copy(), [cutL, cutD]), (x,y), (1,-1))
    partLU = Sprite("partLU", cut_surface(img.copy(), [cutR, cutD]), (x,y), (-1,-1))

    return partRD.area + partLD.area + partRU.area + partLU.area

def cut_surface(surface, cuts):
    for pts in cuts:
        pygame.gfxdraw.filled_polygon(surface, pts, (0,0,0,0))
    return surface


def wait_for_space():
    global is_fullscreen
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                return True
            elif event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == K_F2:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN, 32)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    return False

def title_demo():
    bg = pygame.image.load(r".\image\title.png")
    bg_rect = bg.get_rect()
    screen.blit(bg, bg_rect)
    pygame.display.update()
    while True:
        screen.fill((120,20,220))
        ans = wait_for_space()
        if ans:
            break
    print("game start")


def stage_demo(stage):
    bg = pygame.image.load(stage.backimage)
    bg_rect = bg.get_rect()
    screen.blit(bg, bg_rect)
    font1 = pygame.font.Font(myfont, 80)
    text1 = font1.render(stage.text1, True, stage.fontcolor)
    rect1 = text1.get_rect(center=(WIDTH//2, HEIGHT//2-100))
    screen.blit(text1, rect1)
    font2 = pygame.font.Font(myfont, 120)
    text2 = font2.render(stage.text2, True, stage.fontcolor)
    rect2 = text2.get_rect(center=(WIDTH//2, HEIGHT//2+20))
    screen.blit(text2, rect2)
    pygame.display.update()
    while True:
        ans = wait_for_space()
        if ans:
            break
    print("stage start")


def add_gaya(stage):
    gaya1 = Sprite("gaya1", stage.gaya1, (0,0), (1,1), -135)
    gaya2 = Sprite("gaya2", stage.gaya2, (WIDTH,0), (-1,1), 135)
    gaya3 = Sprite("gaya3", stage.gaya3, (0,HEIGHT), (1,-1), -45)
    gaya4 = Sprite("gaya4", stage.gaya4, (WIDTH,HEIGHT), (-1,-1), 45)

def main():
    global myfont
    group = pygame.sprite.RenderUpdates()
    Sprite.containers = group    

    title_demo()

    cnt = 0
    stage = Stage(1)
    bg = pygame.image.load(stage.backimage)
    bg_rect = bg.get_rect()
    circle = Sprite("circle", stage.circle, (WIDTH//2,HEIGHT//2), (0,0), 0)
    stage_demo(stage)

    is_break = False
    while True:
        clock.tick(60)
        screen.fill((0,0,0))
        screen.blit(bg, bg_rect)
        group.update()
        group.draw(screen)
        
        if cnt == 0:
            ans = wait_for_space()
            if ans:
                circle.kill()
                total_area = divide_surface(circle)
                cnt += 1

        # 拡散
        elif 0 < cnt < 100:
            cnt += 1

        # 停止
        elif cnt == 100:
            cnt += 1
            for sprite in group.spritedict:
                sprite.add_text(total_area)
            add_gaya(stage)

        elif cnt > 100:
            ans = wait_for_space()
            if ans:
                is_break = True
            group.update()
            group.draw(screen)
            for sprite in group.spritedict:
                if hasattr(sprite, "msg"):
                    font = pygame.font.Font(myfont, 100)
                    sprite.text = font.render(sprite.msg, True, stage.fontcolor)
                    screen.blit(sprite.text, sprite.text_rect)

        pygame.display.update()
        if is_break:
            break    
    print("end")

if __name__ == "__main__":
    main()
