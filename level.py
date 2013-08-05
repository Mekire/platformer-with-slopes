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
    def __init__(self,sheet,mapname):
        self.pallet = sheet
        self.cell_size = (32,32)
        self.map_rect = pg.Rect(0,0,544,544)
        self.map_dict = self.load_map(mapname)
        self.rect_dict = self.make_rect_dict()
        self.cells = rip_from_sheet(self.pallet,self.cell_size,(8,2))
        self.height_dict = gen_height_map(self.cells)
        self.mask_dict = self.make_mask_dict()

    def load_map(self,filename,directory="maps"):
        """Unpickle the requested file."""
        with open(os.path.join(directory,filename),"rb") as myfile:
            loaded_map = pickle.load(myfile)
            return loaded_map

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

    def update(self,surface):
        """Redraw tiles to surface."""
        for destination,target in self.map_dict.items():
            destination = (destination[0]*self.cell_size[0]+self.map_rect.x,
                           destination[1]*self.cell_size[1]+self.map_rect.y)
            surface.blit(self.cells[target],destination)
