import math
from PIL import Image, ImageDraw

class ImageBox:
    ORIENTATION_HORIZONTAL = 0
    ORIENTATION_VERTICAL = 1
    
    def __init__(self, orientation=ORIENTATION_HORIZONTAL, margin=5, spacing=5, background=(0,0,0)):
        self.image = Image.new('RGB', (0,0))
        self.orientation = orientation
        self.images = []
        self.margin = margin
        self.spacing = spacing
        self.background = background

    def addImage(self, im):
        self.images.append(im)
        self.layout()

    def setBackground(self, rgb):
        self.background = rgb
        self.layout()
        
    def layout(self):
        if self.orientation==ImageBox.ORIENTATION_HORIZONTAL: self.__horizontal__()
        if self.orientation==ImageBox.ORIENTATION_VERTICAL: self.__vertical__()

    def __horizontal__(self):
        total_size = (0, 0)
        for im in self.images:
            total_size = (total_size[0] + im.size[0], total_size[1] if total_size[1] > im.size[1] else im.size[1])
        total_size = (total_size[0] + (len(self.images)-1)*self.spacing + 2*self.margin, total_size[1] + 2*self.margin)

        self.image = Image.new('RGB', total_size, self.background)
        pos = (self.margin, self.margin)
        for im in self.images:
            self.image.paste(im, pos)
            pos = (pos[0] + im.size[0] + self.spacing, pos[1])

    def __vertical__(self):
        total_size = (0, 0)
        for im in self.images:
            total_size = (total_size[0] if total_size[0] > im.size[0] else im.size[0], total_size[1] + im.size[1])
        total_size = (total_size[0] + 2*self.margin, total_size[1] + (len(self.images)-1)*self.spacing + 2*self.margin)

        self.image = Image.new('RGB', total_size, self.background)
        pos = (self.margin, self.margin)
        for im in self.images:
            self.image.paste(im, pos)
            pos = (pos[0], pos[1] + im.size[1] + self.spacing)

    def getImage(self):
        return self.image