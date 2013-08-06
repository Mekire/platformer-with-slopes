"""
Our player class including the (currently overly complicated) collision
mechanics.

-Written by Sean J. McKiernan 'Mekire'
"""


import pygame as pg


class _Collision(object):
    """Pulling some of the collision detection methods out for better
    organization.  Inherited by Player (and possibly other sprites later)."""
    def detect_ground(self,level):
        """Calls the appropriate collision function depending on if the player
        is on the ground or in the air."""
        if not self.fall:
            self.grounded(level)
        else:
            self.airborne(level)
        self.reset_wall_floor_rects()

    def grounded(self,level):
        """Detects the ground beneath the player when not jumping.
        Implementation is based around the information found at:
        http://info.sonicretro.org/Sonic_Physics_Guide"""
        change = None
        pads_on = [False,False]
        for i,floor in enumerate(self.floor_detect_rects):
            collide,pads_on = self.check_floor_initial(pads_on,(i,floor),level)
            if collide:
                change = self.check_floor_final(collide,(i,floor),change,level)
        if pads_on[0]^pads_on[1]:
            change = self.detect_glitch_fix(pads_on,change,level)
        if change != None:
            self.rect.y = int(change-self.rect.height)
        else:
            self.fall = True

    def check_floor_initial(self,pads_on,pad_details,level):
        """Find out if a detector is hitting a solid cell."""
        i,floor = pad_details
        collide = []
        for cell in level.rect_dict:
            if floor.colliderect(level.rect_dict[cell]):
                collide.append(cell)
                pads_on[i] = True
        return collide,pads_on

    def check_floor_final(self,collide,pad_details,change,level):
        """Get exact ground value from a colliding detector."""
        i,floor = pad_details
        for key in collide:
            coord = level.map_dict[key]
            cell_heights = level.height_dict[coord]
            x_loc_in_cell = floor.x-key[0]*level.cell_size[0]
            offset = cell_heights[x_loc_in_cell]
            if change == None:
                change = (key[1]+1)*level.cell_size[1]-offset
            else:
                change = min((key[1]+1)*level.cell_size[1]-offset,change)
        return change

    def detect_glitch_fix(self,pads,change,level):
        """Fixes a glitch with the blit location that occurs on up-slopes when
        one detection bar hits a solid cell and the other doesn't. This could
        probably still be improved."""
        inc,index = ((1,0) if not pads[0] else (-1,1))
        detector = self.floor_detect_rects[index].copy()
        pad_details = (index,detector)
        old_change = change
        while detector.x != self.floor_detect_rects[not index].x:
            detector.x += inc
            collide = self.check_floor_initial([0,0],pad_details,level)[0]
            change = self.check_floor_final(collide,pad_details,change,level)
            if change < old_change:
                return change
        return old_change

    def airborne(self,level):
        """Search for the ground via mask detection while in the air."""
        mask = self.floor_detect_mask
        check = (pg.Rect(self.rect.x+1,self.rect.y,self.rect.width-1,1),
                 pg.Rect(self.rect.x+1,self.rect.bottom-1,self.rect.width-2,1))
        stop_fall = False
        for rect in check:
            if self.collide_with(level,rect,mask,[0,int(self.y_vel)]):
                offset = [0,int(self.y_vel)]
                self.y_vel = self.adjust_pos(level,rect,mask,offset,1,)
                stop_fall = True
        self.rect.y += int(self.y_vel)
        if stop_fall:
            self.fall = False

    def detect_wall(self,level):
        """Detects collisions with walls."""
        if not self.fall:
            rect,mask = self.wall_detect_rect,self.wall_detect_mask
        else:
            rect,mask = self.rect,self.fat_mask
        if self.collide_with(level,rect,mask,(int(self.x_vel),0)):
            self.x_vel = self.adjust_pos(level,rect,mask,[int(self.x_vel),0],0)
        self.rect.x += int(self.x_vel)
        self.reset_wall_floor_rects()

    def adjust_pos(self,level,rect,mask,offset,off_ind):
        """Continuously calls the collide_with method, decrementing the players
        rect position until no collision is detected."""
        offset[off_ind] += (1 if offset[off_ind]<0 else -1)
        while 1:
            if any(self.collide_with(level,rect,mask,offset)):
                offset[off_ind] += (1 if offset[off_ind]<0 else -1)
                if not offset[off_ind]:
                    return 0
            else:
                return offset[off_ind]

    def collide_with(self,level,rect,mask,offset):
        """The real collision detection occurs here. Initial tests are done with
        rect collision and if positive further tests are done with masks."""
        test = pg.Rect((rect.x+offset[0],rect.y+offset[1]),rect.size)
        self.collide_ls = []
        for cell,rec in level.rect_dict.items(): #Rect collision first
            if test.colliderect(rec):  #If rect collision positive, test masks.
                level_rect = level.rect_dict[cell]
                mask_test = test.x-level_rect.x,test.y-level_rect.y
                level_mask = level.mask_dict[level.map_dict[cell]]
                if level_mask.overlap_area(mask,mask_test):
                    self.collide_ls.append(cell)
        return self.collide_ls


