from tools import load_img

from functools import cached_property
class Item:
    def __init__(self, img_path : str, name : str, max_stack : int=64):
        self.img_path = img_path
        self.name = name
        self.max_stack = max_stack



    @cached_property
    def img(self):
        #only load the image when its needed
        #also prevents an error where the image tries to load before pg.set_mode has been called
        return load_img(self.img_path)


