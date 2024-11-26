import os
import random
import sys
import pygame as pg
import time

WIDTH, HEIGHT = 1100, 650
# こうかとんの移動量を定義する辞書
DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0, +5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (+5, 0)
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外かを判断する
    引数：こうかとRect or 爆弾Rect
    戻り数：真理値タプル（横,縦）/画面内：Ture,画面外：False
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する
    - 画面を半透明の黒で覆い、「Game Over」を表示する
    - 泣いているこうかとん画像を画面中央に貼り付ける
    - 5秒間表示してゲームを終了する
    """
    # 半透明の黒い矩形を描画
    rect_surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)  # 透明度をサポートするSurface
    pg.draw.rect(rect_surface, (0, 0, 0, 128), (0, 0, WIDTH, HEIGHT))  # 半透明の黒い矩形
    screen.blit(rect_surface, (0, 0))  # 画面に描画

    # 泣いているこうかとん画像をロードして描画
    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    cry_rct_left = cry_img.get_rect()
    cry_rct_left.center = (WIDTH // 3 - 50, HEIGHT // 2)
    cry_rct_right = cry_img.get_rect()
    cry_rct_right.center = (2 * WIDTH // 3 + 50, HEIGHT // 2)

    screen.blit(cry_img, cry_rct_left)
    screen.blit(cry_img, cry_rct_right)
    # 「Game Over」の文字列を描画
    font = pg.font.Font(None, 100)  # フォントサイズ100
    text = font.render("Game Over", True, (255, 255, 255))  # 赤色の文字
    text_rct = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rct)

    # 画面を更新して5秒間停止
    pg.display.update()
    time.sleep(5)

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20)) # 爆弾用の空Surface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) # 爆弾円を描く
    bb_img.set_colorkey((0, 0, 0)) # 四隅の黒を透過させる
    bb_rct = bb_img.get_rect()# 爆弾Rectの抽出
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5 # 爆弾速度ベクトル

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        if kk_rct.colliderect(bb_rct):
            gameover(screen)  # ゲームオーバー画面を表示
            return  # ゲーム終了
        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]
        kk_rct.move_ip(sum_mv)
 # 画面外に出た場合、元の位置に戻す
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
 # 爆弾の移動
        bb_rct.move_ip(vx, vy)

        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横にはみ出てる
            vx *= -1
        if not tate:  # 縦にはみ出てる
            vy *= -1
# こうかとんと爆弾の衝突判定       

        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
