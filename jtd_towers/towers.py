import pygame as pg
from settings import *
from itertools import chain

vec = pg.math.Vector2


class Tower(pg.sprite.Sprite):
    def __init__(self, game, x, y, name="Gun"):
        self._layer = TOWER_LAYER
        self.groups = game.all_sprites, game.towers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.name = name
        self.game = game
        # Temporary Image
        self.image = self.game.tower_images[self.name]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.pos = vec(self.rect.center)
        self.damage = TOWERS["Gun"]["Damage"]
        self.attack_radius = TOWERS["Gun"]["Attack Radius"]
        self.fire_rate = TOWERS["Gun"]["Fire Rate"]
        self.target = None
        self.last_shot = pg.time.get_ticks()
        self.shooting = False
        self.damage_alpha = None
        self.rot = 0

    # Chooses target based on how close it is to the end
    def acquire_target(self):
        mobs_in_range = []
        closest_mob = None
        # Find mobs within range of tower's radius
        for mob in self.game.mobs:
            dist = self.pos - mob.pos
            if 0 < dist.length() < self.attack_radius:
                mobs_in_range.append(mob)
        # Target the closest mob the the End sprite
        for mob in mobs_in_range:
            if closest_mob is None:
                closest_mob = mob
            elif closest_mob.distance_from_end > mob.distance_from_end and mob.alive():
                closest_mob = mob
            self.target = closest_mob
        # If there are no mobs in range, clear target
        if len(mobs_in_range) == 0:
            self.target = None

    def shoot(self):
        now = pg.time.get_ticks()
        if self.target and self.target.alive():
            if now - self.last_shot > self.fire_rate:
                self.last_shot = now
                # self.shooting_anim()
                self.target.health -= self.damage
                FireFlash(self.game, self.pos + vec(0, -40).rotate(-self.rot), self.rot)

    def shooting_anim(self):
        # Flash as shooting
        self.shooting = True
        self.damage_alpha = chain(DAMAGE_ALPHA)

    def update(self, *args):
        self.acquire_target()
        self.shoot()
        if self.target is not None:
            self.rot = (self.target.pos - self.pos).angle_to(vec(0, -1))
        self.image = pg.transform.rotate(self.game.tower_images[self.name], self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        if self.shooting:
            # TODO THis makes the tower disappear
            # I have just disabled this for now
            try:
                self.image.fill((255, 0, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                self.shooting = False


class GunTower(Tower):
    def __init__(self, game, x, y):
        Tower.__init__(self, game, x, y)
        # self.image.fill(TOWERS["Gun"]["Color"])
        self.damage = TOWERS["Gun"]["Damage"]
        self.attack_radius = TOWERS["Gun"]["Attack Radius"]
        self.fire_rate = TOWERS["Gun"]["Fire Rate"]
        self.name = "Gun"


class CannonTower(Tower):
    def __init__(self, game, x, y):
        Tower.__init__(self, game, x, y)
        # self.image.fill(TOWERS["Cannon"]["Color"])
        self.damage = TOWERS["Cannon"]["Damage"]
        self.attack_radius = TOWERS["Cannon"]["Attack Radius"]
        self.fire_rate = TOWERS["Cannon"]["Fire Rate"]
        self.name = "Cannon"


class FireFlash(pg.sprite.Sprite):
    def __init__(self, game, pos, rot):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.transform.rotate(self.game.gun_fire_img, rot)
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > 40:
            self.kill()
