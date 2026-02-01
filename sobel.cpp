#include <cstring>
#include <algorithm>

extern "C" {
    struct Img { unsigned char* d; int w, h; };

    Img* sobel(unsigned char* img, int w, int h) {
        Img* r = new Img{new unsigned char[w*h], w, h};
        memset(r->d, 0, w*h);
        
        int gx[3][3] = {{-1,0,1},{-2,0,2},{-1,0,1}};
        int gy[3][3] = {{-1,-2,-1},{0,0,0},{1,2,1}};
        
        for(int y=1; y<h-1; y++) for(int x=1; x<w-1; x++) {
            int sx=0, sy=0;
            for(int ky=-1; ky<=1; ky++) for(int kx=-1; kx<=1; kx++) {
                int pix = img[(y+ky)*w+x+kx];
                sx += pix*gx[ky+1][kx+1];
                sy += pix*gy[ky+1][kx+1];
            }
            int mag = std::min(255, (int)std::sqrt(sx*sx + sy*sy));
            r->d[y*w+x] = mag;
        }
        return r;
    }

    void free_img(Img* i) { delete[] i->d; delete i; }
    unsigned char* data(Img* i) { return i->d; }
    int width(Img* i) { return i->w; }
    int height(Img* i) { return i->h; }
}
