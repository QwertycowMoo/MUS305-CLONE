# Idea is to listen to an image (preferably of space, a fractal, etc)
# find the average color of the image
# Then go pixel by pixel over the image and sonify the pixels so you can "hear" the colors


# Python code for Julia Fractal
from PIL import Image
from numpy import sqrt, array
from numpy.linalg import norm
from musx import Note, Score, Seq, MidiFile, rescale
from musx.midi import gm

# I copied these two calculation from some numpy website
# I did not do any of this work for either the julia or mandelbrot calculation
def julia_calculation(w, h, zoom, cX, cY, moveX, moveY, maxIter):
    # creating the new image in RGB mode
    bitmap = Image.new("RGB", (w, h), "white")
  
    # Allocating the storage for the image and
    # loading the pixel data.
    pix = bitmap.load()
    for x in range(w):
        for y in range(h):
            zx = 1.5*(x - w/2)/(0.5*zoom*w) + moveX
            zy = 1.0*(y - h/2)/(0.5*zoom*h) + moveY
            i = maxIter
            while zx*zx + zy*zy < 4 and i > 1:
                tmp = zx*zx - zy*zy + cX
                zy,zx = 2.0*zx*zy + cY, tmp
                i -= 1
  
            # convert byte to RGB (3 bytes), kinda 
            # magic to get nice colors
            # If it is black, then it is within the set
            pix[x,y] = (i << 21) + (i << 10) + i*8
    return bitmap

def mandelbrot_calculation(imgx, imgy, xa, xb, ya, yb, maxIt):  

    image = Image.new("RGB", (imgx, imgy))
    
    for y in range(imgy):
        zy = y * (yb - ya) / (imgy - 1)  + ya
        for x in range(imgx):
            zx = x * (xb - xa) / (imgx - 1)  + xa
            z = zx + zy * 1j
            c = z
            for i in range(maxIt):
                if abs(z) > 2.0: break
                z = z * z + c
            image.putpixel((x, y), ((i << 21) + (i << 10) + i*8))
    
    return image

def get_average_color(colors):
    # Uses sqrt of sum of squared because it gets closer to actual value
    sum_r = 0
    sum_g = 0
    sum_b = 0
    for color in colors:
        (r, g, b) = color
        sum_r += r * r
        sum_g += g * g
        sum_b += b * b
    return [sqrt(sum_r/len(colors)), sqrt(sum_g/len(colors)), sqrt(sum_b/len(colors))]

def compose_from_image(score, image, w, h):
    first_col_color = []
    for x in range(w):
        colors = []
        for y in range(h):
            colors.append(image.getpixel((x, y)))
        if not first_col_color:
            first_col_color = get_average_color(colors)
        sonify(score, colors, first_col_color)
        yield 0.05

def sonify(score, colors, first_col_color):
    # find distance between pixel color and first row
    b = array(first_col_color)
    for i,rgb in enumerate(colors):
        a = array(rgb)
        dist = norm(a - b)
        # this is kinda arbitrary, works for the julia representation
        # Pretty sure that this would be "not yellow" for julia and "not blue" for mandelbrot
        if dist > 150:
            create_note(score, dist, i)

def create_note(score, dist, pitch):
    # 400 for mandelbrot
    amp = rescale(dist, 0, 400, 0, 1, mode="cos")
    note = Note(score.now, duration=0.05, pitch=pitch, amplitude=amp)
    score.add(note)

# driver function
if __name__ == "__main__":
    
    # setting the width, height and zoom 
    # of the image to be created
    seq = Seq()
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.ElectricPiano1})
    w, h, zoom = 960, 127, 1
    hires_w, hires_h = 1920, 1080
    # Ok we're just gonna take the 127x960 and then map the color to a note
    # Basically computer vision but the problem is the extra color outside of the fractal itself
    # Maybe compare the pixel to the average color of the column
    # Would work for the first and last bit of julia but not for middle
    # Maybe average color of first column, then anything thats not close enough is turned into a note
    # Would work for mandelbrot too, full image

    # Sonifying the fractal in a visual way


    # setting up the variables according to 
    # the equation to  create the fractal
    cX, cY = -0.7, 0.27015
    moveX, moveY = 0.0, 0.0
    maxIter = 255
   
    # julia_image = julia_calculation(w, h, zoom, cX, cY, moveX, moveY, maxIter)
    # julia_image.show()
    actual_mandelbrot_image = mandelbrot_calculation(hires_w, hires_h, -2.0, 1.0, -1.5, 1.5, maxIter)
    actual_mandelbrot_image.show()
    compose_mandelbrot_image = mandelbrot_calculation(w, h, -2.0, 1.0, -1.5, 1.5, maxIter)
    compose_mandelbrot_image.show()
    score.compose([0, compose_from_image(score, compose_mandelbrot_image, w, h)])
    MidiFile("mapping.mid", [meta, seq]).write()
    seq.print()
   