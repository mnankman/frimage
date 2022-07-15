import math
from PIL import Image, ImageDraw
import random
from img.imgengine import *

def project1(size=(800,600)):
    src = Source('resource/sunset.jpg', (12,12))
    g = JuliaGenerator(src, size, True, (-0.0008,0.0008,-0.0008,0.0008), (-0.6523253489293293, -0.44925312958958075))
    g.generate()
    g.getImage().save("project1.png")

def project3(size=(800,600)):
    src = Source('resource/tropical-sunset.jpg', (12,12))
    g = JuliaGenerator(src, size, False, (-0.0008,0.0008,-0.0008,0.0008), (-0.6523253489293293, -0.44925312958958075))
    g.generate()
    g.getImage().save("project3.png")

def project2():
    src = Source('resource/architecture1.jpg', (12,12))
    g = MandelbrotGenerator(src, (800,800), True)
    g.generate()
    g.getImage().save("project2.png")

def project4():
    src = Source('resource/architecture2.jpg', (15,15))
    g = MandelbrotGenerator(src, (800,800), True)
    g.generate()
    g.getImage().save("project4.png")

def project5():
    src = Source('resource/ijsvogel2.jpg', (18,18))
    g = MandelbrotGenerator(src, (800,800), False)
    g.generate()
    g.getImage().save("project5.png")

def project6():
    src = Source('resource/rubberduck.jpg', (12,12))
    g = MandelbrotGenerator(src, (800,800), True)
    g.generate()
    g.getImage().save("project6.png")

def project7():
    src = Source('resource/rubberduck.jpg', (5,5))
    g = JuliaGenerator(src)
    g.setup(size=(800,600), reverseColors=True, area=(-0.0008,0.0008,-0.0008,0.0008), cxy=(-0.6523253489293293, -0.44925312958958075))
    g.generate()
    g.getImage().save("project7.png")


if __name__ == '__main__':
    #project1((2560,1440))
    #project1()
    
    #project4()
    #project5()

    project7()

