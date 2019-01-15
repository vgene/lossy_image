// edge code for UDP socket programming
#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include "LITP.h"

#define IP_PROTOCOL 0
#define PORT_NO 15050
#define NET_BUF_SIZE 1000
#define sendrecvflag 0

#define SERVER_IP "127.0.0.1"
unsigned char bitmapData[DATA_ARR_SIZE];
unsigned char permutedData[DATA_ARR_SIZE];
int reverseMapping[MAX_PIXEL_NUM];
DATA_PACKET dataPackets[PACKET_ARR_SIZE];
//BITMAPFILEHEADER fheader;
//BITMAPINFOHEADER iheader;
HEADER_PACKET headerPacket;
EOD_PACKET eodPacket;

// driver code
int main() {
    int sockfd, nBytes;
    struct sockaddr_in addr_con;
    int addrlen = sizeof(addr_con);
    addr_con.sin_family = AF_INET;
    addr_con.sin_port = htons(PORT_NO);
    addr_con.sin_addr.s_addr = inet_addr(SERVER_IP);
    char net_buf[NET_BUF_SIZE];
    FILE *fp;

    // socket()
    sockfd = socket(AF_INET, SOCK_DGRAM, IP_PROTOCOL);

    if (sockfd < 0)
        printf("\n[!] socket creation failed\n");

//    // bind()
//    if (bind(sockfd, (struct sockaddr *) &addr_con, sizeof(addr_con)) == 0)
//        printf("\nSocket successfully binded!\n");
//    else
//        printf("\n[!] socket binding Failed!\n");
//
//    nBytes = recvfrom(sockfd, net_buf, NET_BUF_SIZE,
//                      sendrecvflag, (struct sockaddr *) &addr_con,
//                      &addrlen);
    clock_t begin = clock();
    LoadBitmapFile("husky.bmp", &(headerPacket.fheader), &(headerPacket.iheader), bitmapData);

    int id = rand() % 100000;
    headerPacket.id = id;
    headerPacket.type = HEADER;

    permuteBMP(&(headerPacket.iheader), bitmapData, permutedData, reverseMapping);

//    int pixels_per_net_buf = (NET_BUF_SIZE - sizeof(int)) / (sizeof(int) + 3) - 1;
    int imgSize = headerPacket.iheader.biSizeImage / 3;
    int packetArrayIdx = 0;
    int data_sent = 0;


    for (int offset = 0, cnt = 0; offset < imgSize; ++cnt) {
        if (cnt % HEADER_PCT_INTERVAL == 0) {
            //printf("Sending a header packet ...\n");

            sendto(sockfd, &headerPacket, HEADER_PCT_SIZE,
                   sendrecvflag,
                   (struct sockaddr *) &addr_con, addrlen);
        } else {
            //printf("Sending a data packet ...\n");

            int len = PIXELS_PER_PACKET;
            if (imgSize - offset <= PIXELS_PER_PACKET) {
                len = imgSize - offset;
            }
            int bsize = getChunck(id, dataPackets + packetArrayIdx, permutedData, reverseMapping, offset, len);
//            printf("bsize is: %d\n", bsize);
//        memmove(packets + offset, p, sizeof(DATA_PACKET));
            sendto(sockfd, dataPackets + packetArrayIdx, bsize,
                   sendrecvflag,
                   (struct sockaddr *) &addr_con, addrlen);
            offset += len;
            ++packetArrayIdx;
            ++data_sent;
        }
    }
    eodPacket.id = id;
    eodPacket.type = EOD;
    for (int i = 0; i < NUM_OF_EODS; ++i) {
        //printf("Sending EOD packets ...\n");
        sendto(sockfd, &eodPacket, EOD_PCT_SIZE,
               sendrecvflag,
               (struct sockaddr *) &addr_con, addrlen);
    }
    printf("Sent %d data packets.", data_sent);

    nBytes = recvfrom(sockfd, net_buf, NET_BUF_SIZE,
                      sendrecvflag, (struct sockaddr *) &addr_con,
                      &addrlen);
    if (!strcmp(net_buf, SUCC_MSG)) {
        printf("Send successful !!!\n");
    } else {
        printf("Send failed ...\n");
    }

    clock_t end = clock();

    double time_spent = (double) (end - begin) / CLOCKS_PER_SEC;
    printf("UDP Time %.6lfs\n", time_spent);

    return 0;
}