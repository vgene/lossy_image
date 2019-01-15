//
// Created by shaoweizhu on 2019-01-06.
//

#include "LITP.h"
#include <time.h>

unsigned char bitmapData[DATA_ARR_SIZE];
unsigned char permutedData[DATA_ARR_SIZE];
int reverseMapping[MAX_PIXEL_NUM];
BITMAPFILEHEADER fheader;
BITMAPINFOHEADER iheader;

int main() {

    // test reading writing mechanisms
    LoadBitmapFile("husky.bmp", &fheader, &iheader, bitmapData);


    writeBMP("read_then_write.bmp", &fheader, &iheader, bitmapData);
    permuteBMP(&iheader, bitmapData, permutedData, reverseMapping);
    writeBMP("read_then_permuted.bmp", &fheader, &iheader, permutedData);

    // test recovery
    unsigned char *received = malloc(iheader.biSizeImage);
    bzero(received, iheader.biSizeImage);
    DATA_PACKET *packets = malloc((iheader.biSizeImage / 3 + 1) * sizeof(DATA_PACKET));
    clock_t begin = clock();

    for (int offset = 0; offset < iheader.biSizeImage / 3; offset+=PIXELS_PER_PACKET) {
        getChunck(0, packets + offset, permutedData, reverseMapping, offset, PIXELS_PER_PACKET);
//        memmove(packets + offset, p, sizeof(DATA_PACKET));
        restoreBMP(received, packets + offset);
    }
    clock_t end = clock();

    double time_spent = (double) (end - begin) / CLOCKS_PER_SEC;
    printf("time spent get chunck and restoring %.3lfs\n", time_spent);

    writeBMP("restored.bmp", &fheader, &iheader, received);

}