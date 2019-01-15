// server
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <math.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include "LITP.h"

#define IP_PROTOCOL 0
#define IP_ADDRESS "127.0.0.1" // localhost
#define PORT_NO 15050
#define NET_BUF_SIZE 1000
//#define cipherKey 'S'
#define sendrecvflag 0


unsigned char received[DATA_ARR_SIZE];

BITMAPFILEHEADER fheader;
BITMAPINFOHEADER iheader;
struct timeval tod1, tod2;

// driver code
int main() {
    int sockfd, nBytes;
    struct sockaddr_in addr_con;
    int addrlen = sizeof(addr_con);
    addr_con.sin_family = AF_INET;
    addr_con.sin_port = htons(PORT_NO);
    addr_con.sin_addr.s_addr = INADDR_ANY;
    char net_buf[NET_BUF_SIZE];

    // socket()
    sockfd = socket(AF_INET, SOCK_DGRAM,
                    IP_PROTOCOL);

    if (sockfd < 0)
        printf("\nsocket not created\n");
    else
        printf("\nsocket created\n");

//    sendto(sockfd, "initing", 8,
//           sendrecvflag,
//           (struct sockaddr *) &addr_con, addrlen);

    // bind()
    if (bind(sockfd, (struct sockaddr *) &addr_con, sizeof(addr_con)) == 0)
        printf("\nSocket successfully binded!\n");
    else
        printf("\n[!] socket binding Failed!\n");

    int received_hd = 0;
    int cnt_data = 0;
    HEADER_PACKET *pheader = malloc(sizeof(HEADER_PACKET));
    int clocked = 0;
    clock_t begin;
    while (1) {
        // receive
//        printf("Receiving!!!\n");
        bzero(net_buf, sizeof(net_buf));
        nBytes = recvfrom(sockfd, net_buf, NET_BUF_SIZE,
                          sendrecvflag, (struct sockaddr *) &addr_con,
                          &addrlen);
        if (nBytes < 0) {
            printf("Error in receiving!\n");
        }
        if (!clocked) {
            begin = clock();
            clocked = 1;
        }
        if (nBytes == HEADER_PCT_SIZE) {
            if (!received_hd) {
                received_hd = 1;
//                printf("server received header packet!\n");
                memmove(pheader, net_buf, sizeof(HEADER_PACKET));
            }
        } else if (nBytes == DATA_PCT_SIZE) {
            ++cnt_data;
//            printf("server received header packet!\n");
            restoreBMP(received, (DATA_PACKET *) net_buf);
        } else if (nBytes == EOD_PCT_SIZE) {
            printf("server received EOD packet, stop waiting for more packets  ...\n");
            break;
        } else {
            printf("received an unknown packet, ignoring ...\n");
        }
    }


    printf("\n-------------------------------\n");
    printf("Recevied %d data packets.", cnt_data);
    if (received_hd) {
        double w = fabs(pheader->iheader.biWidth);
        double h = fabs(pheader->iheader.biHeight);
        if (cnt_data * PIXELS_PER_PACKET > 0.6 * w * h) {
            sendto(sockfd, SUCC_MSG, strlen(SUCC_MSG),
                   sendrecvflag,
                   (struct sockaddr *) &addr_con, addrlen);
            writeBMP("restored_udp.bmp", &(pheader->fheader), &(pheader->iheader), received);
        } else {
            sendto(sockfd, FAIL_MSG, strlen(FAIL_MSG),
                   sendrecvflag,
                   (struct sockaddr *) &addr_con, addrlen);
            printf("Lost too many data packets. Received %d pixels, but image has %d pixels\n",
                   cnt_data * PIXELS_PER_PACKET, (int) (0.6 * w * h) + 1);
        }
    } else {
        printf("Did not receive header, would not assemble image\n");
    }


    clock_t end = clock();

    double time_spent = (double) (end - begin) / CLOCKS_PER_SEC;
    printf("UDP CPU Time %.6lfs\n", time_spent);

//    gettimeofday(&tod2, NULL);
//    double delta = ((tod2.tv_sec  - tod1.tv_sec) * 1000000u +
//             tod2.tv_usec - tod1.tv_usec) / 1.e6;
//    printf("TOD Time is : %fs\n",delta);

    free(pheader);

    return 0;
}
