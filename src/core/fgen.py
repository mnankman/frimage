import math
from PIL import Image
import random
import numpy as np
import lib.wxdyn.log as  log
            
def gaussian(x, a, b, c, d=0):
    return a * math.exp(-(x - b)**2 / (2 * c**2)) + d

def pixel(i, width=100, map=[], spread=2):
    width = float(width)
    r = sum([gaussian(i, p[1][0], p[0] * width, width/(spread*len(map))) for p in map])
    g = sum([gaussian(i, p[1][1], p[0] * width, width/(spread*len(map))) for p in map])
    b = sum([gaussian(i, p[1][2], p[0] * width, width/(spread*len(map))) for p in map])
    return min(1.0, r), min(1.0, g), min(1.0, b)

def get_gradient_2d(start, stop, width, height, is_horizontal):
    if is_horizontal:
        return np.tile(np.linspace(start, stop, width), (height, 1))
    else:
        return np.tile(np.linspace(start, stop, height), (width, 1)).T

def get_gradient_3d(width, height, start_list, stop_list, is_horizontal_list):
    result = np.zeros((height, width, len(start_list)), dtype=np.float)
    for i, (start, stop, is_horizontal) in enumerate(zip(start_list, stop_list, is_horizontal_list)):
        result[:, :, i] = get_gradient_2d(start, stop, width, height, is_horizontal)
    return result

def getImage(size, plot, gradient):
    assert plot.any()
    assert size
    assert gradient
    if plot.any() and gradient and size:
        w,h = size
        if len(plot.shape)==3:
            frameCount, pw, ph = plot.shape
        elif len(plot.shape)==2:
            frameCount = 1
            pw, ph = plot.shape
        else:
            return None
        frames=[]
        s = (w if w<=pw else pw, h if h<ph else ph)
        for f in range(frameCount):
            im = Image.new("RGB", s)
            ld = im.load()
            for y in range(s[1]):
                for x in range(s[0]):
                    v = plot[f,x,y] if len(plot.shape)==3 else plot[x,y]
                    ld[x,y] = gradient[int(v)]
            frames.append(im)
        frames[0].save('animated.gif', format='GIF',
               append_images=frames[1:], save_all=True, duration=120, loop=0)
        log.trace(function=getImage, args=plot.shape, returns=(len(frames), frames[0]))
        return frames[0]
    else:
        return None

def default_image(w=150, h=150):
    array = get_gradient_3d(w, h, (0, 0, 192), (255, 255, 64), (True, False, False))
    return Image.fromarray(np.uint8(array))

class Source:
    def __init__(self, im=None, heatmapBaseImageSize=(10,10)):
        self.heatmap = []
        self.__sourceImage__ = im if im else default_image()
        self.init(heatmapBaseImageSize)

    def init(self, heatmapBaseImageSize=(10,10)):
        sw,sh = self.__sourceImage__.size
        mw,mh = heatmapBaseImageSize
        self.heatmapBaseImage = self.__sourceImage__.resize((sw if sw<mw else mw, sh if sh<mh else mh))
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
        w,h = self.__sourceImage__.size
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
        return self.__sourceImage__

    def getGradientImage(self):
        return self.gradientImage

    def getHeatmapBaseImage(self):
        return self.heatmapBaseImage

class FractalGenerator:
    def __init__(self, source, size=(512,512)):
        self.source = source
        self.size = size
        self.image = None

    def setup(self, **parameters):
        for k in parameters.keys():
            if hasattr(self, k):
                setattr(self, k, parameters[k])

    def plot(self, progressHandler=None):
        pass
        
    async def generate(self, progressHandler=None):
        self.plotValues, self.maxValue = self.plot(progressHandler=progressHandler)
        log.trace(function=self.generate, returns=(self.plotValues.shape))

