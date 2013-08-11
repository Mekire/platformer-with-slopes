"""
This is a very basic map editor written with the purpose of quickly creating
a testing environment.  Currently it is Python 2.x specific as it utilizes
wx python gui elements.  Mouse selects tiles and places them (right button to
delete tile); arrow keys pan the map. CTRL+L and CTRL+S open load and save
dialogues.

-Written by Sean J. McKiernan 'Mekire'
"""

import os
import sys
import pickle
import wx
import pygame as pg


DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}


class MapCreator(object):
    """A simple map tile editor."""
    def __init__(self):
        """Set up the display.  Get the pallet ready and divide the pallet
        into cell subsurfaces."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.pallet = SHEET
        self.cell_size = (32,32)
        self.pal_rect = self.pallet.get_rect()
        self.map_rect = pg.Rect(288,0,544,256)
        self.offset = [0,0]
        self.timer = 0.0
        self.map_dict = {}
        self.cells = rip_from_sheet(SHEET,self.cell_size,(8,4))
        self.selected = (0,0)
        self.font = pg.font.SysFont("Arial",10)

    def save_map(self,directory="maps"):
        """Uses a wx python widget for save map dialog."""
        wx_app = wx.App(False)
        ask = wx.FileDialog(None, "Save As",directory, "",
                            "Map files (*.txt,*.map)|*.txt;*.map",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        ask.ShowModal()
        path = ask.GetPath()
        if path:
            try:
                with open(path,"wb") as myfile:
                    pickle.dump(self.map_dict,myfile)
                    print("Map saved.")
            except IOError:
                print("Invalid filename.")
        else:
            print("File name not entered.  Data not saved.")

    def load_map(self,directory="maps"):
        """Uses a wx python widget for load map dialog."""
        wx_app = wx.App(False)
        ask = wx.FileDialog(None, "Open", "", "",
                           "Map files (*.txt,*.map)|*.txt;*.map",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ask.ShowModal()
        path = ask.GetPath()
        if path:
            try:
                with open(path,"rb") as myfile:
                    self.map_dict = pickle.load(myfile)
                    print("Map loaded.")
            except IOError:
                print("File not found.")
        else:
            print("Filename not entered.  Cannot load data.")

    def change_selected(self,event):
        """Changes the currently selected tile on the pallet."""
        if event.button == 1:
            mouse = event.pos
            if self.pal_rect.collidepoint(mouse):
                self.selected = mouse[0]//32,mouse[1]//32

    def event_loop(self):
        """Get mouse events for tile placement and pallet change; and
        keyboard events for saving and loading."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.on_click(event)
            elif event.type == pg.KEYDOWN:
                self.on_keydown(event)

    def on_keydown(self,event):
        """Processing for KEYDOWN events."""
        if event.key == pg.K_s:
            if event.mod & pg.KMOD_CTRL:
                self.save_map()
        elif event.key == pg.K_l:
            if event.mod & pg.KMOD_CTRL:
                self.load_map()

    def on_click(self,event):
        """Processing for MOUSEBUTTONDOWN events."""
        self.change_selected(event)
        self.add_and_del(event)

    def add_and_del(self,event):
        """Call appropriate function when clicking on the map area."""
        mouse = event.pos
        coords = ((mouse[0]-self.map_rect.x+self.offset[0]*32)//32,
                  (mouse[1]-self.map_rect.y+self.offset[1]*32)//32)
        if self.map_rect.collidepoint(mouse):
            if event.button == 1:
                self.add_tile(coords)
            elif event.button == 3:
                self.del_tile(coords)

    def del_tile(self,coords):
        """Delete from map and dictionary."""
        if coords in self.map_dict:
            self.map_dict.pop(coords)

    def add_tile(self,coords):
        """Add to map and dictionary."""
        self.map_dict[coords] = self.selected

    def redraw_pallet(self):
        """Redraws the pallet tiles and the selector rectangle."""
        self.screen.fill(0,(0,0,256,288))
        self.screen.blit(self.pallet,(0,0))
        rect = (self.selected[0]*32,self.selected[1]*32,32,32)
        pg.draw.rect(self.screen,(255,0,0),rect,1)
        self.screen.fill((255,0,0),(256,0,32,288))

    def redraw_map(self):
        """Itterate throw the current map_dict and redraw the tiles."""
        self.screen.fill((200,200,200))
        self.screen.fill(0,self.map_rect)
        for destin,target in self.map_dict.items():
            destin = (destin[0]*32+self.map_rect.x-self.offset[0]*32,
                      destin[1]*32+self.map_rect.y-self.offset[1]*32)
            self.screen.blit(self.cells[target],destin)
        pg.draw.rect(self.screen,(255,0,0),self.map_rect,3)

    def draw_grid(self):
        """Draws a blue grid to aid in tile placement."""
        self.screen.fill((255,0,0),(256+544+32,256,32,32))
        stop_x = self.map_rect.right+self.cell_size[0]
        for i in range(self.map_rect.x,stop_x,self.cell_size[0]):
            self.screen.fill((0,0,255),(i,0,1,self.screen_rect.height))
        for i in range(0,self.screen_rect.width,self.cell_size[1]):
            self.screen.fill((0,0,255),(self.map_rect.x,i,self.screen_rect.width,1))

    def render_numbers(self):
        """Draws the coordinate numbers on the border of the grid."""
        for i in range(17):
            number = self.center_num_in_cell(i,0)
            self.screen.blit(number,(self.map_rect.x+32*i,256))
        for j in range(8):
            number = self.center_num_in_cell(j,1)
            self.screen.blit(number,(self.map_rect.right,32*j))

    def center_num_in_cell(self,number,index):
        """Called by the render_numbers function to center number in a cell."""
        num = pg.Surface(self.cell_size).convert_alpha()
        num.fill((0,0,0,0))
        num_rect = num.get_rect()
        rendered = self.font.render(str(self.offset[index]+number),True,(0,0,0))
        rend_rect = rendered.get_rect(center=num_rect.center)
        num.blit(rendered,rend_rect)
        return num

    def check_panning(self):
        """Checks the held keys and pans screen appropriately.  Timer used to
        limit pan speed."""
        now = pg.time.get_ticks()
        if now - self.timer > 1000/10.0:
            self.timer = now
            for key in DIRECT_DICT:
                if self.keys[key]:
                    for i in (0,1):
                        self.offset[i] += DIRECT_DICT[key][i]

    def update(self):
        """Checks the user panning and then redraws everything."""
        self.check_panning()
        self.redraw_map()
        self.draw_grid()
        self.redraw_pallet()
        self.render_numbers()

    def main_loop(self):
        """Where we stop nobody knows."""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)


def rip_from_sheet(sheet,cell_size,sheet_size):
    """Takes a sheet image, a size of each cell, and a size of the
    sheet (in cells).  Returns a dict of sheet coordinates to subsurfaces."""
    coord_dict = {}
    for j in range(sheet_size[1]):
        for i in range(sheet_size[0]):
            rect = pg.Rect((i*cell_size[0],j*cell_size[1]),cell_size)
            coord_dict[(i,j)] = sheet.subsurface(rect)
    return coord_dict


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_mode((864,288))
    SHEET = pg.image.load("tiles_edit.png").convert()
    SHEET.set_colorkey((255,0,255))
    run_it = MapCreator()
    run_it.main_loop()
    pg.quit()
    sys.exit()
