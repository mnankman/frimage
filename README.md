FrImage Studio is a hobby project that got a little bit out of hand...
I first started experimenting with a way to use the colour palette of a photograph for colouring Mandelbrot (and Julia) fractals. 
The first results were rather promising, so I soon needed an easier way to explore the fractal space to find interesting shapes. 
Which motivated me to build a complete fractal imaging studio. 

FrImage Studio is built on Python3 (3.9.4) and depends on the following libraries:
- Pillow Imaging Library (PIL) 9.0.1
- wxPython 4.1.1
- wxasync 0.46
- Numpy 1.23.1

main.py starts the main application with minimal logging output (only the ERROR category is shown)
mainwindow.py starts the application with lots and lots of logging output 
