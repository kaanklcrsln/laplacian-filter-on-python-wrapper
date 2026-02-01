import ctypes as c, numpy as np, matplotlib.pyplot as plt, os
from PIL import Image

lib_lap = c.CDLL(os.path.join(os.path.dirname(__file__), 'liblaplacian.dylib'))
lib_sob = c.CDLL(os.path.join(os.path.dirname(__file__), 'libsobel.dylib'))

class I(c.Structure):
    _fields_ = [("d", c.POINTER(c.c_ubyte)), ("w", c.c_int), ("h", c.c_int)]

f_lap = lib_lap.filter
f_lap.argtypes = [c.POINTER(c.c_ubyte), c.c_int, c.c_int]
f_lap.restype = c.POINTER(I)

f_sob = lib_sob.sobel
f_sob.argtypes = [c.POINTER(c.c_ubyte), c.c_int, c.c_int]
f_sob.restype = c.POINTER(I)

lib_lap.data.argtypes = [c.POINTER(I)]
lib_lap.data.restype = c.POINTER(c.c_ubyte)
lib_lap.width.argtypes = [c.POINTER(I)]
lib_lap.width.restype = c.c_int
lib_lap.height.argtypes = [c.POINTER(I)]
lib_lap.height.restype = c.c_int
lib_lap.free_img.argtypes = [c.POINTER(I)]

lib_sob.data.argtypes = [c.POINTER(I)]
lib_sob.data.restype = c.POINTER(c.c_ubyte)
lib_sob.width.argtypes = [c.POINTER(I)]
lib_sob.width.restype = c.c_int
lib_sob.height.argtypes = [c.POINTER(I)]
lib_sob.height.restype = c.c_int
lib_sob.free_img.argtypes = [c.POINTER(I)]

def laplacian(p):
    img = np.array(Image.open(p).convert('L'), dtype=np.uint8)
    h, w = img.shape
    r = f_lap(img.ctypes.data_as(c.POINTER(c.c_ubyte)), w, h)
    rh = lib_lap.height(r)
    rw = lib_lap.width(r)
    d = np.ctypeslib.as_array(lib_lap.data(r), (rh, rw)).copy()
    lib_lap.free_img(r)
    return img, d

def sobel(p):
    img = np.array(Image.open(p).convert('L'), dtype=np.uint8)
    h, w = img.shape
    r = f_sob(img.ctypes.data_as(c.POINTER(c.c_ubyte)), w, h)
    rh = lib_sob.height(r)
    rw = lib_sob.width(r)
    d = np.ctypeslib.as_array(lib_sob.data(r), (rh, rw)).copy()
    lib_sob.free_img(r)
    return img, d

def show(p):
    o, lap = laplacian(p)
    _, sob = sobel(p)
    fig, ax = plt.subplots(1, 3, figsize=(18, 6))
    ax[0].imshow(o, cmap='gray')
    ax[0].set_title('Original')
    ax[1].imshow(lap, cmap='gray')
    ax[1].set_title('Laplacian')
    ax[2].imshow(sob, cmap='gray')
    ax[2].set_title('Sobel')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    show('image-ex.jpg')
