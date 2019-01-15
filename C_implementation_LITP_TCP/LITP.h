// binary BMP parsing code modified from https://stackoverflow.com/questions/14279242/read-bitmap-file-into-structure


#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

// convert MS def to gcc standard
typedef uint8_t BYTE;
typedef uint16_t WORD;
typedef uint32_t DWORD;
typedef uint64_t QWORD;
typedef int32_t LONG;

#define PIXELS_PER_PACKET 120
#define HEADER_PCT_SIZE (sizeof(HEADER_PACKET))
#define DATA_PCT_SIZE (sizeof(DATA_PACKET))
#define EOD_PCT_SIZE (sizeof(EOD_PACKET))
#define MAX_PIXEL_NUM (1024*768)
#define DATA_ARR_SIZE (MAX_PIXEL_NUM*3+10)
#define PACKET_ARR_SIZE (MAX_PIXEL_NUM/PIXELS_PER_PACKET+10)
#define HEADER_PCT_INTERVAL 30
#define NUM_OF_EODS 15

const char *SUCC_MSG = "Succeeded from server\n";
const char *FAIL_MSG = "Failed from server\n";


enum PACKET_TYPE {
    HEADER, DATA, EOD
};

#pragma pack(push, 1)

typedef struct tagBITMAPFILEHEADER {
    WORD bfType;  //specifies the file type
    DWORD bfSize;  //specifies the size in bytes of the bitmap file
    WORD bfReserved1;  //reserved; must be 0
    WORD bfReserved2;  //reserved; must be 0
    DWORD bfOffBits;  //species the offset in bytes from the bitmapfileheader to the bitmap bits
} BITMAPFILEHEADER;

#pragma pack(pop)


#pragma pack(push, 1)

typedef struct tagBITMAPINFOHEADER {
    DWORD biSize;  //specifies the number of bytes required by the struct
    LONG biWidth;  //specifies width in pixels
    LONG biHeight;  //species height in pixels
    WORD biPlanes; //specifies the number of color planes, must be 1
    WORD biBitCount; //specifies the number of bit per pixel
    DWORD biCompression;//specifies the type of compression
    DWORD biSizeImage;  //size of image in bytes
    LONG biXPelsPerMeter;  //number of pixels per meter in x axis
    LONG biYPelsPerMeter;  //number of pixels per meter in y axis
    DWORD biClrUsed;  //number of colors used by th ebitmap
    DWORD biClrImportant;  //number of colors that are important
} BITMAPINFOHEADER;

#pragma pack(pop)

#pragma pack(push, 1)   // this helps to pack the struct to 5-bytes
typedef struct tdata_packet {
    int id;
    enum PACKET_TYPE type;
    int original[PIXELS_PER_PACKET + 1];
    unsigned char data[PIXELS_PER_PACKET * 3 + 1];
} DATA_PACKET;
#pragma pack(pop)   // turn packing off

#pragma pack(push, 1)   // this helps to pack the struct to 5-bytes
typedef struct theader_packet {
    int id;
    enum PACKET_TYPE type;
    BITMAPFILEHEADER fheader;
    BITMAPINFOHEADER iheader;
} HEADER_PACKET;
#pragma pack(pop)   // turn packing off

#pragma pack(push, 1)   // this helps to pack the struct to 5-bytes
typedef struct teod_packet {
    int id;
    enum PACKET_TYPE type;
} EOD_PACKET;
#pragma pack(pop)   // turn packing off

/**
 * Load a bmp file from disk
 * @param filename file name, char string
 * @param bitmapFileHeader bitmap file header, mostly useless
 * @param bitmapInfoHeader info header, containing see above
 * @return
 */
