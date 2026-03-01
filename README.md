# Laplacian Filter with Python Wrapper
<img width="943" height="857" alt="Screenshot 2026-02-02 at 01 03 01" src="https://github.com/user-attachments/assets/8db3e740-368a-4723-9b8f-655fe101e6eb" />

A C++ implementation of the edge detection filter compiled as a shared library and wrapped with Python ctypes for easy integration.

## Project Structure

```
.
├── laplacian.cpp           # C source with Laplacian filter implementation
├── liblaplacian.dylib      # Compiled shared library (macOS)
├── laplacian_wrapper.py    # Python wrapper using ctypes
└── image-ex.jpg            # Example image for testing
```

## How It Works

1. **C++ Core** (`laplacian.cpp`)
   - Implements the Laplacian kernel: 3x3 convolution matrix
   - Processes grayscale image data as flat array
   - Returns filtered image with edge detection applied
   - Compiled as shared library for cross-language usage

2. **Python Wrapper** (`laplacian_wrapper.py`)
   - Loads the compiled C++ library using ctypes
   - Converts PIL images to numpy arrays
   - Calls C++ filter function with image data
   - Returns results as numpy arrays for matplotlib visualization

3. **Data Flow**
   ```
   Image File (JPG) → PIL Load → Grayscale Convert → NumPy Array
   → C++ Filter via ctypes → Filtered NumPy Array → Matplotlib Display
   ```

## Requirements

- Python 3.6+
- NumPy
- Pillow
- Matplotlib

## Usage

```python
from laplacian_wrapper import laplacian, show

# Get filtered image
original, filtered = laplacian('image-ex.jpg')

# Display side by side
show('image-ex.jpg')
```

## Compilation

```bash
g++ -shared -fPIC -o liblaplacian.dylib laplacian.cpp -std=c++11
```


