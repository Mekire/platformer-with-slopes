import os
import sys
import pickle
import wx
import pygame as pg


class MapCreator(object):
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.pallet = SHEET
        self.cell_size = (32,32)
        self.pal_rect = self.pallet.get_rect()
        self.map_rect = pg.Rect(288,0,544,544)
        self.map_dict = {}
        self.cells = rip_from_sheet(SHEET,self.cell_size,(8,2))
        self.selected = (0,0)

    def save_map(self):
        wx_app = wx.App(False)
        ask = wx.TextEntryDialog(None,"Save as:")
        ask.ShowModal()
        result = ask.GetValue()
        if result:
            try:
                with open(result,"wb") as myfile:
                    pickle.dump(self.map_dict,myfile)
                    print("Map saved.")
            except IOError:
                print("Invalid filename.")
        else:
            print("File name not entered.  Data not saved.")

    def load_map(self):
        wx_app = wx.App(False)
        ask = wx.TextEntryDialog(None,"Load file:")
        ask.ShowModal()
        result = ask.GetValue()
        if result:
            try:
                with open(result,"rb") as myfile:
                    self.map_dict = pickle.load(myfile)
                    print("Map loaded.")
            except IOError:
                print("File not found.")
        else:
            print("Filename not entered.  Cannot load data.")

    def change_selected(self,event):
        if event.button == 1:
            mouse = event.pos
            if self.pal_rect.collidepoint(mouse):
                self.selected = mouse[0]//32,mouse[1]//32

    def event_loop(self):
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

    def redraw_pallet(self):
        """Redraws the pallet tiles and the selector rectangle."""
        self.screen.blit(self.pallet,(0,0))
        rect = (self.selected[0]*32,self.selected[1]*32,32,32)
        pg.draw.rect(self.screen,(255,0,0),rect,1)

    def add_and_del(self,event):
        """Call appropriate function when clicking on the map area."""
        mouse = event.pos
        coords = (mouse[0]-self.map_rect.x)//32,(mouse[1]-self.map_rect.y)//32
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

    def redraw_map(self):
        for destin,target in self.map_dict.items():
            destin = (destin[0]*32+self.map_rect.x,destin[1]*32+self.map_rect.y)
            self.screen.blit(self.cells[target],destin)

    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.screen.fill(0)
            self.screen.fill((255,0,0),(256,0,32,600))
            self.redraw_pallet()
            self.redraw_map()
            pg.display.update()
            self.clock.tick(self.fps)


def rip_from_sheet(sheet,cell_size,sheet_size):
    coord_dict = {}
    for j in range(sheet_size[1]):
        for i in range(sheet_size[0]):
            rect = pg.Rect((i*cell_size[0],j*cell_size[1]),cell_size)
            coord_dict[(i,j)] = sheet.subsurface(rect)
    return coord_dict


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_mode((832,256))
    SHEET = pg.image.load("basic_tileset_big.png").convert()
    SHEET.set_colorkey((255,0,255))
    run_it = MapCreator()
    run_it.main_loop()
    pg.quit()
    sys.exit()




