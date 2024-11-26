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
    rect_surface = pg.Surface((WIDTH, HEIGHT))  # 透明度をサポートするSurface
    rect_surface.set_alpha(200)
    rect_surface.fill((0, 0, 0))  # 半透明の黒い矩形
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
    text = font.render("Game Over", True, (255, 255, 255)) 
    text_rct = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rct)

    # 画面を更新して5秒間停止
    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    ゲームオーバー画面を表示するサイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す
    """
    bb_imgs = []
    accs = [a for a in range(1, 11)]  # 加速度リスト
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))  # 可変サイズの爆弾Surface
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)  # 円を描く
        bb_img.set_colorkey((0, 0, 0))  # 黒を透過色に設定
        bb_imgs.append(bb_img)  # リストに追加
    return bb_imgs, accs


def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    移動量の合計値タプルに対応する向きの画像Surfaceを返す
    引数：
        sum_mv: 移動量の合計を表すタプル（x方向, y方向）
    戻り値：
        pg.Surface: 合計移動量に対応する向きの画像Surface
    """
    # rotozoomしたSurfaceを値とした辞書を準備
    kk_images = {
        (0, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9),    # 上
        (0, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 180, 0.9),  # 下
        (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 0.9),   # 左
        (+5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 0.9),  # 右
        (-5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 0.9),  # 左上
        (-5, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 135, 0.9), # 左下
        (+5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 0.9), # 右上
        (+5, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -135, 0.9),# 右下
        (0, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)      # 静止
    }
    return kk_images.get(sum_mv, kk_images[(0, 0)])  # 未知のタプルは静止状態


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 爆弾リストと加速度リストを初期化
    bb_imgs, bb_accs = init_bb_imgs()
    bb_rct = bb_imgs[0].get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    
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

        # 時間に応じて爆弾のサイズと加速度を変更
        bb_img = bb_imgs[min(tmr // 500, 9)]  # 爆弾サイズ
        avx = vx * bb_accs[min(tmr // 500, 9)]  # 加速度適用
        avy = vy * bb_accs[min(tmr // 500, 9)]

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
# こうかとんの向きを更新
        kk_img = get_kk_img(tuple(sum_mv))
 # 爆弾の移動
        bb_rct.move_ip(avx, avy)

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
