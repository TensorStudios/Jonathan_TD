import pygame as pg
from settings import *
from itertools import chain


vec = pg.math.Vector2


class Tower(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.towers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.pos = vec(self.rect.center)
        self.damage = TOWER_DAMAGE
        self.attack_radius = TOWER_ATTACK_RADIUS
        self.target = None
        self.last_shot = pg.time.get_ticks()
        self.shooting = False
        self.damage_alpha = None

    def acquire_target(self):
        mobs_in_range = []
        closest_mob = None
        for mob in self.game.mobs:
            dist = self.pos - mob.pos
            if 0 < dist.length() < TOWER_ATTACK_RADIUS:
                mobs_in_range.append(mob)
        for mob in mobs_in_range:
            if closest_mob is None:
                closest_mob = mob
            elif closest_mob.distance_from_end > mob.distance_from_end and mob.alive():
                closest_mob = mob
            self.target = closest_mob

    def shoot(self):
        now = pg.time.get_ticks()
        # print(self.target.alive())
        if self.target and self.target.alive():
            if now - self.last_shot > TOWER_FIRE_RATE:
                self.last_shot = now
                self.shooting_anim()
                self.target.health -= self.damage

    def shooting_anim(self):
        self.shooting = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 2)

    def update(self, *args):
        self.acquire_target()
        self.shoot()
        self.image.fill(WHITE)
        if self.shooting:
            # print("shooting")
            try:
                self.image.fill((255, 0, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                self.shooting = False


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHTGREY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.hit_rect = MOB_HIT_RECT
        self.pos = vec(self.rect.center)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0
        self.health = MOB_HEALTH
        self.health_bar = None
        self.speed = MOB_SPEED
        self.damage = MOB_DAMAGE
        self.distance_from_end = None

    def draw_health(self):
        health_pct = self.health / MOB_HEALTH
        if health_pct > 0.6:
            col = GREEN
        elif health_pct > 0.3:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * health_pct)
        self.health_bar = pg.Rect(0, 0, width, 7)
        pg.draw.rect(self.image, col, self.health_bar)

    def update(self):
        # The mob only needs to travel to the left
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHTGREY)
        self.vel = vec(-self.speed, 0)
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if self.health <= 0:
            self.kill()
        self.distance_from_end = (self.pos - self.game.end.rect.center).length_squared()
        print(self.distance_from_end)


class End(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = END_HEALTH

    def draw_health(self):
        health_pct = self.health / END_HEALTH
        if health_pct > 0.6:
            col = GREEN
        elif health_pct > 0.3:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * health_pct)
        self.health_bar = pg.Rect(0, 0, width, 7)
        pg.draw.rect(self.image, col, self.health_bar)

    def update(self, *args):
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(CYAN)


# It seems like it will be very difficult to have bullets hit mobs, expecially when they have to track them around
# corners. I am going to scrap this sprite for now, and maybe call it back if slow towers like missiles or something are
# in play.
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((5, 5))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * BULLET_SPEED
        self.damage = damage

    def update(self, *args):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
