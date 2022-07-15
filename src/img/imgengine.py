import math
from PIL import Image, ImageDraw
import random
from .imgbox import ImageBox
            
def gaussian(x, a, b, c, d=0):
    return a * math.exp(-(x - b)**2 / (2 * c**2)) + d

def pixel(i, width=100, map=[], spread=2):
    width = float(width)
    r = sum([gaussian(i, p[1][0], p[0] * width, width/(spread*len(map))) for p in map])
    g = sum([gaussian(i, p[1][1], p[0] * width, width/(spread*len(map))) for p in map])
    b = sum([gaussian(i, p[1][2], p[0] * width, width/(spread*len(map))) for p in map])
    return min(1.0, r), min(1.0, g), min(1.0, b)

class Source:
    def __init__(self, sourceImagePath, heatmapBaseImageSize=(10,10)):
        self.heatmap = []
        self.sourceImagePath = sourceImagePath
        im = Image.open(self.sourceImagePath)
        self.sourceImage = im.convert('RGB')
        self.init(heatmapBaseImageSize)

    def init(self, heatmapBaseImageSize=(10,10)):
        w,h = self.sourceImage.size
        mw,mh = heatmapBaseImageSize
        self.heatmapBaseImage = self.sourceImage.resize((w if w<mw else mw, h if h<mh else mh))
        self.heatmap = []
        color_count = {}
        img = self.heatmapBaseImage
        w, h = img.size
        # iterate through each pixel in the image and keep a count per unique color
        for x in range(w):
            for y in range(h):
                rgb = img.getpixel((x, y))
                if rgb in color_count:
                    color_count[rgb] += 1
                else:
                    color_count[rgb] = 1
        
        t = w * h
        total_steps = len(color_count)
        step = 0.0
        for c in sorted(color_count):
            n = color_count[c]
            r,g,b = c
            mapping = [round(step, 3), (round(r/255, 3), round(g/255, 3), round(b/255, 3))]
            #print(mapping)
            self.heatmap.append(mapping)
            step+=n*(1+1/total_steps)/t

        self.createGradientImage()

    def createGradientImage(self):
        w,h = self.sourceImage.size
        im = Image.new('RGB', (w,1))
        ld = im.load()
        for x in range(w):
            r, g, b = pixel(x, width=w, map=self.heatmap)
            r, g, b = [int(256*v) for v in (r, g, b)]
            ld[x, 0] = r, g, b
        self.gradientImage = im

    def getGradientPixels(self, w, reverse=False):
        pixels = []
        for i in range(w):
            r, g, b = pixel(w-i-1 if reverse else i, width=w, map=self.heatmap)
            r, g, b = [int(256*v) for v in (r, g, b)]
            pixels.append((r,g,b))
        return pixels

    def getSourceImage(self):
        return self.sourceImage

    def getGradientImage(self):
        return self.gradientImage

    def getHeatmapBaseImage(self):
        return self.heatmapBaseImage

class ImageGenerator:
    def __init__(self, source, size=(512,512), reverseColors=False):
        self.source = source
        self.size = size
        self.reverseColors = reverseColors

    def setup(self, **parameters):
        for k in parameters.keys():
            if hasattr(self, k):
                setattr(self, k, parameters[k])
        
    async def generate(self, progressHandler=None):
        self.image = Image.new("RGB", self.size)

    def getImage(self): 
        return self.image

class JuliaGenerator(ImageGenerator):
    def __init__(self, source, size=(512,512), reverseColors=False, area=(-2.0,1.0,-1.5,1.5), cxy=None, maxIt=256):
        super().__init__(source, size, reverseColors)
        self.area = area
        self.cxy = cxy
        self.maxIt = maxIt

    async def generate(self, progressHandler=None):
        self.image = Image.new("RGB", self.size)
        self.pixels = self.source.getGradientPixels(self.maxIt, self.reverseColors)
        ld = self.image.load()
        
        # Julia set to draw
        print("cxy=", self.cxy)
        cx, cy = self.cxy if self.cxy!=None else (random.random() * 2.0 - 1.0, random.random() - 0.5)
        c = complex(cx, cy)
        
        # drawing area (xa < xb and ya < yb)
        xa,xb,ya,yb = self.area
        
        w, h = self.image.size
        for y in range(h):
            zy = y * (yb - ya) / (h - 1) + ya
            for x in range(w):
                zx = x * (xb - xa) / (w - 1) + xa
                z = complex(zx, zy)
                for i in range(self.maxIt):
                    if abs(z) > 2.0: break 
                    z = z * z + c 
                ld[x,y] = self.pixels[i]
            if progressHandler!=None and y % 10 == 0:
                progressHandler(self, int(100*y/h))
        progressHandler(self, 100)

    def getImage(self):
        return self.image

    def getFancyImage(self):
        sourceBox = ImageBox(ImageBox.ORIENTATION_HORIZONTAL, 2, 2, self.pixels[255])
        sourceBox.addImage(self.source.getSourceImage())
        
        fractalBox = ImageBox(ImageBox.ORIENTATION_HORIZONTAL, 1, 1, self.pixels[255])
        fractalBox.addImage(self.image)

        im = fractalBox.getImage()
        w,h = im.size
        sw,sh=sourceBox.getImage().size
        im.paste(sourceBox.getImage(), (10,h-sh-10))
        return im

class MandelbrotGenerator(ImageGenerator):
    def __init__(self, source, size=(512,512), reverseColors=False, area=(-2.0,1.0,-1.5,1.5), maxIt=256):
        super().__init__(source, size, reverseColors)
        self.area = area
        self.maxIt = maxIt

    async def generate(self, progressHandler=None):
        self.image = Image.new("RGB", self.size)
        self.pixels = self.source.getGradientPixels(self.maxIt, self.reverseColors)
        ld = self.image.load()
        
        # drawing area (xa < xb and ya < yb)
        xa,xb,ya,yb = self.area

        w,h = self.image.size        
        for y in range(h):
            cy = y * (yb - ya) / (h - 1)  + ya
            for x in range(w):
                cx = x * (xb - xa) / (w - 1) + xa
                c = complex(cx, cy)
                z = 0
                for i in range(self.maxIt):
                    if abs(z) > 2.0: break 
                    z = z * z + c 
                ld[x,y] = self.pixels[i]
            if progressHandler!=None and y % 10 == 0:
                progressHandler(self, int(100*y/h))
        progressHandler(self, 100)

    def getImage(self):
        return self.image

    def getFancyImage(self):
        sourceBox = ImageBox(ImageBox.ORIENTATION_HORIZONTAL, 2, 2, self.pixels[255])
        sourceBox.addImage(self.source.getSourceImage())

        fractalBox = ImageBox(ImageBox.ORIENTATION_HORIZONTAL, 2, 2, self.pixels[255])
        fractalBox.addImage(self.image)

        im = fractalBox.getImage()
        w,h = im.size
        sw,sh=sourceBox.getImage().size
        im.paste(sourceBox.getImage(), (5,5))
        return im

