"""
A basic map loader for our program.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import pickle
import pygame as pg


def gen_height_map(cells):
    """Create a list of pixel heights for each cell."""
    height_dict = {}
    test_mask = pg.Mask((1,cells[(0,0)].get_height()))
    test_mask.fill()
    for coord,cell in cells.items():
        heights = []
        mask = pg.mask.from_surface(cell)
        for i in range(cell.get_width()):
            height = mask.overlap_area(test_mask,(i,0))
            heights.append(height)
        height_dict[(coord)] = heights
    return height_dict


def rip_from_sheet(sheet,cell_size,sheet_size):
    """Return a dict of coordinates to surfaces."""
    coord_dict = {}
    for j in range(sheet_size[1]):
        for i in range(sheet_size[0]):
            rect = pg.Rect((i*cell_size[0],j*cell_size[1]),cell_size)
            coord_dict[(i,j)] = sheet.subsurface(rect)
    return coord_dict


class LevelMap(object):
    """Mangages maps created by our map editor."""
    def __init__(self,sheet,mapname,viewport):
        self.pallet = sheet
        self.viewport = viewport
        self.viewport_image = pg.Surface(self.viewport.size).convert_alpha()
        self.cell_size = (32,32)
        self.rect,self.map_dict = self.load_map(mapname)
        self.rect_dict = self.make_rect_dict()
        self.cells = rip_from_sheet(self.pallet,self.cell_size,(8,4))
        self.height_dict = gen_height_map(self.cells)
        self.mask_dict = self.make_mask_dict()

    def load_map(self,filename,directory="maps"):
        """Unpickle the requested file."""
        with open(os.path.join(directory,filename),"rb") as myfile:
            loaded_map = pickle.load(myfile)
        return self.preprocess_map(loaded_map)

    def make_rect_dict(self):
        """Make a dict of map location coordinates to rects for initial
        collision detection."""
        width,height = self.cell_size
        rect_dict = {}
        for cell in self.map_dict:
            rect_dict[cell] = pg.Rect(cell[0]*width,cell[1]*height,width,height)
        return rect_dict

    def make_mask_dict(self):
        """Make a dict of map location coordinates to masks for final
        collision detection."""
        mask_dict = {}
        for cell in self.cells:
            mask_dict[cell] = pg.mask.from_surface(self.cells[cell])
        return mask_dict

    def update(self,surface,player):
        """Redraw tiles to surface."""
        self.update_viewport(player)
        self.viewport_image.fill(0)
        for destination,target in self.map_dict.items():
            destination = (destination[0]*self.cell_size[0],
                           destination[1]*self.cell_size[1])
            screen_final = (destination[0]-self.viewport.x,
                            destination[1]-self.viewport.y)
            if self.viewport.x-32 <= destination[0] <= self.viewport.right:
                if self.viewport.y-32 <= destination[1] <= self.viewport.bottom:
                    self.viewport_image.blit(self.cells[target],screen_final)
        player.draw(self.viewport_image,self.viewport)
        surface.blit(self.viewport_image,(0,0))

    def get_dimensions(self,map_dict):
        """Find the rectangle size of the entire map."""
        min_x = min(x for (x,y) in map_dict)
        min_y = min(y for (x,y) in map_dict)
        max_x = max(x for (x,y) in map_dict)
        max_y = max(y for (x,y) in map_dict)
        width,height = (max_x-min_x+1)*32,(max_y-min_y+1)*32
        rect = pg.Rect(min_x*32,min_y*32,width,height)
        return rect

    def normalize_map(self,rect,map_dict):
        """Re-map coordinates so that the topleft corner of the map is
        at (0,0)"""
        topleft = rect.x//32,rect.y//32
        remapped = {}
        if topleft != (0,0):
            for coord in map_dict:
                new_key = (coord[0]-topleft[0],coord[1]-topleft[1])
                remapped[new_key] = map_dict[coord]
        rect.topleft = (0,0)
        return rect,remapped

    def preprocess_map(self,map_dict):
        """Find size of map and normalize its coordinates."""
        map_rect = self.get_dimensions(map_dict)
        return self.normalize_map(map_rect,map_dict)

    def update_viewport(self,player):
        """The viewport will stay centered on the player unless the player
        approaches the edge of the map."""
        for i in (0,1):
            minimal = max(0,player.rect.center[i]-self.viewport.size[i]//2)
            maximal = self.rect.size[i]-self.viewport.size[i]
            self.viewport[i] = min(minimal,maximal)