class Player(_Collision):
    """Our humble protagonist."""
    def __init__(self,*rect_style_args):
        self.x_vel = self.y_vel = 0
        self.fall = False
        self.speed = 3
        self.jump_power = -6.5
        self.jump_cut_magnitude = -3
        self.grav = 0.22
        self.rect = pg.Rect(rect_style_args)
        self.image = pg.Surface((self.rect.size)).convert()
        self.image.fill((100,0,255))
        self.setup_collision_rects()

    def setup_collision_rects(self):
        """Setup for the collision detection bars and rects. Currently only run
        on init."""
        self.reset_wall_floor_rects()
        self.fat_mask = pg.Mask(self.rect.size)
        self.fat_mask.fill()
        self.wall_detect_mask = pg.Mask(self.wall_detect_rect.size)
        self.wall_detect_mask.fill()
        self.floor_detect_mask = pg.Mask((self.rect.width-2,1))
        self.floor_detect_mask.fill()
        self.collide_ls = []

    def physics_update(self):
        """Currently just a very basic gravity function."""
        if self.fall:
            self.y_vel += self.grav
        else:
            self.y_vel = 0

    def reset_wall_floor_rects(self):
        """Sets the collision detection bar rects based on the players rect
        position.  Called every frame."""
        flr = (pg.Rect((self.rect.x+1,self.rect.y),(1,self.rect.height+16)),
               pg.Rect((self.rect.right-2,self.rect.y),(1,self.rect.height+16)))
        wall = pg.Rect(self.rect.x,self.rect.bottom-10,self.rect.width,1)
        self.floor_detect_rects = flr
        self.wall_detect_rect = wall

    def jump(self):
        """Called when the player presses the jump key."""
        if not self.fall:
            self.y_vel = self.jump_power
            self.fall = True

    def jump_cut(self):
        """Called when the palyer releases the jump key before maximum height is
        reached."""
        if self.fall:
            if self.y_vel < self.jump_cut_magnitude:
                self.y_vel = self.jump_cut_magnitude

    def check_keys(self,keys):
        """Calculate player's self.x_vel based on keys held."""
        self.x_vel = 0
        if keys[pg.K_RIGHT]:
            self.x_vel += self.speed
        if keys[pg.K_LEFT]:
            self.x_vel -= self.speed

    def draw_detectors(self,surface,shift):
        """Draws the collisions detector rects for demonstration purposes."""
        for wreck in self.floor_detect_rects:
            surface.fill((255,0,0),wreck.move(shift))
        surface.fill((0,255,255),self.wall_detect_rect.move(shift))

    def update(self,level,keys):
        """Check keys, collisions, physics, and draw."""
        self.check_keys(keys)
        self.detect_wall(level)
        self.detect_ground(level)
        self.physics_update()

    def draw(self,surface,view_rect):
        shift = (-view_rect[0],-view_rect[1])
        rect = self.rect.move(shift)
        surface.blit(self.image,rect)
        self.draw_detectors(surface,shift)
