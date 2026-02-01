import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import ctypes as c
import os

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

for lib in [lib_lap, lib_sob]:
    lib.data.argtypes = [c.POINTER(I)]
    lib.data.restype = c.POINTER(c.c_ubyte)
    lib.width.argtypes = [c.POINTER(I)]
    lib.width.restype = c.c_int
    lib.height.argtypes = [c.POINTER(I)]
    lib.height.restype = c.c_int
    lib.free_img.argtypes = [c.POINTER(I)]

class FilterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Edge Detection Filters")
        self.root.geometry("1200x800")
        self.original_img = None
        self.filtered_img = None
        
        self.setup_ui()
        
    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        
        tk.Button(top_frame, text="Load Image", command=self.load_image, width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        filter_frame = tk.LabelFrame(top_frame, text="Filters", padx=10, pady=10)
        filter_frame.pack(side=tk.LEFT, padx=20)
        
        self.filter_var = tk.StringVar(value="laplacian")
        tk.Radiobutton(filter_frame, text="Laplacian", variable=self.filter_var, value="laplacian").pack(anchor=tk.W)
        tk.Radiobutton(filter_frame, text="Sobel", variable=self.filter_var, value="sobel").pack(anchor=tk.W)
        tk.Label(filter_frame, text="").pack()
        
        tk.Button(top_frame, text="Run", command=self.apply_filter, width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(self.root, text="Ready. Load an image to start.", fg="blue")
        self.status_label.pack()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = tk.LabelFrame(main_frame, text="Original Image", padx=5, pady=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.left_canvas = tk.Canvas(left_frame, bg="gray", width=400, height=400)
        self.left_canvas.pack(fill=tk.BOTH, expand=True)
        
        right_frame = tk.LabelFrame(main_frame, text="Filtered Image", padx=5, pady=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.right_canvas = tk.Canvas(right_frame, bg="gray", width=400, height=400)
        self.right_canvas.pack(fill=tk.BOTH, expand=True)
        
        bottom_frame = tk.LabelFrame(self.root, text="Histogram", padx=5, pady=5)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.hist_canvas = tk.Canvas(bottom_frame, bg="white")
        self.hist_canvas.pack(fill=tk.BOTH, expand=True)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            return
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        if file_size > 4:
            messagebox.showerror("Error", "Image size exceeds 4MB limit!")
            self.status_label.config(text="Error: Image too large", fg="red")
            return
        
        try:
            self.original_img = np.array(Image.open(file_path).convert('L'), dtype=np.uint8)
            self.display_original()
            self.status_label.config(text=f"Image loaded: {os.path.basename(file_path)} ({file_size:.2f}MB)", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.status_label.config(text="Error loading image", fg="red")
    
    def display_original(self):
        img = Image.fromarray(self.original_img)
        img.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img)
        self.left_canvas.create_image(200, 200, image=photo)
        self.left_canvas.image = photo
    
    def apply_filter(self):
        if self.original_img is None:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        
        filter_type = self.filter_var.get()
        h, w = self.original_img.shape
        
        try:
            if filter_type == "laplacian":
                r = f_lap(self.original_img.ctypes.data_as(c.POINTER(c.c_ubyte)), w, h)
            else:
                r = f_sob(self.original_img.ctypes.data_as(c.POINTER(c.c_ubyte)), w, h)
            
            rh = lib_lap.height(r) if filter_type == "laplacian" else lib_sob.height(r)
            rw = lib_lap.width(r) if filter_type == "laplacian" else lib_sob.width(r)
            lib_ptr = lib_lap if filter_type == "laplacian" else lib_sob
            
            self.filtered_img = np.ctypeslib.as_array(lib_ptr.data(r), (rh, rw)).copy()
            lib_ptr.free_img(r)
            
            self.display_filtered()
            self.display_histogram()
            self.status_label.config(text=f"Filter applied: {filter_type.upper()}", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {e}")
            self.status_label.config(text="Error applying filter", fg="red")
    
    def display_filtered(self):
        img = Image.fromarray(self.filtered_img)
        img.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img)
        self.right_canvas.create_image(200, 200, image=photo)
        self.right_canvas.image = photo
    
    def display_histogram(self):
        self.hist_canvas.delete("all")
        
        fig = Figure(figsize=(10, 2.5), dpi=100)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        
        ax1.hist(self.original_img.ravel(), bins=256, color='blue', alpha=0.7, range=(0, 256))
        ax1.set_title('Original Image Histogram')
        ax1.set_xlabel('Pixel Value')
        ax1.set_ylabel('Frequency')
        
        ax2.hist(self.filtered_img.ravel(), bins=256, color='red', alpha=0.7, range=(0, 256))
        ax2.set_title('Filtered Image Histogram')
        ax2.set_xlabel('Pixel Value')
        ax2.set_ylabel('Frequency')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.hist_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == '__main__':
    root = tk.Tk()
    app = FilterGUI(root)
    root.mainloop()