int LoadBitmapFile(char *filename, BITMAPFILEHEADER *bitmapFileHeader, BITMAPINFOHEADER *bitmapInfoHeader,
                   unsigned char *bitmapData) {
    FILE *filePtr; //our file pointer
//	BITMAPFILEHEADER bitmapFileHeader; //our bitmap file header
    unsigned char *bitmapImage;  //store image data
    int imageIdx = 0; //image index counter

    //open filename in read binary mode
    filePtr = fopen(filename, "rb");
    if (filePtr == NULL)
        return -1;

    //read the bitmap file header
    fread(bitmapFileHeader, sizeof(BITMAPFILEHEADER), 1, filePtr);

    //verify that this is a bmp file by check bitmap id
    if (bitmapFileHeader->bfType != 0x4D42) {
        fclose(filePtr);
        return -1;
    }

    //read the bitmap info header
    fread(bitmapInfoHeader, sizeof(BITMAPINFOHEADER), 1,
          filePtr); // small edit. forgot to add the closing bracket at sizeof

    //move file point to the begging of bitmap data
    fseek(filePtr, bitmapFileHeader->bfOffBits, SEEK_SET);

    //read in the bitmap image data
    fread(bitmapData, bitmapInfoHeader->biSizeImage, 1, filePtr);

    //make sure bitmap image data was read
    if (bitmapData == NULL) {
        fclose(filePtr);
        return -1;
    }

    //close file and return bitmap image data
    fclose(filePtr);
    return 0;
}

HEADER_PACKET *createHeaderPacket(int id, BITMAPFILEHEADER fheader, BITMAPINFOHEADER iheader) {
    HEADER_PACKET *hp = malloc(sizeof(HEADER_PACKET));
    hp->id = id;
    hp->fheader = fheader;
    hp->iheader = iheader;
    return hp;
}

/**
 * Create an array of randomly permuted 1 .. size
 * @param size
 * @return a permuted array
 */
void getRandomPermutation(int size, int *r) {
//    int *r = malloc(size * sizeof(int));
    // initial range of numbers
    for (int i = 0; i < size; ++i) {
        r[i] = i + 1;
    }
    // shuffle
    for (int i = 1; i <= size; ++i) {
        int j = rand() % i;
        r[i] = r[j];
        r[j] = i;
    }
}

// randarr[i] = k means the original position for index i is k
void permuteBMP(BITMAPINFOHEADER *header, unsigned char *bitmapData, unsigned char *permuted, int *reverseMapping) {
    int len = (header->biSizeImage) / 3;
    getRandomPermutation(len, reverseMapping);
//    unsigned char *permuted = (unsigned char *) malloc(header->biSizeImage);
//    bzero(permuted, header->biSizeImage);
    for (int i = 0; i < len; i++) {
        memcpy(permuted + (i << 1) + i, bitmapData + (reverseMapping[i] << 1) + reverseMapping[i], 3);
    }
}

static inline int
getChunck(int id, DATA_PACKET *p, const unsigned char *permutedBMP, const int randarr[], int offset, int len) {
    p->id = id;
    p->type = DATA;
    memcpy(p->original, randarr + offset, len << 2);
    memcpy(p->data, permutedBMP + (offset << 1) + offset, (len << 1) + len);
    return DATA_PCT_SIZE;
}

static inline void restoreBMP(unsigned char *received, const DATA_PACKET *currentPacket) {
    int *origs = currentPacket->original;
    for (int i = 0; i < PIXELS_PER_PACKET; ++i) {
        memcpy(received + (origs[i] << 1) + origs[i], (currentPacket->data) + (i << 1) + i, 3);
    }
}


void writeBMP(const char *filename, const BITMAPFILEHEADER *fheader, const BITMAPINFOHEADER *iheader,
              const unsigned char *received) {
    FILE *write_ptr;
    write_ptr = fopen(filename, "wb");
    fwrite(fheader, sizeof(BITMAPFILEHEADER), 1, write_ptr);
    fwrite(iheader, sizeof(BITMAPINFOHEADER), 1, write_ptr);
    fwrite(received, iheader->biSizeImage, 1, write_ptr);
    fclose(write_ptr);
}