class JuliaGenerator(FractalGenerator):
    def __init__(self, source, size=(512,512), area=(-2.0,1.0,-1.5,1.5), cxy=None, maxIt=256):
        super().__init__(source, size)
        self.area = area
        self.cxy = cxy
        self.maxIt = maxIt

    def plot(self, progressHandler=None):
        cx, cy = self.cxy if self.cxy!=None else (random.random() * 2.0 - 1.0, random.random() - 0.5)
        c = complex(cx, cy)
        w,h = self.size
        plotValues = np.empty(self.size)
        xa,xb,ya,yb = self.area  # drawing area (xa < xb and ya < yb)
        fy = (yb - ya) / (h - 1)
        fx = (xb - xa) / (w - 1)
        i_max = 0
        for y in range(h):
            zy = y * fy + ya
            for x in range(w):
                zx = x * fx + xa
                z = complex(zx, zy)
                for i in range(self.maxIt):
                    if abs(z) > 2.0: break 
                    z = z * z + c 
                plotValues[x,y] = i
                i_max = i if i>i_max else i_max
            if progressHandler!=None and y % 10 == 0:
                progressHandler(self, int(100*y/h))
        if progressHandler!=None: progressHandler(self, 100)
        return (plotValues, i_max)


class MandelbrotGenerator(FractalGenerator):
    def __init__(self, source, size=(512,512), areas=[(-2.0,1.0,-1.5,1.5)], maxIt=256):
        super().__init__(source, size)
        self.area = None
        self.areas = areas
        self.maxIt = maxIt

    def plot(self, progressHandler=None):
        if self.areas==None and self.area!=None:
            self.areas=[self.area]
        n = len(self.areas)
        w,h = self.size
        self.plotValues = np.empty((n,w,h))
        self.i_max = 0
        for f in range(n):
            self.area = self.areas[f]
            self.plotFrame(progressHandler, n, f)
        return (self.plotValues, self.i_max)
    
    def plotFrame(self, progressHandler=None, n=1, frame=0):
        log.debug(function=self.plotFrame, args=(n,frame))
        w,h = self.size
        xa,xb,ya,yb = self.area  # drawing area (xa < xb and ya < yb)
        fy = (yb - ya) / (h - 1)
        fx = (xb - xa) / (w - 1)
        total=n*h
        for y in range(h):
            cy = y * fy  + ya
            for x in range(w):
                cx = x * fx + xa
                c = complex(cx, cy)
                z = 0
                for i in range(self.maxIt):
                    if abs(z) > 2.0: break 
                    z = z * z + c 
                self.plotValues[frame, x, y] = i
                self.i_max = i if i>self.i_max else self.i_max
            if progressHandler!=None and y % 10 == 0:
                frameprogress=y/h
                totalprogress=frame + frameprogress
                progressHandler(self, int(totalprogress*100/n))
        if progressHandler!=None: progressHandler(self, int((frame+1)*100/n))


from decimal import Decimal
class SmoothMandelbrotGenerator(FractalGenerator):
    def __init__(self, source, size=(512,512), area=(-2.0,1.0,-1.5,1.5), maxIt=256):
        super().__init__(source, size)
        self.area = area
        self.maxIt = maxIt

    def plot(self, progressHandler=None):
        w,h = self.size
        self.plotValues = np.empty(self.size)
        xa,xb,ya,yb = self.area  # drawing area (xa < xb and ya < yb)
        fy = (yb - ya) / (h - 1)
        fx = (xb - xa) / (w - 1)
        mu_max = 0
        for y in range(h):
            cy = y * fy  + ya
            for x in range(w):
                cx = x * fx + xa
                c = complex(cx, cy)
                z = complex(0, 0)
                for i in range(self.maxIt):
                    modulus = Decimal(math.sqrt(z.real*z.real + z.imag*z.imag))
                    if modulus > 2.0: break
                    z = z*z+c 

                for n in range(2): z=z*z+c
                i += n+1
                modulus = Decimal(math.sqrt(z.real*z.real + z.imag*z.imag))
                try:
                    mu = i - math.log(math.log(modulus)) / math.log(Decimal(2.0))
                except ValueError as ve:
                    mu = i
                finally:
                    mu_max = mu if mu>mu_max else mu_max
                    self.plotValues[x,y] = int(mu)

            if progressHandler!=None and y % 10 == 0:
                progressHandler(self, int(100*y/h))
        progressHandler(self, 100)

    
